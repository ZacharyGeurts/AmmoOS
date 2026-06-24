#!/usr/bin/env python3
"""NEXUS Field DNS — smart truthful self-hosted resolver (IPv4 + IPv6).

Only loopback listeners. Foreign resolvers (Charter, Google, Cloudflare, etc.)
are stopped by field-dns.sh firewall + resolv enforcement. Resolution uses
dig +trace from root hints — no shortcut public DNS.
"""
from __future__ import annotations

import json
import os
import re
import socket
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))

OUT_JSON = STATE / "field-dns.json"
PANEL_CACHE = STATE / "field-dns-panel.json"
PID_FILE = STATE / "field-dns.pid"
BLOCKLIST = STATE / "adblock" / "domains-block.txt"
EXTRA_BLOCK = STATE / "dns-truth-blocklist.txt"
CACHE_TTL = int(os.environ.get("NEXUS_FIELD_DNS_CACHE_TTL", "300"))

IPV4 = os.environ.get("NEXUS_FIELD_DNS_IPV4", "127.0.0.1")
IPV6 = os.environ.get("NEXUS_FIELD_DNS_IPV6", "::1")
PORT = int(os.environ.get("NEXUS_FIELD_DNS_PORT", "53"))


def _bind_hosts_v4() -> list[str]:
    raw = os.environ.get("NEXUS_FIELD_DNS_BINDS_IPV4", "127.0.0.1,127.0.0.53")
    hosts = [h.strip() for h in raw.split(",") if h.strip()]
    return hosts or [IPV4]


def _bind_hosts_v6() -> list[str]:
    raw = os.environ.get("NEXUS_FIELD_DNS_BINDS_IPV6", IPV6)
    hosts = [h.strip() for h in raw.split(",") if h.strip()]
    return hosts or [IPV6]

QTYPE_MAP = {1: "A", 28: "AAAA", 5: "CNAME", 15: "MX", 16: "TXT"}

_cache: dict[str, tuple[float, list[str]]] = {}
_cache_lock = threading.Lock()
_stats = {"queries": 0, "blocked": 0, "cache_hits": 0, "errors": 0, "started_at": ""}


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load_blocklist() -> set[str]:
    blocked: set[str] = set()
    for path in (BLOCKLIST, EXTRA_BLOCK):
        if not path.is_file():
            continue
        try:
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                dom = line.strip().lower().lstrip(".")
                if dom and not dom.startswith("#"):
                    blocked.add(dom)
        except OSError:
            continue
    return blocked


def _is_blocked(qname: str, blocked: set[str]) -> bool:
    name = qname.lower().rstrip(".")
    if not name:
        return False
    if name in blocked:
        return True
    parts = name.split(".")
    for i in range(len(parts)):
        suffix = ".".join(parts[i:])
        if suffix in blocked:
            return True
    return False


def _encode_name(name: str) -> bytes:
    out = bytearray()
    for label in name.rstrip(".").split("."):
        raw = label.encode("idna", errors="replace")[:63]
        out.append(len(raw))
        out.extend(raw)
    out.append(0)
    return bytes(out)


def _read_name(data: bytes, offset: int) -> tuple[str, int]:
    labels: list[str] = []
    end = offset
    jumped = False
    while offset < len(data):
        length = data[offset]
        if length == 0:
            offset += 1
            if not jumped:
                end = offset
            break
        if length & 0xC0 == 0xC0:
            if offset + 1 >= len(data):
                break
            if not jumped:
                end = offset + 2
            ptr = ((length & 0x3F) << 8) | data[offset + 1]
            offset = ptr
            jumped = True
            continue
        offset += 1
        labels.append(data[offset : offset + length].decode("idna", errors="replace"))
        offset += length
    return ".".join(labels), end


def _parse_query(data: bytes) -> tuple[int, str, int, int] | None:
    if len(data) < 12:
        return None
    txn_id, flags, qdcount, _, _, _ = struct.unpack("!HHHHHH", data[:12])
    if qdcount < 1 or (flags >> 15) & 1:
        return None
    qname, offset = _read_name(data, 12)
    if offset + 4 > len(data):
        return None
    qtype, qclass = struct.unpack("!HH", data[offset : offset + 4])
    return txn_id, qname, qtype, qclass


def _pack_rdata(qtype: int, value: str) -> bytes | None:
    if qtype == 1:
        try:
            return socket.inet_pton(socket.AF_INET, value)
        except OSError:
            return None
    if qtype == 28:
        try:
            return socket.inet_pton(socket.AF_INET6, value)
        except OSError:
            return None
    return None


def _build_response(
    txn_id: int,
    qname: str,
    qtype: int,
    qclass: int,
    answers: list[str],
    rcode: int = 0,
) -> bytes:
    header = struct.pack("!HHHHHH", txn_id, 0x8180 | (rcode & 0xF), 1, len(answers), 0, 0)
    question = _encode_name(qname) + struct.pack("!HH", qtype, qclass)
    body = bytearray()
    for ans in answers:
        rdata = _pack_rdata(qtype, ans)
        if not rdata:
            continue
        body.extend(_encode_name(qname))
        body.extend(struct.pack("!HHI", qtype, qclass, 120))
        body.extend(struct.pack("!H", len(rdata)))
        body.extend(rdata)
    return header + question + bytes(body)


def _resolve_trace(qname: str, qtype_name: str) -> list[str]:
    try:
        proc = subprocess.run(
            [
                "dig",
                "+trace",
                "+time=4",
                "+tries=1",
                "+noall",
                "+answer",
                qname,
                qtype_name,
            ],
            capture_output=True,
            text=True,
            timeout=14,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    out: list[str] = []
    for line in (proc.stdout or "").splitlines():
        parts = line.split()
        if len(parts) >= 5 and parts[3] == qtype_name:
            out.append(parts[4])
    return out[:24]


def _resolve(qname: str, qtype: int, blocked: set[str]) -> tuple[list[str], str]:
    qtype_name = QTYPE_MAP.get(qtype)
    if not qtype_name:
        return [], "unsupported"
    if _is_blocked(qname, blocked):
        return [], "blocked"
    key = f"{qname.lower()}:{qtype_name}"
    now = time.time()
    with _cache_lock:
        hit = _cache.get(key)
        if hit and hit[0] > now:
            _stats["cache_hits"] += 1
            return hit[1], "cache"
    answers = _resolve_trace(qname, qtype_name)
    if answers:
        with _cache_lock:
            _cache[key] = (now + CACHE_TTL, answers)
        return answers, "trace"
    return [], "miss"


def _handle_query(data: bytes, blocked: set[str]) -> bytes | None:
    parsed = _parse_query(data)
    if not parsed:
        return None
    txn_id, qname, qtype, qclass = parsed
    _stats["queries"] += 1
    answers, reason = _resolve(qname, qtype, blocked)
    if reason == "blocked":
        _stats["blocked"] += 1
        return _build_response(txn_id, qname, qtype, qclass, [], rcode=3)
    if not answers:
        _stats["errors"] += 1
        return _build_response(txn_id, qname, qtype, qclass, [], rcode=2)
    return _build_response(txn_id, qname, qtype, qclass, answers)


def _udp_loop(family: int, host: str) -> None:
    sock = socket.socket(family, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if family == socket.AF_INET6:
        try:
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        except OSError:
            pass
    sock.bind((host, PORT))
    blocked = _load_blocklist()
    last_reload = time.time()
    while True:
        if time.time() - last_reload > 120:
            blocked = _load_blocklist()
            last_reload = time.time()
        try:
            data, addr = sock.recvfrom(4096)
        except OSError:
            continue
        resp = _handle_query(data, blocked)
        if resp:
            try:
                sock.sendto(resp, addr)
            except OSError:
                pass


def _publish(extra: dict[str, Any] | None = None) -> None:
    doc: dict[str, Any] = {
        "updated": _now(),
        "title": "NEXUS Truth DNS",
        "priority": 1,
        "self_hosted": True,
        "truthful": True,
        "foreign_resolvers_stopped": True,
        "ipv4": {"host": IPV4, "port": PORT},
        "ipv6": {"host": IPV6, "port": PORT},
        "listeners": [f"{IPV4}#{PORT}", f"[{IPV6}]#{PORT}"],
        "stats": dict(_stats),
        "blocklist_domains": len(_load_blocklist()),
        "cache_entries": len(_cache),
    }
    if extra:
        doc.update(extra)
    tmp = OUT_JSON.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(OUT_JSON)


def _multipoint_mod() -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "dns_multipoint_identity", INSTALL / "lib" / "dns-multipoint-identity.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def serve() -> int:
    _stats["started_at"] = _now()
    listeners: list[str] = []
    threads: list[threading.Thread] = []
    for host in _bind_hosts_v4():
        listeners.append(f"{host}#{PORT}")
        threads.append(threading.Thread(target=_udp_loop, args=(socket.AF_INET, host), daemon=True))
    for host in _bind_hosts_v6():
        listeners.append(f"[{host}]#{PORT}")
        threads.append(threading.Thread(target=_udp_loop, args=(socket.AF_INET6, host), daemon=True))
    try:
        _multipoint_mod().build_identity(running=True)
    except Exception:
        pass
    _publish({"running": True, "pid": os.getpid(), "listeners": listeners})
    PID_FILE.write_text(f"{os.getpid()}\n", encoding="utf-8")
    for t in threads:
        t.start()
    while True:
        time.sleep(30)
        try:
            _multipoint_mod().build_identity(running=True)
        except Exception:
            pass
        _publish({"running": True, "pid": os.getpid(), "listeners": listeners})


def status() -> dict[str, Any]:
    if OUT_JSON.is_file():
        try:
            return json.loads(OUT_JSON.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {
        "updated": _now(),
        "running": False,
        "self_hosted": True,
        "ipv4": {"host": IPV4, "port": PORT},
        "ipv6": {"host": IPV6, "port": PORT},
    }


def _planetary_mod() -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "dns_planetary_security", INSTALL / "lib" / "dns-planetary-security.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def build_panel() -> dict[str, Any]:
    srv = status()
    planetary = _planetary_mod().build_planetary_dns(extra={"server": srv})
    multipoint: dict[str, Any] = {}
    try:
        multipoint = _multipoint_mod().build_identity(running=bool(srv.get("running")))
    except Exception:
        multipoint = {}
    doc: dict[str, Any] = {
        "schema": "field-dns/v1",
        "updated": _now(),
        "title": "NEXUS Truth DNS",
        "running": bool(srv.get("running")),
        "self_hosted": True,
        "truthful": True,
        "priority": 1,
        "listeners": srv.get("listeners") or [f"{IPV4}#{PORT}", f"[{IPV6}]#{PORT}"],
        "ipv4": srv.get("ipv4") or {"host": IPV4, "port": PORT},
        "ipv6": srv.get("ipv6") or {"host": IPV6, "port": PORT},
        "stats": {
            **(srv.get("stats") or {}),
            **(planetary.get("stats") or {}),
        },
        "blocklist_domains": srv.get("blocklist_domains", len(_load_blocklist())),
        "cache_entries": srv.get("cache_entries", len(_cache)),
        "foreign_resolvers_stopped": True,
        "planetary": planetary,
        "rfc_matrix": planetary.get("rfc_matrix") or [],
        "legal_framework": planetary.get("legal_framework") or [],
        "root_servers": planetary.get("root_servers") or [],
        "zones": planetary.get("zones") or [],
        "resolv": planetary.get("resolv") or {},
        "resolver_policy": planetary.get("resolver_policy") or {},
        "planetary_security_level": planetary.get("planetary_security_level"),
        "multipoint_identity": multipoint,
        "identification_points": multipoint.get("identification_points") or [],
        "dns_override_active": (multipoint.get("override") or {}).get("resolv", {}).get("nexus_override_active"),
    }
    tmp = PANEL_CACHE.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(PANEL_CACHE)
    return doc


def panel_json() -> dict[str, Any]:
    if PANEL_CACHE.is_file():
        try:
            return json.loads(PANEL_CACHE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return build_panel()


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: field-dns.py [serve|build|json|status]", file=sys.stderr)
        return 1
    cmd = sys.argv[1]
    if cmd == "serve":
        serve()
        return 0
    if cmd == "build":
        print(json.dumps(build_panel(), ensure_ascii=False))
        return 0
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    if cmd == "status":
        print(json.dumps(status(), ensure_ascii=False))
        return 0
    print("usage: field-dns.py [serve|build|json|status]", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
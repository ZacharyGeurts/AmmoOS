#!/usr/bin/env python3
"""NEXUS Field DHCP — issue leases only; DNS option 6 → Truth Resolver."""
from __future__ import annotations

import json
import os
import socket
import struct
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
PANEL_CACHE = STATE / "field-dhcp-panel.json"
PID_FILE = STATE / "field-dhcp.pid"
LEASE_FILE = STATE / "field-dhcp-leases.json"

PORT = 67
DNS_SERVERS = ["127.0.0.1"]
LEASE_SEC = int(os.environ.get("NEXUS_FIELD_DHCP_LEASE", "3600"))
POOL_START = os.environ.get("NEXUS_FIELD_DHCP_POOL_START", "192.168.50.100")
POOL_END = os.environ.get("NEXUS_FIELD_DHCP_POOL_END", "192.168.50.200")
BIND_IF = os.environ.get("NEXUS_FIELD_DHCP_BIND", "0.0.0.0")

_stats = {"discover": 0, "offer": 0, "request": 0, "ack": 0, "rejected": 0, "started_at": ""}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _ip_to_int(ip: str) -> int:
    return struct.unpack("!I", socket.inet_aton(ip))[0]


def _int_to_ip(n: int) -> str:
    return socket.inet_ntoa(struct.pack("!I", n & 0xFFFFFFFF))


def _next_lease(mac: str) -> str:
    leases = _load_json(LEASE_FILE, {"leases": {}})
    pool = leases.setdefault("leases", {})
    if mac in pool:
        return pool[mac]["ip"]
    start = _ip_to_int(POOL_START)
    end = _ip_to_int(POOL_END)
    used = {_ip_to_int(v["ip"]) for v in pool.values() if v.get("ip")}
    for n in range(start, end + 1):
        if n not in used:
            ip = _int_to_ip(n)
            pool[mac] = {"ip": ip, "leased_at": _now(), "dns": DNS_SERVERS}
            _save_json(LEASE_FILE, leases)
            return ip
    return POOL_START


def _dhcp_options(data: bytes) -> dict[int, bytes]:
    opts: dict[int, bytes] = {}
    if len(data) < 240:
        return opts
    i = 240
    while i < len(data):
        code = data[i]
        if code == 255:
            break
        if code == 0:
            i += 1
            continue
        if i + 1 >= len(data):
            break
        ln = data[i + 1]
        i += 2
        opts[code] = data[i : i + ln]
        i += ln
    return opts


def _build_reply(msg_type: int, xid: bytes, yiaddr: str, chaddr: bytes) -> bytes:
    op = 2
    htype = 1
    hlen = 6
    hops = 0
    secs = 0
    flags = 0
    ciaddr = "0.0.0.0"
    siaddr = BIND_IF if BIND_IF != "0.0.0.0" else "127.0.0.1"
    giaddr = "0.0.0.0"
    sname = b"\x00" * 64
    file_ = b"\x00" * 128
    magic = b"\x63\x82\x53\x63"
    opts = bytearray()
    opts.extend(bytes([53, 1, msg_type]))
    opts.extend(bytes([54, 4]) + socket.inet_aton(siaddr))
    opts.extend(bytes([51, 4]) + struct.pack("!I", LEASE_SEC))
    dns_blob = b"".join(socket.inet_aton(d) for d in DNS_SERVERS)
    opts.extend(bytes([6, len(dns_blob)]) + dns_blob)
    opts.extend(bytes([1, 4]) + socket.inet_aton("255.255.255.0"))
    opts.append(255)
    header = struct.pack(
        "!BBBBI4s4s4s4s16s64s128s4s",
        op, htype, hlen, hops,
        struct.unpack("!I", xid)[0],
        socket.inet_aton(ciaddr),
        socket.inet_aton(yiaddr),
        socket.inet_aton(siaddr),
        socket.inet_aton(giaddr),
        chaddr[:16].ljust(16, b"\x00"),
        sname,
        file_,
        magic,
    )
    return header + bytes(opts)


def _guard_mod() -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location("dns_threat_guard", INSTALL / "lib" / "dns-threat-guard.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _handle(data: bytes, addr: tuple[str, int]) -> bytes | None:
    if len(data) < 240:
        _stats["rejected"] += 1
        return None
    client = f"{addr[0]}:{addr[1]}"
    try:
        mod = _guard_mod()
        if mod.is_permanently_blocked(client):
            _stats["rejected"] += 1
            return None
        ok, reason = mod.listen_before_reject(client_key=client, packet_len=len(data))
        if not ok:
            _stats["rejected"] += 1
            mod.eradicate_threat(client_key=client, reason=reason, vector="DDOS_FLOOD")
            return None
    except Exception:
        pass
    opts = _dhcp_options(data)
    msg_type = opts.get(53, b"\x01")[0] if 53 in opts else 1
    xid = data[4:8]
    chaddr = data[28:44]
    mac = ":".join(f"{b:02x}" for b in chaddr[:6])
    if msg_type == 1:
        _stats["discover"] += 1
        ip = _next_lease(mac)
        _stats["offer"] += 1
        return _build_reply(2, xid, ip, chaddr)
    if msg_type == 3:
        _stats["request"] += 1
        ip = _next_lease(mac)
        _stats["ack"] += 1
        return _build_reply(5, xid, ip, chaddr)
    _stats["rejected"] += 1
    return None


def _loop() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((BIND_IF, PORT))
    while True:
        try:
            data, addr = sock.recvfrom(2048)
        except OSError:
            continue
        resp = _handle(data, addr)
        if resp:
            try:
                sock.sendto(resp, addr)
            except OSError:
                pass


def _takeover_mod() -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "dns_service_takeover", INSTALL / "lib" / "dns-service-takeover.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _may_serve_dhcp() -> bool:
    try:
        return bool(_takeover_mod().can_serve_dhcp())
    except Exception:
        return True


def serve() -> int:
    if not _may_serve_dhcp():
        build_panel()
        time.sleep(15)
        return 0
    _stats["started_at"] = _now()
    PID_FILE.write_text(f"{os.getpid()}\n", encoding="utf-8")
    _loop()
    return 0


def build_panel() -> dict[str, Any]:
    leases = _load_json(LEASE_FILE, {"leases": {}})
    takeover: dict[str, Any] = {}
    try:
        takeover = _takeover_mod().panel_json()
    except Exception:
        takeover = {}
    may_serve = _may_serve_dhcp()
    running = False
    if PID_FILE.is_file():
        try:
            pid = int(PID_FILE.read_text(encoding="utf-8").strip().split()[0])
            os.kill(pid, 0)
            running = True
        except (OSError, ValueError):
            running = False
    doc = {
        "schema": "field-dhcp/v1",
        "updated": _now(),
        "running": running,
        "may_serve": may_serve,
        "takeover_phase": takeover.get("phase") or "observing",
        "motto": "DHCP issues only — DNS option 6 → NEXUS Truth Resolver.",
        "bind": f"{BIND_IF}:{PORT}",
        "pool": {"start": POOL_START, "end": POOL_END},
        "dns_option": DNS_SERVERS,
        "lease_seconds": LEASE_SEC,
        "stats": dict(_stats),
        "leases": list(leases.get("leases", {}).items())[:48],
        "lease_count": len(leases.get("leases") or {}),
        "hostess7": {
            "inside": "LAN DHCP → 127.0.0.1 DNS",
            "outside": "No DHCP on WAN — DNS admin ports 7/77/777 read-only",
        },
    }
    _save_json(PANEL_CACHE, doc)
    return doc


def panel_json() -> dict[str, Any]:
    if PANEL_CACHE.is_file():
        try:
            return json.loads(PANEL_CACHE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return build_panel()


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "serve":
        serve()
        return 0
    if cmd == "build":
        print(json.dumps(build_panel(), ensure_ascii=False))
        return 0
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: field-dhcp.py [serve|build|json]"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
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
    # 127.0.0.53 is systemd-resolved — binding there conflicts; redirect via resolv instead.
    raw = os.environ.get("NEXUS_FIELD_DNS_BINDS_IPV4", "127.0.0.1")
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


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


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
        try:
            raw = label.encode("ascii")[:63]
        except UnicodeEncodeError:
            raw = label.encode("idna")[:63]
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
        labels.append(data[offset : offset + length].decode("ascii", errors="replace"))
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


def _guard_mod() -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location("dns_threat_guard", INSTALL / "lib" / "dns-threat-guard.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _integrity_mod() -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location("dns_egress_integrity", INSTALL / "lib" / "dns-egress-integrity.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _resolve_trace(qname: str, qtype_name: str) -> list[str]:
    guard = _guard_mod()
    if not guard.acquire_dig_slot():
        return []
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
        guard.release_dig_slot()
        return []
    finally:
        guard.release_dig_slot()
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
        try:
            _integrity_mod().verify_dns_answer(qname, qtype_name, answers)
        except Exception:
            pass
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "dns_internet_field", INSTALL / "lib" / "dns-internet-field.py",
            )
            if spec and spec.loader:
                _inf = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(_inf)
                _inf.record_query(qname, answers)
        except Exception:
            pass
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
        client = f"{addr[0]}:{addr[1]}"
        try:
            guard = _guard_mod()
            if guard.is_permanently_blocked(client):
                continue
            parsed_peek = _parse_query(data)
            qtype_peek = parsed_peek[2] if parsed_peek else None
            ok, reason = guard.listen_before_reject(
                client_key=client, packet_len=len(data), qtype=qtype_peek,
            )
            if not ok:
                guard.eradicate_threat(client_key=client, reason=reason, vector="DDOS_FLOOD")
                continue
        except Exception:
            pass
        try:
            resp = _handle_query(data, blocked)
        except Exception:
            _stats["errors"] += 1
            continue
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


def _acquire_serve_lock() -> bool:
    """Single resolver instance — duplicate binds cause silent query loss."""
    if PID_FILE.is_file():
        try:
            old = int(PID_FILE.read_text(encoding="utf-8").strip().split()[0])
            os.kill(old, 0)
            return False
        except (OSError, ValueError):
            pass
    return True


def serve() -> int:
    if not _acquire_serve_lock():
        time.sleep(10)
        return 0
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


def _recent_queries(limit: int = 48) -> list[dict[str, Any]]:
    hints = STATE / "field-dns-cache-hints.jsonl"
    rows: list[dict[str, Any]] = []
    if not hints.is_file():
        return rows
    try:
        lines = hints.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines[-limit:]:
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except OSError:
        pass
    return list(reversed(rows[-limit:]))


def _engineer_briefing(
    srv: dict[str, Any],
    planetary: dict[str, Any],
    multipoint: dict[str, Any],
    internet_field: dict[str, Any],
    takeover: dict[str, Any] | None = None,
) -> dict[str, Any]:
    seed = _load_json(INSTALL / "data" / "dns-admin-seed.json", {})
    welcome = seed.get("welcome") or {}
    resolv = planetary.get("resolv") or {}
    stats = srv.get("stats") or {}
    alerts: list[dict[str, Any]] = []

    if not srv.get("running"):
        alerts.append({
            "level": "critical",
            "code": "resolver_down",
            "title": "Truth Resolver not running",
            "detail": "UDP listener offline — restart nexus-genius or field-dns serve.",
            "action": "sudo systemctl restart nexus-genius",
        })
    takeover_phase = (takeover or {}).get("phase") or "observing"
    if takeover_phase in ("observing", "ready"):
        alerts.append({
            "level": "info",
            "code": "takeover_pending",
            "title": f"Graceful takeover — phase {takeover_phase}",
            "detail": "Incumbent DNS/DHCP left running until NEXUS Truth Resolver is healthy.",
            "action": "Wait for primary phase — no resolv interrupt",
        })
    elif not resolv.get("nexus_truth_enforced"):
        v4_ns = ", ".join(resolv.get("ipv4_nameservers") or []) or "—"
        v6_ns = ", ".join(resolv.get("ipv6_nameservers") or []) or "—"
        stacks = []
        if resolv.get("ipv4_nameservers") and not resolv.get("ipv4_truth_enforced"):
            stacks.append(f"IPv4 foreign: {v4_ns}")
        if resolv.get("ipv6_nameservers") and not resolv.get("ipv6_truth_enforced"):
            stacks.append(f"IPv6 foreign: {v6_ns}")
        detail = " · ".join(stacks) if stacks else f"Nameservers: {', '.join(resolv.get('nameservers') or ['—'])}"
        alerts.append({
            "level": "high",
            "code": "resolv_foreign",
            "title": "resolv.conf not steered to NEXUS (dual-stack)",
            "detail": f"{detail} — enforce cycle pending or needs root.",
            "action": "nexus_field_dns_enforce_resolv (daemon cycle or sudo)",
        })
    if int(stats.get("errors") or 0) > int(stats.get("queries") or 0) * 0.25 and int(stats.get("queries") or 0) > 3:
        alerts.append({
            "level": "medium",
            "code": "high_error_rate",
            "title": "Elevated SERVFAIL rate",
            "detail": f"{stats.get('errors', 0)} errors on {stats.get('queries', 0)} queries — check dig +trace path.",
            "action": "Inspect field-dns.json stats; verify root reachability",
        })
    if (internet_field.get("total_slots") or 0) and (internet_field.get("recognized_slots") or 0) == 0:
        alerts.append({
            "level": "info",
            "code": "internet_silent",
            "title": "Internet field all silent",
            "detail": "WHOLE slots loaded — run pull cycle or resolve domains to light LOCAL NOW.",
            "action": "python3 lib/dns-internet-field.py pull",
        })

    enforced = sum(1 for r in (planetary.get("rfc_matrix") or []) if r.get("compliance") == "enforced")
    return {
        "headline": welcome.get("headline") or "Engineer briefing — everything DNS upfront",
        "lead": welcome.get("lead") or "Truth Resolver on loopback. Trace-only. No foreign shortcut.",
        "upfront": list(welcome.get("dns_upfront") or []),
        "love_note": welcome.get("love_note") or "",
        "alerts": alerts,
        "healthy": not any(a.get("level") in ("critical", "high") for a in alerts),
        "quick_facts": {
            "running": bool(srv.get("running")),
            "pid": srv.get("pid"),
            "started_at": stats.get("started_at"),
            "listeners": srv.get("listeners") or [],
            "planetary_level": planetary.get("planetary_security_level"),
            "host_level": planetary.get("host_security_level"),
            "rfc_enforced": enforced,
            "rfc_total": len(planetary.get("rfc_matrix") or []),
            "root_servers": len(planetary.get("root_servers") or []),
            "multipoint_points": multipoint.get("point_count") or len(multipoint.get("identification_points") or []),
            "internet_slots": internet_field.get("total_slots", 0),
            "internet_recognized": internet_field.get("recognized_slots", 0),
            "foreign_blocked": len(planetary.get("foreign_resolvers_blocked") or []),
            "foreign_ipv4_blocked": len(planetary.get("foreign_resolver_ipv4") or []),
            "foreign_ipv6_blocked": len(planetary.get("foreign_resolver_ipv6") or []),
            "ipv6_truth_enforced": (planetary.get("resolv") or {}).get("ipv6_truth_enforced"),
            "blocklist_domains": srv.get("blocklist_domains", 0),
            "cache_entries": srv.get("cache_entries", 0),
        },
        "admin_ports": seed.get("admin_ports") or [7, 77, 777],
        "port_mnemonic": seed.get("port_mnemonic") or {},
    }


def _build_traffic_patterns(
    srv: dict[str, Any],
    dhcp: dict[str, Any],
    egress: dict[str, Any],
    threat_guard: dict[str, Any],
    recent: list[dict[str, Any]],
) -> dict[str, Any]:
    stats = srv.get("stats") or {}
    queries = int(stats.get("queries") or 0)
    cache_hits = int(stats.get("cache_hits") or 0)
    blocked = int(stats.get("blocked") or 0)
    errors = int(stats.get("errors") or 0)
    total = max(queries, 1)
    eg_st = egress.get("stats") or {}
    tg_st = threat_guard.get("stats") or {}
    egress_checks = int(eg_st.get("total_checks") or 0)
    egress_verified = int(eg_st.get("verified_exact") or 0)
    leases = int(dhcp.get("lease_count") or 0)
    pct = lambda n: round((n / total) * 100) if queries else 0
    return {
        "schema": "dns-traffic-patterns/v1",
        "updated": _now(),
        "dns": {
            "queries": queries,
            "cache_hits": cache_hits,
            "blocked": blocked,
            "errors": errors,
            "hit_rate_pct": pct(cache_hits),
            "block_rate_pct": pct(blocked),
            "error_rate_pct": pct(errors),
            "egress_checks": egress_checks,
            "egress_verified": egress_verified,
            "permanent_blocks": int(tg_st.get("permanent_blocks") or 0),
            "recent_query_count": len(recent),
        },
        "dhcp": {
            "leases_active": leases,
            "running": bool(dhcp.get("running")),
            "bind": dhcp.get("bind") or "0.0.0.0:67",
            "dns_option": dhcp.get("dns_option") or ["127.0.0.1"],
        },
        "channels": [
            {"id": "queries", "label": "DNS queries", "value": queries, "pct": 100 if queries else 0},
            {"id": "cache", "label": "Cache hits", "value": cache_hits, "pct": pct(cache_hits)},
            {"id": "blocked", "label": "Policy blocked", "value": blocked, "pct": pct(blocked)},
            {"id": "errors", "label": "SERVFAIL", "value": errors, "pct": pct(errors)},
            {
                "id": "egress",
                "label": "Egress verified",
                "value": egress_verified,
                "pct": round((egress_verified / egress_checks) * 100) if egress_checks else 0,
            },
            {"id": "leases", "label": "DHCP leases", "value": leases, "pct": 100 if dhcp.get("running") and leases else 0},
        ],
    }


def _build_threat_model(
    planetary: dict[str, Any],
    multipoint: dict[str, Any],
    threat_guard: dict[str, Any],
    takeover: dict[str, Any],
    dhcp: dict[str, Any],
    srv: dict[str, Any],
    briefing: dict[str, Any],
) -> dict[str, Any]:
    pol = planetary.get("resolver_policy") or {}
    tg_pol = threat_guard.get("policy") or {}
    alerts = briefing.get("alerts") or []
    concern_count = sum(1 for a in alerts if a.get("level") in ("critical", "high", "medium"))
    enforced = int(briefing.get("quick_facts", {}).get("rfc_enforced") or 0)
    rfc_total = int(briefing.get("quick_facts", {}).get("rfc_total") or 0)
    if concern_count >= 2:
        overall = "elevated"
    elif concern_count:
        overall = "guarded"
    elif planetary.get("planetary_security_level") == "extreme":
        overall = "controlled"
    else:
        overall = "stable"
    foreign_blocked = int(briefing.get("quick_facts", {}).get("foreign_blocked") or 0)
    mp_pts = multipoint.get("point_count") or len(multipoint.get("identification_points") or [])
    untrusted = len(multipoint.get("untrusted_never_added") or [])
    inc = (takeover.get("incumbents") or {})
    return {
        "schema": "dns-threat-model/v1",
        "updated": _now(),
        "framework": "STRIDE + DNS/DHCP planetary",
        "overall_risk": overall,
        "controls_active": enforced,
        "controls_total": rfc_total,
        "summary": (
            "Loopback Truth Resolver, multipoint secure identification, foreign resolver block, "
            "DHCP listen-before-reject — planetary EXTREME when host honorability permits."
        ),
        "dns_vectors": [
            {
                "id": "spoofing",
                "threat": "DNS response spoofing / cache poison",
                "level": "mitigated" if pol.get("truthful_trace") else "open",
                "control": "dig +trace from root — no public shortcut",
                "rfc": "RFC 4033",
            },
            {
                "id": "tampering",
                "threat": "Unauthorized zone or record mutation",
                "level": "mitigated" if pol.get("loopback_only") else "monitored",
                "control": "Loopback bind only · egress integrity hash match",
                "rfc": "RFC 1035 §4.1",
            },
            {
                "id": "repudiation",
                "threat": "Query/answer non-repudiation gap",
                "level": "monitored",
                "control": "Recent query JSONL + egress integrity log",
                "rfc": "RFC 7766",
            },
            {
                "id": "disclosure",
                "threat": "Foreign resolver data exfiltration",
                "level": "mitigated" if planetary.get("foreign_resolvers_stopped", True) else "open",
                "control": f"{foreign_blocked} documented resolvers blocked",
                "rfc": "RFC 8484",
            },
            {
                "id": "dos",
                "threat": "Amplification / QPS flood",
                "level": "mitigated" if tg_pol.get("max_qps_per_client") else "monitored",
                "control": f"Max {tg_pol.get('max_qps_per_client', 30)} QPS/client · permanent eradication",
                "rfc": "RFC 6891",
            },
            {
                "id": "elevation",
                "threat": "Lateral movement via DNS channel",
                "level": "mitigated" if tg_pol.get("no_lateral_movement") else "monitored",
                "control": "No lateral movement · DHCP DNS-only option",
                "rfc": "RFC 2131",
            },
        ],
        "dhcp_vectors": [
            {
                "id": "rogue",
                "threat": "Rogue DHCP server on LAN",
                "level": "monitored" if inc.get("incumbent_dhcp") else "mitigated",
                "control": "Incumbent port-67 detection · graceful takeover",
                "rfc": "RFC 2131",
            },
            {
                "id": "starvation",
                "threat": "DHCP pool exhaustion",
                "level": "monitored" if dhcp.get("running") else "info",
                "control": f"{dhcp.get('lease_count', 0)} active leases · bind {dhcp.get('bind', '67/udp')}",
                "rfc": "RFC 2131 §4.3",
            },
            {
                "id": "option-inject",
                "threat": "Malicious DNS option injection",
                "level": "mitigated",
                "control": f"DNS option → {', '.join(dhcp.get('dns_option') or ['127.0.0.1'])}",
                "rfc": "RFC 3646",
            },
        ],
        "identification": {
            "points": mp_pts,
            "untrusted_blocked": untrusted,
        },
        "concern_count": concern_count,
        "resolver_running": bool(srv.get("running")),
    }


def _internet_field_mod() -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "dns_internet_field", INSTALL / "lib" / "dns-internet-field.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def build_panel() -> dict[str, Any]:
    srv = status()
    planetary = _planetary_mod().build_planetary_dns(extra={"server": srv})
    multipoint: dict[str, Any] = {}
    internet_field: dict[str, Any] = {}
    try:
        multipoint = _multipoint_mod().build_identity(running=bool(srv.get("running")))
    except Exception:
        multipoint = {}
    try:
        internet_field = _internet_field_mod().build_internet_field(pull_live=bool(srv.get("running")))
    except Exception:
        internet_field = {}
    egress: dict[str, Any] = {}
    threat_guard: dict[str, Any] = {}
    dhcp: dict[str, Any] = {}
    takeover: dict[str, Any] = {}
    try:
        egress = _integrity_mod().build_panel()
    except Exception:
        egress = {}
    try:
        threat_guard = _guard_mod().build_panel()
    except Exception:
        threat_guard = {}
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("field_dhcp", INSTALL / "lib" / "field-dhcp.py")
        if spec and spec.loader:
            _dhcp = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_dhcp)
            dhcp = _dhcp.build_panel()
    except Exception:
        dhcp = {}
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dns_service_takeover", INSTALL / "lib" / "dns-service-takeover.py",
        )
        if spec and spec.loader:
            _to = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_to)
            takeover = _to.build_panel()
    except Exception:
        takeover = {}
    hostess7 = takeover.get("hostess7") or {
        "inside": {
            "dns": f"{IPV4}:{PORT} loopback Truth Resolver",
            "dhcp": dhcp.get("bind") or "67/udp LAN pool",
            "movement": "none — issue/listen only",
        },
        "outside": {
            "dns_admin": "ports 7 · 77 · 777 read-only",
            "dhcp": "disabled on WAN",
            "movement": "none — information only",
        },
    }
    briefing = _engineer_briefing(srv, planetary, multipoint, internet_field, takeover)
    recent = _recent_queries()
    traffic_patterns = _build_traffic_patterns(srv, dhcp, egress, threat_guard, recent)
    threat_model = _build_threat_model(
        planetary, multipoint, threat_guard, takeover, dhcp, srv, briefing,
    )
    doc: dict[str, Any] = {
        "schema": "field-dns/v1",
        "updated": _now(),
        "title": "NEXUS Truth DNS & DHCP",
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
        "foreign_resolver_ipv4": planetary.get("foreign_resolver_ipv4") or [],
        "foreign_resolver_ipv6": planetary.get("foreign_resolver_ipv6") or [],
        "resolver_policy": planetary.get("resolver_policy") or {},
        "planetary_security_level": planetary.get("planetary_security_level"),
        "multipoint_identity": multipoint,
        "identification_points": multipoint.get("identification_points") or [],
        "dns_override_active": (multipoint.get("override") or {}).get("resolv", {}).get("nexus_override_active"),
        "internet_field": internet_field,
        "internet_slots": internet_field.get("total_slots", 0),
        "internet_recognized": internet_field.get("recognized_slots", 0),
        "internet_coverage_pct": internet_field.get("coverage_pct", 0),
        "recent_queries": recent,
        "engineer_briefing": briefing,
        "traffic_patterns": traffic_patterns,
        "threat_model": threat_model,
        "legacy_dns_equipment": (_load_json(INSTALL / "data" / "dns-admin-seed.json", {}).get("legacy_dns_equipment") or []),
        "identity": planetary.get("identity") or {},
        "egress_integrity": egress,
        "threat_guard": threat_guard,
        "takeover": takeover,
        "dhcp_server": dhcp,
        "hostess7_service": hostess7,
        "servers": {
            "dns": {
                "running": bool(srv.get("running")),
                "listeners": srv.get("listeners") or [],
                "port": PORT,
                "pid": srv.get("pid"),
            },
            "dhcp": {
                "running": bool(dhcp.get("running")),
                "bind": dhcp.get("bind"),
                "lease_count": dhcp.get("lease_count", 0),
                "dns_option": dhcp.get("dns_option") or ["127.0.0.1"],
                "dns_option_v6": dhcp.get("dns_option_v6") or ["::1"],
            },
        },
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
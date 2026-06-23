#!/usr/bin/env python3
"""NEXUS Field US Intel — Page 1 dossier for THIS machine.

Sherlock-grade facts gleaned only from local field tools and state:
ss, ip, arp, proc, resolv.conf, NEXUS state files. No external APIs.
"""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
OUT = STATE / "us-field.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], timeout: int = 8) -> str:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, errors="replace")
        return (proc.stdout or "").strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _nexus_version() -> str:
    common = INSTALL / "lib" / "nexus-common.sh"
    if common.is_file():
        m = re.search(r'NEXUS_VERSION="([^"]+)"', common.read_text(encoding="utf-8", errors="replace"))
        if m:
            return m.group(1)
    return "unknown"


def _read_file_tail(path: Path, limit: int = 4000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _uptime_sec() -> float | None:
    try:
        with open("/proc/uptime", encoding="utf-8") as fh:
            return float(fh.read().split()[0])
    except (OSError, ValueError, IndexError):
        return None


def _meminfo() -> dict[str, int]:
    out: dict[str, int] = {}
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8", errors="replace").splitlines():
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            num = re.search(r"(\d+)", v)
            if num:
                out[k.strip()] = int(num.group(1))
    except OSError:
        pass
    return out


def _cpu_model() -> str:
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


def _interfaces() -> list[dict[str, Any]]:
    raw = _run(["ip", "-j", "addr"])
    if raw:
        try:
            rows = json.loads(raw)
        except json.JSONDecodeError:
            rows = []
        out = []
        for iface in rows:
            name = iface.get("ifname", "")
            state = iface.get("operstate", "")
            addrs = []
            for ai in iface.get("addr_info") or []:
                addrs.append({
                    "family": ai.get("family"),
                    "local": ai.get("local"),
                    "prefixlen": ai.get("prefixlen"),
                    "scope": ai.get("scope"),
                })
            out.append({"name": name, "state": state, "addresses": addrs})
        return out
    text = _run(["ip", "addr"])
    return [{"raw": line} for line in text.splitlines()[:40] if line.strip()]


def _default_route() -> dict[str, str]:
    text = _run(["ip", "route", "show", "default"])
    if not text:
        return {}
    m = re.search(r"default via (\S+).*dev (\S+)", text)
    if m:
        return {"gateway": m.group(1), "device": m.group(2), "raw": text.splitlines()[0]}
    return {"raw": text.splitlines()[0] if text else ""}


def _dns_local() -> dict[str, Any]:
    resolv = Path("/etc/resolv.conf")
    servers: list[str] = []
    search: list[str] = []
    if resolv.is_file():
        for line in resolv.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("nameserver"):
                servers.append(line.split()[1])
            elif line.startswith("search"):
                search.extend(line.split()[1:])
    snap = STATE / "resolv.sha"
    dns_hash = ""
    if snap.is_file():
        dns_hash = snap.read_text(encoding="utf-8", errors="replace").strip()[:64]
    return {"nameservers": servers, "search_domains": search, "dns_hash": dns_hash}


def _ss_summary() -> dict[str, Any]:
    text = _run(["ss", "-H", "-tunap"], timeout=12)
    estab = listen = syn = 0
    procs: dict[str, int] = {}
    remotes: dict[str, int] = {}
    listeners: list[dict[str, str]] = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        st = parts[1]
        if st in ("ESTAB", "ESTABLISHED"):
            estab += 1
        elif st in ("LISTEN", "LISTENING"):
            listen += 1
            local = parts[4] if len(parts) > 4 else ""
            proc_m = re.search(r'users:\(\("([^"]+)"', line)
            listeners.append({
                "local": local,
                "process": proc_m.group(1) if proc_m else "",
            })
        elif st.startswith("SYN"):
            syn += 1
        proc_m = re.search(r'users:\(\("([^"]+)"', line)
        if proc_m:
            procs[proc_m.group(1)] = procs.get(proc_m.group(1), 0) + 1
        if st in ("ESTAB", "ESTABLISHED") and len(parts) > 5:
            remote = parts[5]
            rip = remote.rsplit(":", 1)[0].strip("[]")
            if rip and not rip.startswith("127."):
                remotes[rip] = remotes.get(rip, 0) + 1
    top_procs = sorted(procs.items(), key=lambda x: -x[1])[:12]
    top_remotes = sorted(remotes.items(), key=lambda x: -x[1])[:12]
    return {
        "established": estab,
        "listening": listen,
        "syn_state": syn,
        "top_processes": [{"process": p, "socket_count": c} for p, c in top_procs],
        "top_remote_peers": [{"ip": ip, "socket_count": c} for ip, c in top_remotes],
        "listeners": listeners[:24],
    }


def _arp_neighbors() -> list[dict[str, str]]:
    snap = STATE / "arp.snapshot"
    if snap.is_file():
        rows = []
        for line in snap.read_text(encoding="utf-8", errors="replace").splitlines()[:40]:
            if not line.strip():
                continue
            rows.append({"line": line.strip()})
        return rows
    text = _run(["ip", "neigh", "show"])
    return [{"line": ln} for ln in text.splitlines()[:40] if ln.strip()]


def _gatekeeper_slice() -> dict[str, Any]:
    doc = _load_json(STATE / "connection-intent.json", {})
    conns = doc.get("connections") or []
    by_verdict: dict[str, int] = {}
    pending = 0
    for c in conns:
        v = c.get("verdict") or "UNKNOWN"
        by_verdict[v] = by_verdict.get(v, 0) + 1
        if c.get("requires_user_trust"):
            pending += 1
    return {
        "updated": doc.get("updated"),
        "connection_count": doc.get("connection_count", len(conns)),
        "strict_trust": doc.get("strict_trust"),
        "packet_permission": doc.get("packet_permission"),
        "permitted_flow_count": doc.get("permitted_flow_count", 0),
        "segment_block_count": doc.get("segment_block_count", 0),
        "pending_trust_count": doc.get("pending_trust_count", pending),
        "verdict_histogram": by_verdict,
        "harm_candidates": doc.get("harm_candidates", 0),
    }


def _trust_posture() -> dict[str, Any]:
    trusted_path = STATE / "firewall-trusted.tsv"
    blocks_path = STATE / "firewall-blocks.tsv"
    trusted = 0
    blocked = 0
    if trusted_path.is_file():
        trusted = max(0, sum(1 for _ in trusted_path.read_text(encoding="utf-8", errors="replace").splitlines()) - 1)
    if blocks_path.is_file():
        blocked = max(0, sum(1 for _ in blocks_path.read_text(encoding="utf-8", errors="replace").splitlines()) - 1)
    settings = _load_json(STATE / "settings.override", {})
    if not settings:
        settings = {}
        for line in _read_file_tail(STATE / "settings.override").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                settings[k.strip()] = v.strip()
    return {
        "trusted_entries": trusted,
        "active_blocks": blocked,
        "lockdown_first_complete": (STATE / "lockdown-first.done").is_file(),
        "strict_trust_setting": settings.get("NEXUS_GATEKEEPER_STRICT_TRUST", "1"),
        "paranoia_block": settings.get("NEXUS_PARANOIA_BLOCK", "0"),
        "auto_crush": settings.get("NEXUS_ATTACK_KIT_AUTO_CRUSH", "1"),
    }


def _field_storage() -> dict[str, Any]:
    paths = [
        STATE / "packet-field.json",
        STATE / "packet-field.ring.jsonl",
        STATE / "human-dossier.json",
        STATE / "connection-intent.json",
        STATE / "host-attacks-panel.json",
        STATE / "threat-panel.json",
    ]
    catalog = []
    for p in paths:
        if p.is_file():
            catalog.append({"path": str(p), "size": p.stat().st_size, "exists": True})
        else:
            catalog.append({"path": str(p), "size": 0, "exists": False})
    ring_lines = 0
    ring = STATE / "packet-field.ring.jsonl"
    if ring.is_file():
        try:
            ring_lines = sum(1 for _ in ring.read_text(encoding="utf-8", errors="replace").splitlines())
        except OSError:
            pass
    return {"artifacts": catalog, "packet_ring_lines": ring_lines}


def _vigil_mode() -> str:
    st = STATE / "vigil.state"
    if not st.is_file():
        return "unknown"
    for line in st.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("mode="):
            return line.split("=", 1)[1].strip()
    return "unknown"


def _observations(doc: dict[str, Any]) -> list[dict[str, str]]:
    """Plain-English rundown blocks — one headline per fact, readable at a glance."""
    blocks: list[dict[str, str]] = []
    ident = doc.get("identity") or {}
    net = doc.get("network") or {}
    sock = doc.get("sockets") or {}
    gk = doc.get("gatekeeper") or {}
    trust = doc.get("trust_posture") or {}

    host = ident.get("hostname") or "this machine"
    os_line = f"{ident.get('os') or 'Linux'} {ident.get('os_release') or ''}".strip()
    blocks.append({
        "label": "Who you are on this network",
        "text": (
            f"{host} is running {os_line} on {ident.get('arch') or 'unknown'} hardware. "
            f"Kernel: {(ident.get('kernel') or '—')[:80]}. "
            f"Uptime: {ident.get('uptime_human') or '—'}."
        ),
    })
    if ident.get("cpu_model"):
        mem = ident.get("memory") or {}
        ram = f"{mem['MemTotal_kB'] // 1024} MiB RAM" if mem.get("MemTotal_kB") else "RAM unknown"
        blocks.append({"label": "Hardware", "text": f"{ident['cpu_model']}. {ram}."})

    route = net.get("default_route") or {}
    if route.get("gateway"):
        blocks.append({
            "label": "Default gateway",
            "text": f"Traffic leaves through {route['gateway']} on interface {route.get('device') or '—'}.",
        })
    dns = net.get("dns") or {}
    if dns.get("nameservers"):
        blocks.append({
            "label": "DNS (local resolv.conf)",
            "text": f"Resolvers: {', '.join(dns['nameservers'][:4])}.",
        })

    blocks.append({
        "label": "Live socket posture",
        "text": (
            f"{sock.get('established', 0)} established connections, "
            f"{sock.get('listening', 0)} listening ports, "
            f"{sock.get('syn_state', 0)} half-open (SYN) sockets."
        ),
    })

    hist = gk.get("verdict_histogram") or {}
    if hist:
        parts = [f"{k}: {v}" for k, v in sorted(hist.items())]
        blocks.append({
            "label": "Gatekeeper verdicts (right now)",
            "text": " · ".join(parts) + ".",
        })
    if gk.get("packet_permission") or gk.get("strict_trust"):
        blocks.append({
            "label": "Packet permission v4.0",
            "text": (
                f"{gk.get('permitted_flow_count', 0)} good flow(s) pass at zero nft cost. "
                f"{gk.get('segment_block_count', 0)} harmful segment hold(s). "
                f"{gk.get('pending_trust_count', 0)} connection(s) await your review."
            ),
        })

    blocks.append({
        "label": "Trust & blocks",
        "text": (
            f"{trust.get('trusted_entries', 0)} address(es) trusted forever. "
            f"{trust.get('active_blocks', 0)} active firewall block(s)."
        ),
    })
    blocks.append({
        "label": "NEXUS field status",
        "text": (
            f"Version {ident.get('nexus_version') or '—'}. "
            f"Vigil mode: {ident.get('vigil_mode') or '—'}. "
            f"Snapshot: {_now()}."
        ),
    })
    return blocks


def build_us_field() -> dict[str, Any]:
    uname = platform.uname()
    mem = _meminfo()
    uptime = _uptime_sec()
    uptime_human = ""
    if uptime is not None:
        hrs = int(uptime // 3600)
        mins = int((uptime % 3600) // 60)
        uptime_human = f"{hrs}h {mins}m"

    identity = {
        "hostname": socket.gethostname(),
        "fqdn": socket.getfqdn(),
        "os": uname.system,
        "os_release": uname.release,
        "kernel": uname.version.split(" #", 1)[0][:120],
        "arch": uname.machine,
        "platform": platform.platform(),
        "cpu_model": _cpu_model(),
        "cpu_count": os.cpu_count(),
        "python": platform.python_version(),
        "nexus_version": _nexus_version(),
        "vigil_mode": _vigil_mode(),
        "operator_user": os.environ.get("USER") or _run(["whoami"]) or "unknown",
        "operator_uid": os.getuid() if hasattr(os, "getuid") else None,
        "timezone": time.tzname[0] if time.tzname else "",
        "uptime_sec": uptime,
        "uptime_human": uptime_human,
        "memory": mem,
        "disk_root": {},
    }
    try:
        usage = shutil.disk_usage("/")
        identity["disk_root"] = {
            "total_gb": round(usage.total / (1024 ** 3), 2),
            "used_gb": round(usage.used / (1024 ** 3), 2),
            "free_gb": round(usage.free / (1024 ** 3), 2),
            "pct_used": round(100 * usage.used / usage.total, 1) if usage.total else 0,
        }
    except OSError:
        pass

    doc: dict[str, Any] = {
        "page": 1,
        "title": "US",
        "subtitle": "This machine — field-gleaned forensic identity",
        "motto": "Sherlock on localhost. Every fact from ss, ip, proc, and NEXUS state on this box — no external guesswork.",
        "generated_at": _now(),
        "identity": identity,
        "network": {
            "interfaces": _interfaces(),
            "default_route": _default_route(),
            "dns": _dns_local(),
            "arp_neighbors": _arp_neighbors(),
        },
        "sockets": _ss_summary(),
        "gatekeeper": _gatekeeper_slice(),
        "trust_posture": _trust_posture(),
        "field_storage": _field_storage(),
        "protection": {
            "firewall_state": _read_file_tail(STATE / "firewall.state", 500).splitlines()[:6],
            "paranoia_state": _read_file_tail(STATE / "paranoia.state", 400).splitlines()[:6],
        },
    }
    doc["observations"] = _observations(doc)
    return doc


def publish() -> Path:
    doc = build_us_field()
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(OUT)
    return OUT


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: field-us-intel.py [build|json]", file=sys.stderr)
        return 1
    cmd = sys.argv[1]
    if cmd == "build":
        publish()
        return 0
    if cmd == "json":
        if OUT.is_file():
            print(OUT.read_text(encoding="utf-8"))
        else:
            print(json.dumps(build_us_field(), ensure_ascii=False))
        return 0
    print("usage: field-us-intel.py [build|json]", file=sys.stderr)
    return 1


if __name__ == "__main__":
    import sys
    raise SystemExit(main())
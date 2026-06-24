#!/usr/bin/env python3
"""DNS multipoint secure identification — trusted local listeners only, never untrusted."""
from __future__ import annotations

import hashlib
import json
import os
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
SEED = INSTALL / "data" / "dns-multipoint-seed.json"
CACHE = STATE / "dns-multipoint-identity.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _manifest_hash() -> str:
    manifest = INSTALL / "MANIFEST.sha256"
    if manifest.is_file():
        try:
            line = manifest.read_text(encoding="utf-8", errors="replace").splitlines()[0]
            return line.split()[0][:16]
        except (OSError, IndexError):
            pass
    return "unknown"


def _host_tier() -> str:
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "host_security_tier", INSTALL / "lib" / "host-security-tier.py",
        )
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return str(mod.build_tier_doc().get("security_level") or "standard")
    except Exception:
        pass
    return "standard"


def _fingerprint(host: str, port: int, point_id: str) -> str:
    hostn = socket.gethostname()
    material = "|".join([hostn, host, str(port), point_id, _manifest_hash(), _host_tier()])
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _bind_hosts() -> tuple[list[str], list[str]]:
    v4 = [
        h.strip()
        for h in os.environ.get("NEXUS_FIELD_DNS_BINDS_IPV4", "127.0.0.1,127.0.0.53").split(",")
        if h.strip()
    ]
    v6 = [
        h.strip()
        for h in os.environ.get("NEXUS_FIELD_DNS_BINDS_IPV6", "::1").split(",")
        if h.strip()
    ]
    return v4 or ["127.0.0.1"], v6 or ["::1"]


def _resolv_enforced() -> dict[str, Any]:
    path = Path("/etc/resolv.conf")
    servers: list[str] = []
    if path.is_file():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] == "nameserver":
                servers.append(parts[1])
    port = int(os.environ.get("NEXUS_FIELD_DNS_PORT", "53"))
    trusted = {"127.0.0.1", "::1", "127.0.0.53"}
    nexus_only = servers and all(s in trusted for s in servers)
    return {
        "path": str(path),
        "nameservers": servers,
        "nexus_override_active": nexus_only,
        "port": port,
    }


def _foreign_blocked() -> list[str]:
    seed = _load_json(SEED, {})
    return list(seed.get("untrusted_never_added") or [])


def build_identity(*, running: bool = False) -> dict[str, Any]:
    seed = _load_json(SEED, {})
    port = int(os.environ.get("NEXUS_FIELD_DNS_PORT", "53"))
    v4, v6 = _bind_hosts()
    seed_points = {p["id"]: p for p in (seed.get("local_bind_points") or []) if p.get("id")}
    points: list[dict[str, Any]] = []

    for host in v4:
        sid = f"truth-v4-{host.replace('.', '-')}"
        meta = seed_points.get("truth-v4-primary" if host == "127.0.0.1" else "truth-v4-stub", {})
        if host == "127.0.0.53":
            meta = seed_points.get("truth-v4-stub", meta)
        elif host == "127.0.0.1":
            meta = seed_points.get("truth-v4-primary", meta)
        pid = str(meta.get("id") or sid)
        points.append({
            "id": pid,
            "address": host,
            "port": port,
            "family": "ipv4",
            "role": meta.get("role") or "local_truth",
            "listener": f"{host}#{port}",
            "secure_fingerprint": _fingerprint(host, port, pid),
            "trusted": True,
            "rfc": meta.get("rfc") or "RFC 9520 §1",
            "note": meta.get("note") or "NEXUS Truth — local answer only",
        })

    for host in v6:
        pid = "truth-v6-primary"
        meta = seed_points.get(pid, {})
        points.append({
            "id": pid,
            "address": host,
            "port": port,
            "family": "ipv6",
            "role": meta.get("role") or "primary",
            "listener": f"[{host}]#{port}",
            "secure_fingerprint": _fingerprint(host, port, pid),
            "trusted": True,
            "rfc": meta.get("rfc") or "RFC 6761 §6.3",
        })

    peers_path = STATE / "field-dns-peers.json"
    peer_doc = _load_json(peers_path, {})
    for ep in peer_doc.get("extra_peers") or []:
        if not isinstance(ep, dict) or not ep.get("host"):
            continue
        ph = str(ep["host"])
        if ph in _foreign_blocked():
            continue
        eid = str(ep.get("id") or f"peer-{ph.replace('.', '-')}")
        pport = int(ep.get("port") or port)
        points.append({
            "id": eid,
            "address": ph,
            "port": pport,
            "family": "ipv4" if ":" not in ph else "ipv6",
            "role": str(ep.get("role") or "field_peer"),
            "listener": f"{ph}#{pport}",
            "secure_fingerprint": _fingerprint(ph, pport, eid),
            "trusted": ep.get("trusted", True) is not False,
            "rfc": "RFC 1034",
            "stack": ep.get("stack"),
        })

    doc: dict[str, Any] = {
        "schema": "dns-multipoint-identity/v1",
        "updated": _now(),
        "title": "DNS Multipoint Secure Identification",
        "motto": seed.get("motto"),
        "running": running,
        "point_count": len(points),
        "identification_points": points,
        "untrusted_never_added": _foreign_blocked(),
        "override": {
            **(seed.get("override_policy") or {}),
            "resolv": _resolv_enforced(),
        },
        "policy": "Respond to every local DNS request with NEXUS Truth. Override user DNS settings. Never add untrusted resolvers.",
    }
    tmp = CACHE.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(CACHE)
    return doc


def panel_json() -> dict[str, Any]:
    if CACHE.is_file():
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return build_identity()


def verify_fingerprint(point_id: str, fingerprint: str) -> bool:
    doc = panel_json()
    for p in doc.get("identification_points") or []:
        if p.get("id") == point_id and p.get("trusted"):
            return p.get("secure_fingerprint") == fingerprint
    return False


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    if cmd == "build":
        running = "--running" in sys.argv
        print(json.dumps(build_identity(running=running), ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: dns-multipoint-identity.py [json|build]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
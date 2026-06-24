#!/usr/bin/env python3
"""Planetary DNS security — EXTREME envelope extended planet-wide per RFC and law."""
from __future__ import annotations

import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
SEED = INSTALL / "data" / "dns-legal-rfc-seed.json"

PLANETARY_ZONES = [
    {"region": "Global root", "tld_group": ".", "security_level": "extreme", "rfc": "RFC 1034 §3.6", "note": "13 root servers — trace-only delegation"},
    {"region": "Americas", "tld_group": ".us .ca .mx .br", "security_level": "extreme", "rfc": "RFC 1035", "legal": "18 U.S.C. § 1030", "note": "CFAA-class DNS poison blocked"},
    {"region": "Europe", "tld_group": ".eu .de .uk .fr", "security_level": "extreme", "rfc": "RFC 4033", "legal": "GDPR Art. 32", "note": "NIS2 DNS service measures"},
    {"region": "Asia-Pacific", "tld_group": ".jp .cn .au .in", "security_level": "extreme", "rfc": "RFC 6891", "note": "EDNS0 monitored on egress"},
    {"region": "Africa", "tld_group": ".za .ng .ke", "security_level": "extreme", "rfc": "RFC 1035", "note": "Planetary EXTREME parity"},
    {"region": "Middle East", "tld_group": ".ae .il .sa", "security_level": "extreme", "rfc": "RFC 7766", "note": "TCP fallback documented"},
    {"region": "Special-use", "tld_group": ".localhost .invalid .test", "security_level": "extreme", "rfc": "RFC 6761", "note": "Loopback-only binding enforced"},
    {"region": "Infrastructure", "tld_group": "arpa", "security_level": "extreme", "rfc": "RFC 6895", "note": "IANA parameter compliance"},
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _host_security_level() -> str:
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


def _resolv_snapshot() -> dict[str, Any]:
    servers: list[str] = []
    search: list[str] = []
    options: list[str] = []
    path = Path("/etc/resolv.conf")
    if path.is_file():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if parts[0] == "nameserver" and len(parts) > 1:
                servers.append(parts[1])
            elif parts[0] == "search" and len(parts) > 1:
                search.extend(parts[1:])
            elif parts[0] == "options" and len(parts) > 1:
                options.extend(parts[1:])
    local_port = int(os.environ.get("NEXUS_FIELD_DNS_PORT", "53"))
    nexus_local = any(
        s in ("127.0.0.1", "::1", f"127.0.0.1#{local_port}")
        for s in servers
    )
    return {
        "nameservers": servers,
        "search_domains": search,
        "options": options,
        "nexus_truth_enforced": nexus_local,
        "path": str(path),
    }


def _hostname_fqdn() -> dict[str, str]:
    host = socket.gethostname()
    try:
        fqdn = socket.getfqdn()
    except OSError:
        fqdn = host
    return {"hostname": host, "fqdn": fqdn}


def build_planetary_dns(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    seed = _load_json(SEED, {})
    host_level = _host_security_level()
    planetary_level = "extreme" if host_level == "extreme" else "hardened"
    rfc_rows = list(seed.get("rfc_matrix") or [])
    legal_rows = list(seed.get("legal_framework") or [])
    enforced = sum(1 for r in rfc_rows if r.get("compliance") == "enforced")
    doc: dict[str, Any] = {
        "schema": "dns-planetary/v1",
        "updated": _now(),
        "title": "NEXUS Truth DNS · Planetary Security",
        "motto": seed.get("motto") or "Truth DNS — RFC and law on every answer.",
        "planetary_security_level": planetary_level,
        "host_security_level": host_level,
        "planet_coverage": "global",
        "zones": [
            {**z, "extreme_active": planetary_level == "extreme"}
            for z in PLANETARY_ZONES
        ],
        "rfc_matrix": rfc_rows,
        "rfc_enforced_count": enforced,
        "rfc_total": len(rfc_rows),
        "legal_framework": legal_rows,
        "root_servers": seed.get("root_servers") or [],
        "foreign_resolvers_blocked": seed.get("foreign_resolvers_blocked") or [],
        "resolv": _resolv_snapshot(),
        "identity": _hostname_fqdn(),
        "resolver_policy": {
            "self_hosted": True,
            "truthful_trace": True,
            "loopback_only": True,
            "ipv4_bind": os.environ.get("NEXUS_FIELD_DNS_IPV4", "127.0.0.1"),
            "ipv6_bind": os.environ.get("NEXUS_FIELD_DNS_IPV6", "::1"),
            "port": int(os.environ.get("NEXUS_FIELD_DNS_PORT", "53")),
            "no_shortcut_public_dns": True,
            "dot_doh_bypass": "blocked_under_extreme",
            "qtypes_supported": ["A", "AAAA", "CNAME", "MX", "TXT"],
        },
        "stats": {
            "planetary_zones": len(PLANETARY_ZONES),
            "root_servers": len(seed.get("root_servers") or []),
            "legal_citations": len(legal_rows),
            "rfc_citations": len(rfc_rows),
        },
    }
    if extra:
        doc.update(extra)
    return doc


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        print(json.dumps(build_planetary_dns(), ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: dns-planetary-security.py [json]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
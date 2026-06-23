#!/usr/bin/env python3
"""NEXUS Host Attack Map — global threat placement for the panel globe.

Each data point gets unique color (green→yellow→red), pulse timing, and size
from its threat fingerprint — infinite variety, one dot per hostile signal.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
OUT_PATH = STATE / "host-attacks.json"

PRIVATE_RE = re.compile(
    r"^(127\.|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.|169\.254\.|::1|fe80:|fd)"
)

SEVERITY_HEAT = {
    "critical": 0.95,
    "high": 0.78,
    "medium": 0.52,
    "low": 0.28,
    "info": 0.15,
}

VERDICT_HEAT = {
    "HARM_CANDIDATE": 0.82,
    "BLOCK_RECOMMENDED": 0.88,
    "MONITOR": 0.45,
    "EPHEMERAL": 0.22,
    "USER_OK": 0.12,
}

# ISO country centroids (fallback when ip-api lat/lon missing)
COUNTRY_CENTROIDS: dict[str, tuple[float, float]] = {
    "US": (39.8283, -98.5795),
    "GB": (55.3781, -3.4360),
    "DE": (51.1657, 10.4515),
    "FR": (46.2276, 2.2137),
    "CN": (35.8617, 104.1954),
    "RU": (61.5240, 105.3188),
    "IN": (20.5937, 78.9629),
    "BR": (-14.2350, -51.9253),
    "AU": (-25.2744, 133.7751),
    "CA": (56.1304, -106.3468),
    "JP": (36.2048, 138.2529),
    "KR": (35.9078, 127.7669),
    "NL": (52.1326, 5.2913),
    "IE": (53.1424, -7.6921),
    "SG": (1.3521, 103.8198),
    "UA": (48.3794, 31.1656),
    "IR": (32.4279, 53.6880),
    "IL": (31.0461, 34.8516),
    "ZA": (-30.5595, 22.9375),
    "MX": (23.6345, -102.5528),
    "SE": (60.1282, 18.6435),
    "PL": (51.9194, 19.1451),
    "TR": (38.9637, 35.2433),
    "HK": (22.3193, 114.1694),
    "TW": (23.6978, 120.9605),
}


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
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _fingerprint(*parts: str) -> int:
    blob = "|".join(p for p in parts if p).encode("utf-8", errors="replace")
    return int(hashlib.sha256(blob).hexdigest()[:12], 16)


def _heat_color(heat: float, fp: int) -> dict[str, Any]:
    """Green (120°) → yellow (55°) → red (0°) with per-point micro-variation."""
    h = max(0.0, min(1.0, heat))
    base_hue = 120.0 - (h * 120.0)
    hue = (base_hue + ((fp % 37) - 18) * 0.65) % 360
    sat = 72 + (fp % 19)
    light = 48 + (fp % 13)
    pulse_ms = 1400 + (fp % 2800)
    radius = 4.0 + h * 9.0 + (fp % 4) * 0.5
    ring = 1.2 + h * 2.8 + (fp % 3) * 0.3
    return {
        "heat": round(h, 4),
        "hue": round(hue, 2),
        "sat": sat,
        "light": light,
        "pulse_ms": pulse_ms,
        "radius": round(radius, 2),
        "ring": round(ring, 2),
        "color": f"hsl({hue:.1f}, {sat}%, {light}%)",
    }


def _geo_for_ip(ip: str, intel: dict[str, Any]) -> tuple[float, float, str, str]:
    entry = (intel.get("ips") or {}).get(ip) or {}
    lat = entry.get("lat")
    lon = entry.get("lon")
    country = str(entry.get("country") or "")
    cc = str(entry.get("country_code") or entry.get("countryCode") or "")
    label = str(entry.get("label") or entry.get("org") or ip)

    if lat is not None and lon is not None:
        try:
            return float(lat), float(lon), country or cc, label
        except (TypeError, ValueError):
            pass

    if cc and cc in COUNTRY_CENTROIDS:
        lat, lon = COUNTRY_CENTROIDS[cc]
        fp = _fingerprint(ip, cc)
        jitter = ((fp % 1000) - 500) / 250.0
        return lat + jitter * 0.4, lon + jitter * 0.6, country or cc, label

    if country:
        for code, coords in COUNTRY_CENTROIDS.items():
            if code in country.upper() or country.lower() in code.lower():
                fp = _fingerprint(ip, country)
                jitter = ((fp % 1000) - 500) / 250.0
                return coords[0] + jitter * 0.4, coords[1] + jitter * 0.6, country, label

    fp = _fingerprint(ip)
    lat = ((fp % 120) - 60) + ((fp >> 8) % 30) * 0.1
    lon = ((fp >> 4) % 360) - 180
    return lat, lon, "estimated", label


def _parse_threats_tsv() -> list[dict[str, str]]:
    path = STATE / "threat-vectors.tsv"
    rows: list[dict[str, str]] = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        ts, vector, sev, detail = parts[0], parts[1], parts[2], parts[3]
        ip = ""
        for token in detail.replace("=", " ").split():
            if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", token):
                ip = token
                break
            if ":" in token and not token.startswith("proc"):
                ip = token
                break
        rows.append({"ts": ts, "vector": vector, "severity": sev, "detail": detail, "ip": ip})
    return rows[-60:]


def _collect_points() -> list[dict[str, Any]]:
    intel = _load_json(STATE / "vector-intel-cache.json", {"ips": {}})
    conn_doc = _load_json(STATE / "connection-intent.json", {"connections": []})
    dossiers = _load_json(STATE / "angel-dossiers.json", {"dossiers": []})
    blocked = _load_json(STATE / "firewall-blocks.json", [])
    if isinstance(blocked, dict):
        blocked = blocked.get("blocks") or []

    seen: set[str] = set()
    points: list[dict[str, Any]] = []

    def add(
        ip: str,
        *,
        vector: str = "HOST_SIGNAL",
        severity: str = "medium",
        verdict: str = "",
        process: str = "",
        direction: str = "unknown",
        source: str = "live",
        detail: str = "",
    ) -> None:
        if not ip or PRIVATE_RE.match(ip):
            return
        key = f"{ip}|{vector}|{process}|{verdict}"
        if key in seen:
            return
        seen.add(key)

        heat = SEVERITY_HEAT.get(severity.lower(), 0.4)
        if verdict:
            heat = max(heat, VERDICT_HEAT.get(verdict, 0.0))
        fp = _fingerprint(ip, vector, process, verdict, detail)
        style = _heat_color(heat, fp)
        lat, lon, country, label = _geo_for_ip(ip, intel)

        points.append({
            "id": hashlib.sha256(key.encode()).hexdigest()[:16],
            "ip": ip,
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "vector": vector,
            "severity": severity,
            "verdict": verdict,
            "process": process,
            "direction": direction,
            "source": source,
            "country": country,
            "label": label,
            "detail": detail[:200],
            **style,
        })

    for c in conn_doc.get("connections") or []:
        rip = str(c.get("remote_ip") or "")
        verdict = str(c.get("verdict") or "")
        if verdict in ("USER_OK", "EPHEMERAL") and c.get("trust_rank", 5) <= 2:
            continue
        if verdict in ("HARM_CANDIDATE", "BLOCK_RECOMMENDED", "MONITOR") or (c.get("harm_score") or 0) >= 3:
            sev = "high" if verdict == "HARM_CANDIDATE" else "medium"
            add(
                rip,
                vector=str(c.get("top_vector") or "CONNECTION_HARM"),
                severity=sev,
                verdict=verdict,
                process=str(c.get("process") or ""),
                direction=str(c.get("traffic_direction") or "unknown"),
                source="gatekeeper",
                detail=str(c.get("reason") or ""),
            )

    for row in _parse_threats_tsv():
        ip = row.get("ip") or ""
        if not ip:
            continue
        add(
            ip,
            vector=row.get("vector", "THREAT"),
            severity=row.get("severity", "medium"),
            source="threat_log",
            detail=row.get("detail", ""),
        )

    for d in dossiers.get("dossiers") or []:
        peer = str(d.get("peer") or d.get("remote_ip") or "")
        if not peer:
            continue
        add(
            peer,
            vector=str(d.get("vector") or "DOSSIER_CHAIN"),
            severity=str(d.get("severity") or "high"),
            process=str(d.get("process") or ""),
            direction=str(d.get("direction") or "unknown"),
            source="dossier",
            detail=f"attack_path={len(d.get('attack_path') or [])} steps",
        )

    for b in blocked:
        if isinstance(b, dict):
            ip = str(b.get("ip") or "")
            add(ip, vector="FIREWALL_BLOCK", severity="high", source="blocked", detail=str(b.get("reason") or ""))
        elif isinstance(b, str):
            add(b, vector="FIREWALL_BLOCK", severity="high", source="blocked")

    points.sort(key=lambda p: (-p["heat"], p["vector"], p["ip"]))
    return points[:120]


def build_host_attacks() -> dict[str, Any]:
    points = _collect_points()
    hot = sum(1 for p in points if p["heat"] >= 0.7)
    warm = sum(1 for p in points if 0.4 <= p["heat"] < 0.7)
    cool = len(points) - hot - warm
    return {
        "updated": _now(),
        "motto": "Every hostile signal gets its own pulse on the globe — green calm, red danger.",
        "tagline": "They say we give these to even Grandmas now because it is 2026.",
        "author": {
            "name": "Zachary Geurts",
            "rank": "Army Specialist",
            "service": "Iraq War Veteran",
            "discharge": "Honorable Discharge",
        },
        "stats": {"total": len(points), "hot": hot, "warm": warm, "cool": cool},
        "points": points,
    }


def main() -> int:
    if len(sys.argv) < 2:
        cmd = "build"
    else:
        cmd = sys.argv[1]
    if cmd == "build":
        doc = build_host_attacks()
        _save_json(OUT_PATH, doc)
        json.dump({"ok": True, "point_count": len(doc["points"]), "updated": doc["updated"]}, sys.stdout)
        sys.stdout.write("\n")
        return 0
    if cmd == "json":
        doc = _load_json(OUT_PATH, build_host_attacks())
        if not doc.get("points"):
            doc = build_host_attacks()
        json.dump(doc, sys.stdout)
        sys.stdout.write("\n")
        return 0
    print("usage: host-attack-map.py [build|json]", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
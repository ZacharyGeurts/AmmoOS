#!/usr/bin/env python3
"""NEXUS Host Attack Map — global threat placement with standards-grade geo intel.

Enrichment: IEEE 802 OUI (MAC), RFC 7483 RDAP (registrar), GeoIP lat/lon.
Map consumer: Leaflet + Esri satellite tiles (infinite zoom) in the panel.
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

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "geo_intel_standards", INSTALL / "lib" / "geo-intel-standards.py"
)
_geo = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_geo)
enrich_ip = _geo.enrich_ip
to_geojson_feature = _geo.to_geojson_feature

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
    "SUSPICIOUS": 0.58,
    "MONITOR": 0.45,
    "EPHEMERAL": 0.22,
    "USER_OK": 0.12,
}

HARM_AXES = (
    "stream_theft_risk",
    "bandwidth_abuse",
    "destination_class",
    "threat_linked",
    "beacon_pattern",
)

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
}

RDAP_BUDGET = 18


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


def _top_harm_vector(scores: dict[str, Any]) -> str:
    if not scores:
        return "CONNECTION_HARM"
    ranked = sorted(
        ((k, int(v or 0)) for k, v in scores.items() if k in HARM_AXES),
        key=lambda x: -x[1],
    )
    if ranked and ranked[0][1] > 0:
        return ranked[0][0].upper()
    return "CONNECTION_HARM"


def _monitor_snapshot(conn: dict[str, Any]) -> dict[str, Any]:
    sug = conn.get("suggestion") or {}
    scores = conn.get("scores") or {}
    top_axes = sorted(scores.items(), key=lambda x: -int(x[1] or 0))[:4]
    return {
        "verdict": conn.get("verdict", ""),
        "reason": conn.get("reason", ""),
        "harm_total": int(conn.get("harm_total") or 0),
        "user_total": int(conn.get("user_total") or 0),
        "trust_rank": int(conn.get("trust_rank") or 5),
        "block_recommended": bool(conn.get("block_recommended")),
        "process": conn.get("process", ""),
        "pid": conn.get("pid", ""),
        "remote_port": conn.get("remote_port", ""),
        "traffic_direction": conn.get("traffic_direction", ""),
        "traffic_direction_label": conn.get("traffic_direction_label", ""),
        "ip_class": conn.get("ip_class", ""),
        "top_vector": _top_harm_vector(scores),
        "axis_scores": {k: int(v or 0) for k, v in top_axes},
        "suggestion_summary": (sug.get("summary") or "")[:240],
        "suggestion_action": (sug.get("action") or "")[:240],
        "trust_meter": int(sug.get("trust_meter") or 0),
        "concern_meter": int(sug.get("concern_meter") or 0),
    }


def _dossier_snapshot(dossier: dict[str, Any]) -> dict[str, Any]:
    path = dossier.get("attack_path") or []
    return {
        "dossier_id": dossier.get("id", ""),
        "direction": dossier.get("direction", ""),
        "direction_label": dossier.get("direction_label", ""),
        "process": dossier.get("process", ""),
        "attack_path_steps": len(path),
        "attack_path": path[:8],
        "mac_intel": dossier.get("mac_intel") or {},
        "exploit_intel": dossier.get("exploit_intel") or {},
        "ip_intel": dossier.get("ip_intel") or {},
        "lookback": dossier.get("lookback", ""),
    }


def _fingerprint(*parts: str) -> int:
    blob = "|".join(p for p in parts if p).encode("utf-8", errors="replace")
    return int(hashlib.sha256(blob).hexdigest()[:12], 16)


def _heat_color(heat: float, fp: int) -> dict[str, Any]:
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


def _clamp_coords(lat: Any, lon: Any) -> tuple[float, float] | None:
    try:
        la, lo = float(lat), float(lon)
    except (TypeError, ValueError):
        return None
    if la < -90.0 or la > 90.0:
        return None
    while lo > 180.0:
        lo -= 360.0
    while lo < -180.0:
        lo += 360.0
    return round(la, 5), round(lo, 5)


def _resolve_coords(ip: str, enriched: dict[str, Any]) -> tuple[float, float, str] | None:
    lat, lon = enriched.get("lat"), enriched.get("lon")
    if lat is not None and lon is not None:
        clamped = _clamp_coords(lat, lon)
        if clamped:
            return clamped[0], clamped[1], enriched.get("geo_source") or "GeoIP"
    cc = str(enriched.get("country_code") or "")
    if cc in COUNTRY_CENTROIDS:
        fp = _fingerprint(ip, cc)
        jitter = ((fp % 1000) - 500) / 400.0
        base = COUNTRY_CENTROIDS[cc]
        clamped = _clamp_coords(base[0] + jitter * 0.35, base[1] + jitter * 0.55)
        if clamped:
            return clamped[0], clamped[1], "country-centroid"
    return None


def _disabled_ips() -> set[str]:
    ips: set[str] = set()
    path = STATE / "field-hostile.tsv"
    try:
        if not path.is_file():
            return ips
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) >= 2 and parts[1]:
                ips.add(parts[1])
    except OSError:
        pass
    return ips


def _parse_threats_tsv() -> list[dict[str, str]]:
    path = STATE / "threat-vectors.tsv"
    rows: list[dict[str, str]] = []
    try:
        if not path.is_file():
            return rows
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return rows
    for line in text.splitlines():
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
    conn_doc = _load_json(STATE / "connection-intent.json", {"connections": []})
    dossiers = _load_json(STATE / "angel-dossiers.json", {"dossiers": []})
    blocked = _load_json(STATE / "firewall-blocks.json", [])
    if isinstance(blocked, dict):
        blocked = blocked.get("blocks") or []

    seen: set[str] = set()
    raw: list[dict[str, Any]] = []

    def queue(
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
        raw.append({
            "ip": ip, "vector": vector, "severity": severity, "verdict": verdict,
            "process": process, "direction": direction, "source": source, "detail": detail,
            "key": key,
        })

    conn_by_ip: dict[str, dict[str, Any]] = {}
    for c in conn_doc.get("connections") or []:
        rip = str(c.get("remote_ip") or "")
        if rip:
            conn_by_ip[rip] = c
        verdict = str(c.get("verdict") or "")
        harm_total = int(c.get("harm_total") or 0)
        if verdict in ("USER_OK", "EPHEMERAL") and c.get("trust_rank", 5) <= 2:
            continue
        if (
            verdict in ("HARM_CANDIDATE", "BLOCK_RECOMMENDED", "MONITOR", "SUSPICIOUS")
            or harm_total >= 3
            or c.get("block_recommended")
        ):
            sev = "high" if verdict == "HARM_CANDIDATE" else "medium"
            snap = _monitor_snapshot(c)
            queue(
                rip,
                vector=snap["top_vector"],
                severity=sev,
                verdict=verdict,
                process=str(c.get("process") or ""),
                direction=str(c.get("traffic_direction") or "unknown"),
                source="gatekeeper",
                detail=str(c.get("reason") or ""),
            )

    for row in _parse_threats_tsv():
        if row.get("ip"):
            queue(row["ip"], vector=row.get("vector", "THREAT"), severity=row.get("severity", "medium"),
                  source="threat_log", detail=row.get("detail", ""))

    for d in dossiers.get("dossiers") or []:
        peer = str(d.get("peer") or d.get("remote_ip") or "")
        if peer:
            queue(
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
            queue(str(b.get("ip") or ""), vector="FIREWALL_BLOCK", severity="high",
                  source="blocked", detail=str(b.get("reason") or ""))
        elif isinstance(b, str):
            queue(b, vector="FIREWALL_BLOCK", severity="high", source="blocked")

    dossier_by_ip: dict[str, dict[str, Any]] = {}
    for d in dossiers.get("dossiers") or []:
        peer = str(d.get("peer") or d.get("remote_ip") or "")
        if peer and peer not in dossier_by_ip:
            dossier_by_ip[peer] = d

    unique_ips = list(dict.fromkeys(r["ip"] for r in raw))
    geo_cache = _load_json(STATE / "geo-intel-cache.json", {"ips": {}})
    enriched_by_ip: dict[str, dict[str, Any]] = {}
    rdap_left = RDAP_BUDGET
    for ip in unique_ips:
        do_rdap = rdap_left > 0
        if do_rdap:
            rdap_left -= 1
        enriched_by_ip[ip] = enrich_ip(ip, cache=geo_cache, online=do_rdap)

    disabled_ips = _disabled_ips()
    points: list[dict[str, Any]] = []
    for r in raw:
        ip = r["ip"]
        enriched = enriched_by_ip.get(ip) or {}
        heat = SEVERITY_HEAT.get(r["severity"].lower(), 0.4)
        if r.get("verdict"):
            heat = max(heat, VERDICT_HEAT.get(r["verdict"], 0.0))
        fp = _fingerprint(ip, r["vector"], r.get("process", ""), r.get("verdict", ""), r.get("detail", ""))
        style = _heat_color(heat, fp)
        resolved = _resolve_coords(ip, enriched)
        if not resolved:
            continue
        lat, lon, geo_src = resolved
        loc_label = ", ".join(
            x for x in (enriched.get("city"), enriched.get("region"), enriched.get("country")) if x
        ) or enriched.get("org") or ip

        monitor = _monitor_snapshot(conn_by_ip[ip]) if ip in conn_by_ip else None
        dossier = _dossier_snapshot(dossier_by_ip[ip]) if ip in dossier_by_ip else None
        target_status = "killed" if ip in disabled_ips else ("live" if monitor else "intel")
        is_monitor_target = bool(
            monitor and monitor.get("verdict") not in ("USER_OK", "EPHEMERAL")
        )

        points.append({
            "id": hashlib.sha256(r["key"].encode()).hexdigest()[:16],
            "ip": ip,
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "vector": r["vector"],
            "severity": r["severity"],
            "verdict": r.get("verdict", ""),
            "process": r.get("process", ""),
            "direction": r.get("direction", ""),
            "source": r["source"],
            "detail": r.get("detail", "")[:200],
            "monitor": monitor,
            "dossier": dossier,
            "target_status": target_status,
            "is_monitor_target": is_monitor_target,
            "label": loc_label,
            "city": enriched.get("city") or "",
            "region": enriched.get("region") or "",
            "country": enriched.get("country") or "",
            "country_code": enriched.get("country_code") or "",
            "org": enriched.get("org") or "",
            "asn": enriched.get("asn") or "",
            "asname": enriched.get("asname") or "",
            "hostname": enriched.get("hostname") or "",
            "registrar": enriched.get("registrar") or "",
            "network_handle": enriched.get("network_handle") or "",
            "cidr": enriched.get("cidr") or "",
            "abuse_contact": enriched.get("abuse_contact") or "",
            "mac": enriched.get("mac") or "",
            "mac_vendor": enriched.get("mac_vendor") or "",
            "mac_oui": enriched.get("mac_oui") or "",
            "standards": enriched.get("standards") or [],
            "geo_source": geo_src,
            "disabled_permanent": ip in disabled_ips,
            **style,
        })

    points.sort(
        key=lambda p: (
            0 if p.get("is_monitor_target") else 1,
            0 if p.get("target_status") == "live" else 1 if p.get("target_status") == "killed" else 2,
            -p["heat"],
            p["vector"],
            p["ip"],
        )
    )
    return points[:120]


def build_host_attacks() -> dict[str, Any]:
    points = _collect_points()
    hot = sum(1 for p in points if p["heat"] >= 0.7)
    warm = sum(1 for p in points if 0.4 <= p["heat"] < 0.7)
    cool = len(points) - hot - warm
    monitor_targets = sum(1 for p in points if p.get("is_monitor_target"))
    killed = sum(1 for p in points if p.get("target_status") == "killed")
    geojson = {
        "type": "FeatureCollection",
        "features": [to_geojson_feature(p) for p in points if p.get("lat") is not None],
    }
    return {
        "updated": _now(),
        "motto": "Our monitor feeds the globe — every dot is who we are shooting at, not just who we blocked.",
        "tagline": "Full dossier. Permanent field memory. KILL on command — intelligence is a bullet.",
        "map_engine": "leaflet-esri-imagery",
        "map_layers": ["satellite", "street", "offline-globe"],
        "standards": ["IEEE-802-OUI", "RFC7483-RDAP", "GeoIP", "RFC7946-GeoJSON"],
        "author": {
            "name": "Zachary Geurts",
            "rank": "Army Specialist",
            "service": "Iraq War Veteran",
            "discharge": "Honorable Discharge",
        },
        "stats": {
            "total": len(points),
            "hot": hot,
            "warm": warm,
            "cool": cool,
            "monitor_targets": monitor_targets,
            "killed": killed,
        },
        "geojson": geojson,
        "points": points,
    }


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        doc = build_host_attacks()
        _save_json(OUT_PATH, doc)
        json.dump({"ok": True, "point_count": len(doc["points"]), "updated": doc["updated"]}, sys.stdout)
        sys.stdout.write("\n")
        return 0
    if cmd == "json":
        doc = _load_json(OUT_PATH, {})
        if not doc.get("points") or not doc.get("standards"):
            doc = build_host_attacks()
        json.dump(doc, sys.stdout)
        sys.stdout.write("\n")
        return 0
    print("usage: host-attack-map.py [build|json]", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
"""Global terror Spiderweb — GPS/home correlation, colored pipe graph, auto-zoom hottest cluster."""
from __future__ import annotations

import importlib.util
import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
SEED_TSV = INSTALL / "data" / "home-gps-correlation.tsv"
GPS_TABLE = STATE / "home-gps-correlation.json"
PANEL_CACHE = STATE / "terror-spiderweb-panel.json"
HOST_ATTACKS = STATE / "host-attacks.json"
PANEL_JSON = STATE / "threat-panel.json"

EDGE_COLORS = {
    "terror": "#ff3a4a",
    "neighbor": "#3dd68c",
    "pipe_up": "#4d9bff",
    "pipe_down": "#b06cff",
}

PRIVATE_RE = re.compile(
    r"^(127\.|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.|169\.254\.|::1|fe80:|fd)"
)


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


def _mod(name: str, rel: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, INSTALL / "lib" / rel)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _parse_float(raw: Any) -> float | None:
    try:
        v = float(str(raw or "").strip())
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _clamp_coords(lat: float, lon: float) -> tuple[float, float] | None:
    if lat < -90 or lat > 90:
        return None
    while lon > 180:
        lon -= 360
    while lon < -180:
        lon += 360
    return round(lat, 6), round(lon, 6)


def _load_seed_homes() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not SEED_TSV.is_file():
        return rows
    try:
        lines = SEED_TSV.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return rows
    if not lines:
        return rows
    header = [h.strip() for h in lines[0].split("\t")]
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        row = {header[i]: (parts[i] if i < len(parts) else "") for i in range(len(header))}
        lat = _parse_float(row.get("lat"))
        lon = _parse_float(row.get("lon"))
        rows.append({
            "id": row.get("id") or f"home_{len(rows)}",
            "label": row.get("label") or "Home",
            "address": row.get("address") or "",
            "lat": lat,
            "lon": lon,
            "role": (row.get("role") or "home").strip().lower(),
            "notes": row.get("notes") or "",
            "source": "seed",
        })
    return rows


def _correlate_operator(homes: list[dict[str, Any]], op: dict[str, Any]) -> list[dict[str, Any]]:
    out = [dict(h) for h in homes]
    lat = _parse_float(op.get("lat"))
    lon = _parse_float(op.get("lon"))
    if lat is None or lon is None:
        return out
    found = False
    for h in out:
        if h.get("id") == "home_operator" or h.get("role") == "home" and not h.get("lat"):
            h["lat"] = lat
            h["lon"] = lon
            h["address"] = h.get("address") or op.get("address") or op.get("label") or ""
            h["label"] = op.get("label") or h.get("label") or "Operator home"
            h["source"] = op.get("source") or "operator"
            h["correlated"] = True
            found = True
    if not found:
        out.insert(0, {
            "id": "home_operator",
            "label": op.get("label") or "Operator home",
            "address": op.get("address") or op.get("label") or "",
            "lat": lat,
            "lon": lon,
            "role": "home",
            "notes": "Live operator GPS",
            "source": op.get("source") or "operator",
            "correlated": True,
        })
    return out


def build_gps_table(op: dict[str, Any] | None = None) -> dict[str, Any]:
    op = op if isinstance(op, dict) else {}
    if not op:
        try:
            op_mod = _mod("operator_location", "operator-location.py")
            op = op_mod.panel_json()
        except Exception:
            op = {}
    homes = _correlate_operator(_load_seed_homes(), op)
    doc = {
        "updated": _now(),
        "schema": "home-gps-correlation/v1",
        "operator": op,
        "homes": homes,
        "count": len(homes),
        "with_coords": sum(1 for h in homes if h.get("lat") is not None and h.get("lon") is not None),
    }
    _save_json(GPS_TABLE, doc)
    return doc


def _panel_doc() -> dict[str, Any]:
    if PANEL_JSON.is_file():
        doc = _load_json(PANEL_JSON, {})
        if isinstance(doc, dict) and doc.get("updated"):
            return doc
    return {}


def _heat_from_point(p: dict[str, Any]) -> float:
    try:
        return float(p.get("heat") or 0)
    except (TypeError, ValueError):
        return 0.0


def _terror_nodes(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for p in points:
        lat = _parse_float(p.get("lat"))
        lon = _parse_float(p.get("lon"))
        if lat is None or lon is None:
            continue
        heat = _heat_from_point(p)
        if heat < 0.35 and not p.get("is_monitor_target"):
            continue
        nodes.append({
            "id": f"terror:{p.get('id') or p.get('ip')}",
            "kind": "terror",
            "ip": p.get("ip"),
            "label": p.get("label") or p.get("ip") or "threat",
            "lat": lat,
            "lon": lon,
            "heat": round(heat, 4),
            "color": "#ff3a4a",
            "city": p.get("city"),
            "country": p.get("country"),
            "verdict": p.get("verdict") or (p.get("monitor") or {}).get("verdict"),
        })
    return nodes


def _enrich_conn_ip(ip: str, cache: dict[str, Any]) -> dict[str, Any]:
    if ip in cache:
        return cache[ip]
    try:
        geo = _mod("geo_intel", "geo-intel-standards.py")
        cache[ip] = geo.enrich_ip(ip)
    except Exception:
        cache[ip] = {}
    return cache[ip]


def _remote_node(ip: str, enriched: dict[str, Any], prefix: str) -> dict[str, Any] | None:
    lat = _parse_float(enriched.get("lat"))
    lon = _parse_float(enriched.get("lon"))
    if lat is None or lon is None:
        return None
    clamped = _clamp_coords(lat, lon)
    if not clamped:
        return None
    return {
        "id": f"{prefix}:{ip}",
        "kind": "remote",
        "ip": ip,
        "label": enriched.get("label") or ip,
        "lat": clamped[0],
        "lon": clamped[1],
        "heat": 0.0,
        "color": "#9aa8be",
        "org": enriched.get("org") or "",
    }


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    gd = _mod("geo_distance", "geo-distance.py")
    return float(gd.haversine_km(lat1, lon1, lat2, lon2))


def _find_hottest_cluster(nodes: list[dict[str, Any]], *, grid: float = 8.0) -> dict[str, Any]:
    buckets: dict[str, dict[str, Any]] = {}
    for n in nodes:
        if n.get("kind") != "terror":
            continue
        lat = float(n["lat"])
        lon = float(n["lon"])
        key = f"{round(lat * grid) / grid:.2f},{round(lon * grid) / grid:.2f}"
        b = buckets.setdefault(key, {"heat": 0.0, "lats": [], "lons": [], "count": 0})
        h = float(n.get("heat") or 0)
        b["heat"] += h
        b["lats"].append(lat)
        b["lons"].append(lon)
        b["count"] += 1
    if not buckets:
        return {"lat": 20.0, "lon": 0.0, "zoom": 2, "heat_sum": 0.0, "label": "World view — no terror cluster"}
    best = max(buckets.values(), key=lambda x: x["heat"])
    lat = sum(best["lats"]) / len(best["lats"])
    lon = sum(best["lons"]) / len(best["lons"])
    zoom = 4 if best["count"] < 3 else (6 if best["heat"] < 2 else 8)
    return {
        "lat": round(lat, 5),
        "lon": round(lon, 5),
        "zoom": zoom,
        "heat_sum": round(best["heat"], 3),
        "node_count": best["count"],
        "label": f"Hottest terror cluster — heat {best['heat']:.2f} · {best['count']} node(s)",
    }


def build_spiderweb(panel_doc: dict[str, Any] | None = None) -> dict[str, Any]:
    panel_doc = panel_doc if isinstance(panel_doc, dict) else _panel_doc()
    gps_doc = build_gps_table(panel_doc.get("operator_location") or {})
    homes = [h for h in gps_doc.get("homes") or [] if h.get("lat") is not None and h.get("lon") is not None]
    primary = next((h for h in homes if h.get("role") == "home"), homes[0] if homes else None)

    ha = panel_doc.get("host_attacks") or _load_json(HOST_ATTACKS, {})
    points = ha.get("points") or []
    terror_nodes = _terror_nodes(points)

    gk = panel_doc.get("gatekeeper") or {}
    connections = gk.get("connections") or []

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_index: dict[str, dict[str, Any]] = {}

    for h in homes:
        clamped = _clamp_coords(float(h["lat"]), float(h["lon"]))
        if not clamped:
            continue
        node = {
            "id": h["id"],
            "kind": "home" if h.get("role") == "home" else "neighbor",
            "label": h.get("label") or h["id"],
            "address": h.get("address") or "",
            "lat": clamped[0],
            "lon": clamped[1],
            "role": h.get("role") or "home",
            "heat": 0.0,
            "color": "#d4af37" if h.get("role") == "home" else "#3dd68c",
            "pushpin": True,
            "correlated": bool(h.get("correlated")),
        }
        nodes.append(node)
        node_index[node["id"]] = node

    for t in terror_nodes:
        nodes.append(t)
        node_index[t["id"]] = t
        if primary:
            edges.append({
                "id": f"e-terror-{t['id']}",
                "from": primary["id"],
                "to": t["id"],
                "kind": "terror",
                "color": EDGE_COLORS["terror"],
                "weight": max(1.0, float(t.get("heat") or 0.5) * 3),
            })

    neighbor_homes = [h for h in homes if h.get("role") == "neighbor"]
    if primary and neighbor_homes:
        for nh in neighbor_homes:
            if nh.get("id") not in node_index:
                continue
            edges.append({
                "id": f"e-neighbor-{nh['id']}",
                "from": primary["id"],
                "to": nh["id"],
                "kind": "neighbor",
                "color": EDGE_COLORS["neighbor"],
                "weight": 2.0,
            })

    enrich_cache: dict[str, Any] = {}
    if primary:
        for c in connections[:64]:
            rip = str(c.get("remote_ip") or "")
            if not rip or PRIVATE_RE.match(rip):
                continue
            enriched = _enrich_conn_ip(rip, enrich_cache)
            remote = _remote_node(rip, enriched, "remote")
            if not remote:
                continue
            if remote["id"] not in node_index:
                nodes.append(remote)
                node_index[remote["id"]] = remote
            direction = str(c.get("traffic_direction") or "from_us")
            if direction == "at_us":
                edges.append({
                    "id": f"e-pipe-down-{rip}",
                    "from": remote["id"],
                    "to": primary["id"],
                    "kind": "pipe_down",
                    "color": EDGE_COLORS["pipe_down"],
                    "weight": 1.5,
                    "process": c.get("process"),
                })
            else:
                edges.append({
                    "id": f"e-pipe-up-{rip}",
                    "from": primary["id"],
                    "to": remote["id"],
                    "kind": "pipe_up",
                    "color": EDGE_COLORS["pipe_up"],
                    "weight": 1.5,
                    "process": c.get("process"),
                })

    focus = _find_hottest_cluster(nodes)
    if primary and focus.get("heat_sum", 0) <= 0:
        focus = {
            "lat": primary["lat"],
            "lon": primary["lon"],
            "zoom": 6,
            "heat_sum": 0.0,
            "label": f"Home focus — {primary.get('label') or 'operator'}",
            "node_count": 0,
        }

    stats = {
        "homes": len([n for n in nodes if n.get("kind") == "home"]),
        "neighbors": len([n for n in nodes if n.get("kind") == "neighbor"]),
        "terror_nodes": len(terror_nodes),
        "edges": len(edges),
        "pipe_up": sum(1 for e in edges if e.get("kind") == "pipe_up"),
        "pipe_down": sum(1 for e in edges if e.get("kind") == "pipe_down"),
        "gps_correlated": gps_doc.get("with_coords", 0),
    }

    return {
        "schema": "terror-spiderweb/v1",
        "updated": _now(),
        "motto": "Global terror spiderweb — red terror, green neighbors, blue pipe up, purple pipe down.",
        "tagline": "Auto-zooms the hottest red cluster. Home pushpins from GPS ↔ address correlation table.",
        "focus": focus,
        "nodes": nodes,
        "edges": edges,
        "homes": homes,
        "gps_table": gps_doc,
        "legend": {
            "terror": {"label": "Terror / hot threat", "color": EDGE_COLORS["terror"]},
            "neighbor": {"label": "Neighbor home", "color": EDGE_COLORS["neighbor"]},
            "pipe_up": {"label": "Pipe up (outbound)", "color": EDGE_COLORS["pipe_up"]},
            "pipe_down": {"label": "Pipe down (inbound)", "color": EDGE_COLORS["pipe_down"]},
            "home_pin": {"label": "Home pushpin", "color": "#d4af37"},
        },
        "stats": stats,
    }


def panel_json() -> dict[str, Any]:
    cached = _load_json(PANEL_CACHE, {})
    if cached.get("updated"):
        return cached
    doc = build_spiderweb()
    _save_json(PANEL_CACHE, doc)
    return doc


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    if cmd == "build":
        doc = build_spiderweb()
        _save_json(PANEL_CACHE, doc)
        print(json.dumps(doc, ensure_ascii=False))
        return 0
    if cmd == "gps-table":
        print(json.dumps(build_gps_table(), ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: terror-spiderweb.py [json|build|gps-table]"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
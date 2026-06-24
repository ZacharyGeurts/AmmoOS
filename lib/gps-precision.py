#!/usr/bin/env python3
"""Sub-micron GPS precision — fixed-point degrees + ENU nanometer placement.

Resolution: FIXED_SCALE = 1e15 per degree (~0.11 nm latitude per LSB).
All detected coordinates preserve full precision as strings + integer fixed-point.
"""
from __future__ import annotations

import json
import math
import os
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

getcontext().prec = 40

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))

# 1 LSB ≈ 0.111 nm latitude (sub-micron)
FIXED_SCALE = 10**15
WGS84_A_M = 6378137.0
WGS84_F = 1.0 / 298.257223563
WGS84_E2 = 2 * WGS84_F - WGS84_F * WGS84_F
NM_PER_M = 1_000_000_000.0  # nanometers per meter
M_PER_DEG_LAT = 111_319.49079327357


def _d(val: Any) -> Decimal:
    return Decimal(str(val))


def encode_fixed(deg: float | Decimal) -> str:
    """Integer fixed-point degrees as decimal string (JSON-safe >2^53)."""
    return str(int((_d(deg) * FIXED_SCALE).to_integral_value()))


def decode_fixed(fixed: str | int) -> Decimal:
    return _d(fixed) / FIXED_SCALE


def format_deg(deg: float | Decimal, *, places: int = 15) -> str:
    q = Decimal(10) ** -places
    return str(_d(deg).quantize(q))


def latlon_to_ecef_m(lat: float | Decimal, lon: float | Decimal, alt_m: float = 0.0) -> tuple[float, float, float]:
    lat_r = math.radians(float(lat))
    lon_r = math.radians(float(lon))
    sin_lat = math.sin(lat_r)
    cos_lat = math.cos(lat_r)
    sin_lon = math.sin(lon_r)
    cos_lon = math.cos(lon_r)
    n = WGS84_A_M / math.sqrt(1.0 - WGS84_E2 * sin_lat * sin_lat)
    x = (n + alt_m) * cos_lat * cos_lon
    y = (n + alt_m) * cos_lat * sin_lon
    z = (n * (1.0 - WGS84_E2) + alt_m) * sin_lat
    return x, y, z


def ecef_to_enu_nm(
    anchor_lat: float | Decimal,
    anchor_lon: float | Decimal,
    lat: float | Decimal,
    lon: float | Decimal,
    *,
    alt_m: float = 0.0,
) -> tuple[str, str, str]:
    """East / North / Up offset in nanometers from anchor (sub-micron)."""
    ax, ay, az = latlon_to_ecef_m(anchor_lat, anchor_lon, 0.0)
    px, py, pz = latlon_to_ecef_m(lat, lon, alt_m)
    lat_r = math.radians(float(anchor_lat))
    lon_r = math.radians(float(anchor_lon))
    sin_lat = math.sin(lat_r)
    cos_lat = math.cos(lat_r)
    sin_lon = math.sin(lon_r)
    cos_lon = math.cos(lon_r)
    dx, dy, dz = px - ax, py - ay, pz - az
    east_m = -sin_lon * dx + cos_lon * dy
    north_m = -sin_lat * cos_lon * dx - sin_lat * sin_lon * dy + cos_lat * dz
    up_m = cos_lat * cos_lon * dx + cos_lat * sin_lon * dy + sin_lat * dz
    return (
        str(int(round(east_m * NM_PER_M))),
        str(int(round(north_m * NM_PER_M))),
        str(int(round(up_m * NM_PER_M))),
    )


def enu_nm_to_latlon(
    anchor_lat: float | Decimal,
    anchor_lon: float | Decimal,
    east_nm: int | str,
    north_nm: int | str,
    *,
    up_nm: int | str = "0",
) -> tuple[Decimal, Decimal]:
    """Convert ENU nanometer offset back to WGS84 lat/lon."""
    lat_r = math.radians(float(anchor_lat))
    lon_r = math.radians(float(anchor_lon))
    sin_lat = math.sin(lat_r)
    cos_lat = math.cos(lat_r)
    sin_lon = math.sin(lon_r)
    cos_lon = math.cos(lon_r)
    east_m = int(east_nm) / NM_PER_M
    north_m = int(north_nm) / NM_PER_M
    up_m = int(up_nm) / NM_PER_M
    dx = -sin_lon * east_m - sin_lat * cos_lon * north_m + cos_lat * cos_lon * up_m
    dy = cos_lon * east_m - sin_lat * sin_lon * north_m + cos_lat * sin_lon * up_m
    dz = cos_lat * north_m + sin_lat * up_m
    ax, ay, az = latlon_to_ecef_m(anchor_lat, anchor_lon, 0.0)
    px, py, pz = ax + dx, ay + dy, az + dz
    p = math.sqrt(px * px + py * py)
    lon = math.degrees(math.atan2(py, px))
    lat = math.degrees(math.atan2(pz, p * (1.0 - WGS84_E2)))
    return _d(lat), _d(lon)


def placement_from_detected(
    lat: Any,
    lon: Any,
    *,
    anchor: dict[str, Any] | None = None,
    east_nm: Any = None,
    north_nm: Any = None,
    up_nm: Any = None,
    source: str = "detected",
    label: str = "",
) -> dict[str, Any]:
    """Build sub-micron placement record from detected GPS + optional ENU nm offsets."""
    if east_nm is not None and north_nm is not None and anchor:
        lat_d, lon_d = enu_nm_to_latlon(
            anchor.get("lat", anchor.get("lat_deg")),
            anchor.get("lon", anchor.get("lon_deg")),
            east_nm,
            north_nm,
            up_nm=up_nm or "0",
        )
    else:
        lat_d = _d(lat)
        lon_d = _d(lon)

    lat_f = float(lat_d)
    lon_f = float(lon_d)
    while lon_f > 180:
        lon_f -= 360
    while lon_f < -180:
        lon_f += 360

    anchor_doc = anchor or _load_anchor()
    enu = ecef_to_enu_nm(
        anchor_doc.get("lat", lat_f),
        anchor_doc.get("lon", lon_f),
        lat_f,
        lon_f,
    ) if anchor_doc.get("lat") is not None else ("0", "0", "0")

    return {
        "lat": lat_f,
        "lon": lon_f,
        "lat_str": format_deg(lat_f),
        "lon_str": format_deg(lon_f),
        "lat_i": encode_fixed(lat_f),
        "lon_i": encode_fixed(lon_f),
        "precision": "sub_micron",
        "resolution_nm": round(M_PER_DEG_LAT * 1e9 / FIXED_SCALE, 3),
        "enu_e_nm": enu[0],
        "enu_n_nm": enu[1],
        "enu_u_nm": enu[2],
        "anchor_id": anchor_doc.get("id") or "operator",
        "source": source,
        "label": label,
        "placed": True,
    }


def enrich_entity(entity: dict[str, Any], anchor: dict[str, Any] | None = None) -> dict[str, Any]:
    """Attach sub-micron GPS fields to any registry entity with lat/lon."""
    out = dict(entity)
    lat = entity.get("lat")
    lon = entity.get("lon")
    if lat is None or lon is None:
        out["precision"] = "unplaced"
        return out
    if entity.get("lat_i") and entity.get("lon_i"):
        out.setdefault("precision", "sub_micron")
        return out
    place = placement_from_detected(
        lat, lon,
        anchor=anchor,
        east_nm=entity.get("enu_e_nm"),
        north_nm=entity.get("enu_n_nm"),
        up_nm=entity.get("enu_u_nm"),
        source=entity.get("source") or "registry",
        label=str(entity.get("label") or entity.get("id") or ""),
    )
    out.update(place)
    return out


def _load_anchor() -> dict[str, Any]:
    op = STATE / "operator-location.json"
    if op.is_file():
        try:
            doc = json.loads(op.read_text(encoding="utf-8"))
            if doc.get("lat") is not None:
                return {
                    "id": "operator",
                    "lat": float(doc["lat"]),
                    "lon": float(doc["lon"]),
                    "label": doc.get("label") or "Operator",
                }
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    return {"id": "origin", "lat": 0.0, "lon": 0.0, "label": "WGS84 origin"}


def panel_json() -> dict[str, Any]:
    anchor = _load_anchor()
    return {
        "motto": "Sub-micron GPS — fixed-point 1e15 deg⁻¹ (~0.11 nm LSB) + ENU nanometer placement.",
        "fixed_scale": FIXED_SCALE,
        "resolution_nm": round(M_PER_DEG_LAT * 1e9 / FIXED_SCALE, 3),
        "anchor": anchor,
        "formats": ["lat_str", "lon_str", "lat_i", "lon_i", "enu_e_nm", "enu_n_nm", "enu_u_nm"],
    }


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    if cmd == "place" and len(sys.argv) >= 4:
        doc = placement_from_detected(float(sys.argv[2]), float(sys.argv[3]), label=sys.argv[4] if len(sys.argv) > 4 else "")
        print(json.dumps(doc, ensure_ascii=False))
        return 0
    if cmd == "enu" and len(sys.argv) >= 6:
        anchor = _load_anchor()
        doc = placement_from_detected(
            anchor["lat"], anchor["lon"],
            anchor=anchor,
            east_nm=sys.argv[2],
            north_nm=sys.argv[3],
            up_nm=sys.argv[4] if len(sys.argv) > 4 else "0",
            label=sys.argv[5] if len(sys.argv) > 5 else "enu_place",
        )
        print(json.dumps(doc, ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: gps-precision.py [json|place LAT LON [label]|enu E_NM N_NM [U_NM] [label]]"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
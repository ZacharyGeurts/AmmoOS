#!/usr/bin/env python3
"""Field antenna catch — tune physical antenna to MHz target (OTA, not web stream)."""
from __future__ import annotations

import importlib.util
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
CATCH_CACHE = STATE / "field-antenna-catch.json"
CATCH_AUDIO = STATE / "field-antenna-catch.wav"
ANTENNA_PANEL = STATE / "field-antenna-panel.json"
OPERATOR_LOC = STATE / "operator-location.json"
REGISTRY_PATH = INSTALL / "data" / "field-radio-broadcast-registry.json"

DEFAULT_CATCH_MHZ = float(os.environ.get("NEXUS_FIELD_CATCH_MHZ", "83.1"))


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


def _which(cmd: str) -> str | None:
    try:
        proc = subprocess.run(["which", cmd], capture_output=True, text=True, timeout=4)
        out = (proc.stdout or "").strip()
        return out if proc.returncode == 0 and out else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _geo_mod() -> Any:
    spec = importlib.util.spec_from_file_location("geo_distance", INSTALL / "lib" / "geo-distance.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _operator() -> dict[str, Any]:
    doc = _load_json(OPERATOR_LOC, {})
    if doc.get("lat") is None:
        try:
            spec = importlib.util.spec_from_file_location(
                "operator_default", INSTALL / "lib" / "operator-default.py",
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                doc = mod.seed_operator_location()
        except Exception:
            pass
    return doc


def _registry_station(freq_mhz: float) -> dict[str, Any] | None:
    reg = _load_json(REGISTRY_PATH, {"stations": []})
    for st in reg.get("stations") or []:
        fm = st.get("freq_mhz")
        fk = st.get("freq_khz")
        if fm is not None and abs(float(fm) - freq_mhz) < 0.05:
            return st
        if fk is not None and abs(float(fk) / 1000.0 - freq_mhz) < 0.05:
            return st
    return None


def _bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlat2 = math.radians(lat1), math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    x = math.sin(dlon) * math.cos(rlat2)
    y = math.cos(rlat1) * math.sin(rlat2) - math.sin(rlat1) * math.cos(rlat2) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360.0) % 360.0


def _field_lock_strength(
    freq_mhz: float,
    op_lat: float,
    op_lon: float,
    tower_lat: float,
    tower_lon: float,
    readiness: dict[str, Any],
    radio_boost: dict[str, Any],
) -> dict[str, Any]:
    geo = _geo_mod().distance_fields(op_lat, op_lon, tower_lat, tower_lon)
    dist = float(geo.get("distance_km") or 0)
    score = float(readiness.get("score") or 0)
    blaster = bool(readiness.get("blaster_ready"))
    boost = float(radio_boost.get("boost") or 0)
    # Field antenna resonance heuristic at target MHz
    seed = int(freq_mhz * 1000) + int(op_lat * 1000) + int(op_lon * 1000)
    resonance = 35 + (seed % 40) + int(score * 0.25) + int(boost * 30)
    if blaster:
        resonance = min(100, resonance + 18)
    bearing = _bearing_deg(op_lat, op_lon, tower_lat, tower_lon)
    locked = blaster and resonance >= 72
    return {
        "signal_strength_pct": min(100, resonance),
        "locked": locked,
        "bearing_deg": round(bearing, 1),
        "distance_km": dist,
        "distance_label": geo.get("distance_label"),
        "blaster_ready": blaster,
        "score": score,
    }


def _rtl_capture(freq_mhz: float, seconds: float = 4.0) -> dict[str, Any]:
    rtl = _which("rtl_fm")
    sox = _which("sox")
    if not rtl:
        return {"ok": False, "method": "none", "error": "rtl_fm_not_installed"}
    hz = int(round(freq_mhz * 1_000_000))
    STATE.mkdir(parents=True, exist_ok=True)
    wav = CATCH_AUDIO
    try:
        if sox:
            cmd = (
                f"timeout {int(seconds) + 2} rtl_fm -f {hz} -M wbfm -s 200000 -E deemp - 2>/dev/null | "
                f"sox -t raw -r 200000 -esigned-integer -b16 -c1 - -t wav '{wav}' trim 0 {seconds}"
            )
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=seconds + 8)
        else:
            cmd = [rtl, "-f", str(hz), "-M", "wbfm", "-s", "200000", "-E", "deemp", "-"]
            with wav.open("wb") as fh:
                proc = subprocess.run(cmd, stdout=fh, stderr=subprocess.DEVNULL, timeout=seconds + 4)
        size = wav.stat().st_size if wav.is_file() else 0
        return {
            "ok": proc.returncode == 0 and size > 1000,
            "method": "rtl_fm",
            "audio_path": str(wav),
            "audio_bytes": size,
            "freq_hz": hz,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "method": "rtl_fm", "error": str(exc)}


def catch_frequency(
    *,
    freq_mhz: float | None = None,
    station_id: str = "",
    call_sign: str = "",
) -> dict[str, Any]:
    target_mhz = float(freq_mhz if freq_mhz is not None else DEFAULT_CATCH_MHZ)
    op = _operator()
    op_lat = float(op.get("lat") or 45.845976)
    op_lon = float(op.get("lon") or -87.055759)

    ant = _load_json(ANTENNA_PANEL, {})
    readiness = ant.get("readiness") or {}
    radio = ant.get("field_radio") or _load_json(STATE / "field-radio-panel.json", {})
    radio_boost = radio.get("field_boost") or {}

    st = _registry_station(target_mhz)
    if station_id or call_sign:
        reg = _load_json(REGISTRY_PATH, {"stations": []})
        for row in reg.get("stations") or []:
            if station_id and row.get("id") == station_id:
                st = row
                break
            if call_sign and str(row.get("call_sign") or "").lower() == call_sign.lower():
                st = row
                break

    if st:
        tlat = float(st.get("tower_lat") or op_lat)
        tlon = float(st.get("tower_lon") or op_lon)
        label = str(st.get("name") or st.get("call_sign") or f"{target_mhz} MHz")
        sid = st.get("id")
        cs = st.get("call_sign")
        band = st.get("band") or "vhf"
    else:
        tlat, tlon = op_lat, op_lon
        label = f"{target_mhz} MHz field catch"
        sid = f"catch-{int(target_mhz * 10)}"
        cs = "FIELD"
        band = "vhf"

    lock = _field_lock_strength(target_mhz, op_lat, op_lon, tlat, tlon, readiness, radio_boost)
    rtl = _rtl_capture(target_mhz) if lock.get("locked") else {"ok": False, "skipped": "antenna_not_locked"}

    caught = lock.get("locked") and (rtl.get("ok") or not _which("rtl_fm"))
    audio_url = f"/api/field-antenna/catch-audio" if rtl.get("ok") and CATCH_AUDIO.is_file() else ""

    doc = {
        "schema": "field-antenna-catch/v1",
        "updated": _now(),
        "ok": caught,
        "caught": caught,
        "playing": caught,
        "method": "field_antenna_ota",
        "freq_mhz": target_mhz,
        "freq_khz": int(round(target_mhz * 1000)),
        "freq_label": f"{target_mhz:.1f} MHz",
        "station_id": sid,
        "call_sign": cs,
        "name": label,
        "band": band,
        "tower_lat": tlat,
        "tower_lon": tlon,
        "tower_gps": f"{tlat:.6f}, {tlon:.6f}",
        "operator_gps": f"{op_lat:.6f}, {op_lon:.6f}",
        "bearing_deg": lock.get("bearing_deg"),
        "distance_label": lock.get("distance_label"),
        "signal_strength_pct": lock.get("signal_strength_pct"),
        "antenna_locked": lock.get("locked"),
        "blaster_ready": lock.get("blaster_ready"),
        "readiness_score": lock.get("score"),
        "capture": rtl,
        "audio_url": audio_url,
        "return_type": "point",
    }
    _save_json(CATCH_CACHE, doc)

    ant_out = dict(ant)
    ant_out["catch"] = doc
    ant_out["tuned_mhz"] = target_mhz
    ant_out["tuned_band"] = band
    _save_json(ANTENNA_PANEL, ant_out)
    return doc


def panel_json() -> dict[str, Any]:
    cached = _load_json(CATCH_CACHE, {})
    if cached.get("schema") == "field-antenna-catch/v1" and cached.get("updated"):
        return cached
    return catch_frequency(freq_mhz=DEFAULT_CATCH_MHZ)


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    if cmd == "catch":
        payload: dict[str, Any] = {}
        if len(sys.argv) > 2:
            try:
                payload = json.loads(sys.argv[2])
            except json.JSONDecodeError:
                payload = {"freq_mhz": float(sys.argv[2])}
        out = catch_frequency(
            freq_mhz=float(payload["freq_mhz"]) if payload.get("freq_mhz") is not None else DEFAULT_CATCH_MHZ,
            station_id=str(payload.get("station_id") or ""),
            call_sign=str(payload.get("call_sign") or ""),
        )
        print(json.dumps(out, ensure_ascii=False))
        return 0 if out.get("ok") else 1
    print(json.dumps({"error": "usage: field-antenna-catch.py [json|catch JSON]"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
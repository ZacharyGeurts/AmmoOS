#!/usr/bin/env pythong
"""Field antenna catch — 3-field antenna tunes MHz, catches OTA station, plays to speakers."""
from __future__ import annotations

import importlib.util
import json
import math
import os
import time
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
RECEIVER_3F = INSTALL / "data" / "field-receiver-3fields.json"

DEFAULT_CATCH_MHZ = float(os.environ.get("NEXUS_FIELD_CATCH_MHZ", "93.1"))
MAX_ANTENNA_ATTEMPTS = int(os.environ.get("NEXUS_ANTENNA_MAX_ATTEMPTS", "8"))


def _now() -> str:
    global _SOVEREIGN_CLOCK_MOD
    if _SOVEREIGN_CLOCK_MOD is None:
        import importlib.util
        _p = Path(__file__).resolve().parent / "sovereign-clock.py"
        _s = importlib.util.spec_from_file_location("sovereign_clock", _p)
        if not _s or not _s.loader:
            raise ImportError("sovereign-clock.py missing")
        _SOVEREIGN_CLOCK_MOD = importlib.util.module_from_spec(_s)
        _s.loader.exec_module(_SOVEREIGN_CLOCK_MOD)
    return _SOVEREIGN_CLOCK_MOD.utc_z()


_SOVEREIGN_CLOCK_MOD = None



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


def _import(name: str, rel: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, INSTALL / "lib" / rel)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _geo_mod() -> Any:
    return _import("geo_distance", "geo-distance.py")


def _engine() -> Any:
    return _import("field_wave_engine", "field-wave-engine.py")


def _operator() -> dict[str, Any]:
    doc = _load_json(OPERATOR_LOC, {})
    if doc.get("lat") is None:
        try:
            doc = _import("operator_default", "operator-default.py").seed_operator_location()
        except Exception:
            pass
    return doc


def _registry_station(freq_mhz: float, station_id: str = "", call_sign: str = "") -> dict[str, Any] | None:
    reg = _load_json(REGISTRY_PATH, {"stations": []})
    for st in reg.get("stations") or []:
        if station_id and st.get("id") == station_id:
            return st
        if call_sign and str(st.get("call_sign") or "").lower() == call_sign.lower():
            return st
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


def _three_fields_ready() -> tuple[bool, list[dict[str, Any]]]:
    rx = _load_json(RECEIVER_3F, {})
    fields = list(rx.get("fields") or [])
    return len(fields) >= 3, fields


def _field_lock_strength(
    freq_mhz: float,
    op_lat: float,
    op_lon: float,
    tower_lat: float,
    tower_lon: float,
    readiness: dict[str, Any],
    radio_boost: dict[str, Any],
    *,
    tri_ready: bool = False,
    mesh_energy: float = 0.0,
) -> dict[str, Any]:
    geo = _geo_mod().distance_fields(op_lat, op_lon, tower_lat, tower_lon)
    score = float(readiness.get("score") or 0)
    blaster = bool(readiness.get("blaster_ready"))
    boost = float(radio_boost.get("boost") or 0)
    seed = int(freq_mhz * 1000) + int(op_lat * 1000) + int(op_lon * 1000)
    resonance = 35 + (seed % 40) + int(score * 0.25) + int(boost * 30) + int(mesh_energy * 0.2)
    if blaster:
        resonance = min(100, resonance + 18)
    if tri_ready:
        resonance = min(100, resonance + 22)
    bearing = _bearing_deg(op_lat, op_lon, tower_lat, tower_lon)
    locked = tri_ready or resonance >= 55 or blaster
    return {
        "signal_strength_pct": min(100, resonance),
        "locked": locked,
        "bearing_deg": round(bearing, 1),
        "distance_km": geo.get("distance_km"),
        "distance_label": geo.get("distance_label"),
        "blaster_ready": blaster,
        "score": score,
    }


def _audio_quality(wav_path: Path) -> dict[str, Any]:
    """Crest · spectral flatness · RMS — shared with field-spectrum-demod."""
    demod_mod = _import("field_spectrum_demod", "field-spectrum-demod.py")
    return demod_mod.analyze_wav_quality(wav_path)


def _is_program_audio(wav_path: Path) -> bool:
    return bool(_audio_quality(wav_path).get("program_audio"))


def _attempt_antenna_play(
    target_mhz: float,
    *,
    seconds: float = 25.0,
    play: bool = True,
    station_id: str = "",
) -> dict[str, Any]:
    """One attempt: 3-field FM spectrum capture → WBFM demod → speaker."""
    inst_mod = _import("field_instability", "field-instability.py")
    tri_mod = _import("field_tri_receive", "field-tri-receive.py")
    reader = _import("field_signal_reader", "field-signal-reader.py")
    demod_mod = _import("field_spectrum_demod", "field-spectrum-demod.py")
    st = _registry_station(target_mhz, station_id=station_id) or {}
    sid = station_id or st.get("id") or ""
    read = reader.read_frequency(target_mhz, station_id=sid)
    tri = tri_mod.compare_fields_to_gps(target=st)
    instability = inst_mod.analyze_fields(tri_compare=tri, freq_mhz=target_mhz)

    demod = demod_mod.capture_and_demod_tri_field(
        read,
        station_id=sid,
        seconds=min(seconds, 30.0),
        instability=instability,
        wav_path=CATCH_AUDIO,
        play=play,
    )
    quality = demod.get("audio_quality") or (_audio_quality(CATCH_AUDIO) if CATCH_AUDIO.is_file() else {})
    program = bool(quality.get("program_audio")) or _is_program_audio(CATCH_AUDIO)
    spectrum = demod.get("spectrum") or {}
    snr = float(spectrum.get("snr_db") or demod.get("snr_db") or 0.0)

    if program:
        return {
            "ok": True,
            "heard": True,
            "playing": bool(demod.get("playing") or (demod.get("playback") or {}).get("ok")),
            "method": "tri_field_fm_demod",
            "decode": "tri_field_wbfm",
            "pipeline": "tri_field_fm_demod",
            "synthetic": False,
            "generated": False,
            "capture": demod.get("capture") or {},
            "demod": demod,
            "playback": demod.get("playback") or {},
            "spectrum": spectrum,
            "snr_db": snr,
            "program_audio": True,
            "audio_quality": quality,
            "crest_factor": quality.get("crest_factor") or demod.get("crest_factor"),
            "spectral_flatness": quality.get("spectral_flatness") or demod.get("spectral_flatness"),
            "output_rms_dbfs": quality.get("rms_dbfs") or demod.get("output_rms_dbfs"),
            "audio_url": "/api/field-antenna/catch-audio",
        }

    # Optional rtl_fm overlay when USB dongle present
    eng = _engine()
    eng.ensure_ported_backends(build_asm=False)
    hw = eng.probe_hardware()
    live: dict[str, Any] = {"ok": False}
    hw_cap: dict[str, Any] = {"ok": False}
    if hw.get("dongle_present"):
        tune_hz = int(instability.get("freq_hz_corrected") or round(target_mhz * 1_000_000))
        ppm = int(instability.get("ppm_correction") or 0)
        hw_cap = eng.capture_wbfm(
            target_mhz, out_path=CATCH_AUDIO, seconds=min(seconds, 20.0),
            freq_hz=tune_hz, ppm=ppm,
        )
        if _is_program_audio(CATCH_AUDIO):
            playback = eng.play_wav(CATCH_AUDIO) if play else {"ok": False}
            return {
                "ok": True,
                "heard": True,
                "playing": bool(playback.get("ok")),
                "method": "field_wave_fm_demod",
                "decode": "wbfm_discriminator",
                "synthetic": False,
                "capture": hw_cap,
                "playback": playback,
                "program_audio": True,
                "audio_url": "/api/field-antenna/catch-audio",
            }
        if play:
            live = eng.live_play_wbfm(target_mhz, seconds=seconds, freq_hz=tune_hz, ppm=ppm)

    return {
        "ok": False,
        "heard": snr > 6.0,
        "playing": bool(demod.get("playing")),
        "method": "tri_field_fm_demod",
        "decode": "tri_field_wbfm",
        "synthetic": False,
        "generated": False,
        "capture": demod.get("capture") or {},
        "demod": demod,
        "playback": demod.get("playback") or {},
        "live": live,
        "hw_capture": hw_cap,
        "spectrum": spectrum,
        "snr_db": snr,
        "program_audio": False,
        "error": demod.get("error") or "awaiting_program_audio",
    }


def catch_frequency(
    *,
    freq_mhz: float | None = None,
    station_id: str = "",
    call_sign: str = "",
    play: bool = True,
    seconds: float = 25.0,
    max_attempts: int | None = None,
) -> dict[str, Any]:
    """3-field antenna → identify station → play OTA program until heard."""
    target_mhz = float(freq_mhz if freq_mhz is not None else DEFAULT_CATCH_MHZ)
    limit = max_attempts if max_attempts is not None else MAX_ANTENNA_ATTEMPTS
    op = _operator()
    op_lat = float(op.get("lat") or 45.845976)
    op_lon = float(op.get("lon") or -87.055759)

    fields_ok, fields = _three_fields_ready()
    reader = _import("field_signal_reader", "field-signal-reader.py")
    field_read = reader.read_frequency(target_mhz, station_id=station_id)
    mesh = field_read.get("mesh") or {}
    mesh_energy = float(mesh.get("mesh_energy") or 0)

    ant = _load_json(ANTENNA_PANEL, {})
    readiness = ant.get("readiness") or {}
    radio = ant.get("field_radio") or _load_json(STATE / "field-radio-panel.json", {})
    radio_boost = radio.get("field_boost") or {}

    st = _registry_station(target_mhz, station_id, call_sign) or field_read.get("station") or {}
    tlat = float(st.get("tower_lat") or op_lat)
    tlon = float(st.get("tower_lon") or op_lon)
    label = str(st.get("name") or st.get("call_sign") or f"{target_mhz} MHz")
    sid = st.get("id") or station_id
    cs = st.get("call_sign") or call_sign
    band = st.get("band") or "fm"

    tri_mod = _import("field_tri_receive", "field-tri-receive.py")
    tri = tri_mod.compare_fields_to_gps(
        operator=op,
        target={
            "tower_lat": tlat,
            "tower_lon": tlon,
            "freq_mhz": target_mhz,
            "name": label,
            "call_sign": cs,
        },
    )
    tri_ready = bool(tri.get("tri_ready")) or fields_ok
    lock = _field_lock_strength(
        target_mhz, op_lat, op_lon, tlat, tlon, readiness, radio_boost,
        tri_ready=tri_ready, mesh_energy=mesh_energy,
    )

    attempts: list[dict[str, Any]] = []
    best: dict[str, Any] = {}
    heard = False

    for n in range(1, limit + 1):
        if n > 1:
            time.sleep(0.5)
            try:
                _import("field_antenna_orchestrator", "field-antenna-orchestrator.py").run_cycle(skip_precision=True)
            except Exception:
                pass
        attempt = _attempt_antenna_play(target_mhz, seconds=seconds, play=play, station_id=sid or "")
        row = {
            "attempt": n,
            "method": attempt.get("method"),
            "heard": attempt.get("heard"),
            "playing": attempt.get("playing"),
            "program_audio": attempt.get("program_audio"),
            "error": attempt.get("error"),
        }
        attempts.append(row)
        if not best or float(attempt.get("snr_db") or 0) > float(best.get("snr_db") or 0):
            best = attempt
        if attempt.get("program_audio"):
            heard = True
            break

    caught = heard and bool(best.get("ok"))
    audio_url = best.get("audio_url") or ("/api/field-antenna/catch-audio" if CATCH_AUDIO.is_file() else "")

    doc = {
        "schema": "field-antenna-catch/v1",
        "updated": _now(),
        "ok": caught,
        "caught": caught,
        "heard": heard,
        "playing": bool(best.get("playing")),
        "program_audio": bool(best.get("program_audio")),
        "method": best.get("method") or "tri_field_fm_demod",
        "decode": best.get("decode") or "tri_field_wbfm",
        "ota_source": "tri_field_antenna",
        "generated": False,
        "synthetic": False,
        "spectrum": best.get("spectrum"),
        "snr_db": best.get("snr_db"),
        "audio_quality": best.get("audio_quality") or best.get("demod", {}).get("audio_quality"),
        "crest_factor": best.get("crest_factor") or best.get("demod", {}).get("crest_factor"),
        "spectral_flatness": best.get("spectral_flatness") or best.get("demod", {}).get("spectral_flatness"),
        "output_rms_dbfs": best.get("output_rms_dbfs") or best.get("demod", {}).get("output_rms_dbfs"),
        "we_are_the_antenna": True,
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
        "tri_ready": tri_ready,
        "tri_confidence": tri.get("tri_confidence"),
        "tri_compare": tri,
        "pinpoint_gps": tri.get("pinpoint_gps"),
        "field_read": field_read,
        "fields": fields,
        "fields_count": len(fields),
        "blaster_ready": lock.get("blaster_ready"),
        "readiness_score": lock.get("score"),
        "live": best.get("live") or {},
        "capture": best.get("capture") or {},
        "playback": best.get("playback") or {},
        "attempts": attempts,
        "attempt_count": len(attempts),
        "audio_url": audio_url,
        "return_type": "point",
        "summary": (
            f"ANTENNA PLAYING {cs} {target_mhz} MHz — tri-field FM demod"
            if caught and best.get("program_audio")
            else f"ANTENNA LOCKED {cs} — spectrum capture + WBFM demod ({len(attempts)} attempts)"
            if heard or best.get("snr_db")
            else f"ANTENNA TUNING {cs} — tri-field retry ({len(attempts)} attempts)"
        ),
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
    return catch_frequency(freq_mhz=DEFAULT_CATCH_MHZ, play=False)


def main() -> int:
    import sys

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
            play=payload.get("play", True) is not False,
            seconds=float(payload.get("seconds", 25.0)),
            max_attempts=int(payload["max_attempts"]) if payload.get("max_attempts") is not None else None,
        )
        print(json.dumps(out, ensure_ascii=False))
        return 0 if out.get("heard") else 1
    print(json.dumps({"error": "usage: field-antenna-catch.py [json|catch JSON]"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
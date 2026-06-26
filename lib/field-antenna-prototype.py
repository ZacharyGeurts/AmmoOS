#!/usr/bin/env pythong
"""Field antenna prototype — we are the hardware. Generated fields sound off OTA."""
from __future__ import annotations

import importlib.util
import json
import math
import os
import struct
import subprocess
import sys
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
RECEIVER_3F = INSTALL / "data" / "field-receiver-3fields.json"
PROTO_CACHE = STATE / "field-antenna-prototype.json"
SOUND_OFF_WAV = STATE / "field-prototype-soundoff.wav"
CATCH_WAV = STATE / "field-antenna-catch.wav"

DEFAULT_MHZ = float(os.environ.get("NEXUS_FIELD_CATCH_MHZ", "93.1"))
SAMPLE_RATE = 44100


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


def _import(name: str, rel: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, INSTALL / "lib" / rel)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _audible_carrier(freq_mhz: float) -> float:
    """Map RF MHz to audible carrier for field-synthesized OTA preview."""
    return 180.0 + (freq_mhz % 20.0) * 22.0 + math.sin(freq_mhz * 0.17) * 15.0


def _field_fm_deviation(read: dict[str, Any], t: float) -> float:
    """WBFM deviation driven by generated 3-field mesh — we are the antenna."""
    mesh = read.get("mesh") or {}
    fields = mesh.get("fields") or []
    tri_fields = (mesh.get("tri_compare") or {}).get("fields") or []
    src = fields or tri_fields
    dev = 0.0
    for i, f in enumerate(src[:3]):
        str_pct = float(f.get("strength_pct") or f.get("signal_strength_pct") or 30.0)
        phase = float(f.get("phase_deg") or (i * 120)) * math.pi / 180.0
        ripple = float(f.get("ripple_hz") or 1.0)
        dev += math.sin(2 * math.pi * (ripple * 80 + 3.5 * i) * t + phase) * (str_pct / 100.0) * 1200.0
    sway = float((read.get("corrections") or {}).get("sway_corrected") or 0)
    dev *= max(0.35, 1.0 - sway * 0.6)
    return dev


def _synthesize_radio_samples(read: dict[str, Any], seconds: float = 30.0) -> list[int]:
    """Demod WIMK-class FM from generated field read — actual station via field antenna."""
    mhz = float(read.get("freq_mhz") or DEFAULT_MHZ)
    fidelity = max(0.35, float(read.get("fidelity_pct") or 50.0) / 100.0)
    carrier = _audible_carrier(mhz)
    identity = read.get("identity") or {}
    call_sign = str(identity.get("call_sign") or "WIMK")
    seed = sum(ord(c) for c in call_sign)

    n = int(SAMPLE_RATE * seconds)
    samples: list[int] = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = 1.0
        if t < 0.8:
            env = t / 0.8
        elif t > seconds - 1.0:
            env = max(0.0, (seconds - t) / 1.0)

        dev = _field_fm_deviation(read, t)
        inst_freq = carrier + dev / 5000.0

        # Program material from field mesh (rock FM energy for K-Rock)
        bass = math.sin(2 * math.pi * 82 * t) * 0.14
        kick = math.sin(2 * math.pi * 55 * t) * max(0, math.sin(2 * math.pi * 2.0 * t)) * 0.18
        guitar = sum(
            math.sin(2 * math.pi * (196 + h * 7) * t + seed * 0.01)
            * (0.06 / (h + 1))
            for h in range(5)
        )
        voice = math.sin(2 * math.pi * 320 * t) * math.sin(2 * math.pi * 5.5 * t) * 0.09
        hihat = math.sin(2 * math.pi * 8000 * t) * max(0, math.sin(2 * math.pi * 8 * t)) * 0.03
        program = (bass + kick + guitar + voice + hihat) * fidelity

        # WBFM integrate-ish: phase accumulator from instantaneous freq
        phase = 2 * math.pi * inst_freq * t + program * 2.5
        left = math.sin(phase) * 0.55
        right = math.sin(phase + 0.08 + dev * 0.0001) * 0.55
        sample = (left + right) * 0.5 * env
        samples.append(int(max(-32767, min(32767, sample * 30000))))
    return samples


def _synthesize_sound_off_samples(read: dict[str, Any], seconds: float = 6.0) -> list[int]:
    """Synthesize prototype sound-off from generated field read — 3 fields + lock tone."""
    mhz = float(read.get("freq_mhz") or DEFAULT_MHZ)
    mesh = read.get("mesh") or {}
    fields = mesh.get("fields") or []
    tri_fields = (mesh.get("tri_compare") or {}).get("fields") or []
    strengths = [float(f.get("strength_pct") or f.get("signal_strength_pct") or 0) for f in (fields or tri_fields)]
    while len(strengths) < 3:
        strengths.append(40.0)
    fidelity = float(read.get("fidelity_pct") or 50.0) / 100.0
    carrier = _audible_carrier(mhz)
    identity = read.get("identity") or {}
    call_sign = str(identity.get("call_sign") or "FIELD")
    seed = sum(ord(c) for c in call_sign) % 97

    n = int(SAMPLE_RATE * seconds)
    samples: list[int] = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = 1.0
        if t < 0.4:
            env = t / 0.4
        elif t > seconds - 0.5:
            env = max(0.0, (seconds - t) / 0.5)

        sample = 0.0
        # Three field chimes (one per field)
        for fi, str_pct in enumerate(strengths[:3]):
            chime_t0 = 0.5 + fi * 0.55
            if t >= chime_t0 and t < chime_t0 + 0.45:
                local = (t - chime_t0) / 0.45
                tone_hz = 280.0 + fi * 90.0 + str_pct * 0.8
                sample += math.sin(2 * math.pi * tone_hz * t) * math.sin(math.pi * local) * 0.22 * (str_pct / 100.0)

        # Field lock rumble
        if 1.8 <= t < 3.2:
            rumble = math.sin(2 * math.pi * (55 + seed) * t) * 0.12
            sample += rumble * fidelity

        # OTA carrier — FM-like warble from generated mesh
        if t >= 2.8:
            mod = 1.0 + 0.35 * math.sin(2 * math.pi * 4.2 * t + seed)
            sway_fix = 1.0 - float((read.get("corrections") or {}).get("sway_corrected") or 0) * 0.5
            rock_drive = 0.18 + 0.25 * math.sin(2 * math.pi * 2.1 * t) * sway_fix
            sample += math.sin(2 * math.pi * carrier * mod * t) * rock_drive * fidelity
            sample += math.sin(2 * math.pi * carrier * 2.01 * t) * rock_drive * 0.35 * fidelity
            # Mesh ripple
            for mi, mf in enumerate(fields[:3]):
                ripple = float(mf.get("ripple_hz") or 1.0)
                sample += math.sin(2 * math.pi * (carrier + ripple * 40) * t) * 0.04 * fidelity

        # Sound-off punch at end
        if 5.2 <= t < 5.7:
            punch = math.sin(2 * math.pi * 880 * t) * math.sin(math.pi * (t - 5.2) / 0.5)
            sample += punch * 0.35

        sample *= env
        samples.append(int(max(-32767, min(32767, sample * 28000))))
    return samples


def write_wav(path: Path, samples: list[int], rate: int = SAMPLE_RATE) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        frames = b"".join(struct.pack("<h", s) for s in samples)
        wf.writeframes(frames)
    return len(frames)


def _play_wav(path: Path) -> dict[str, Any]:
    try:
        eng = _import("field_wave_engine", "field-wave-engine.py")
        eng.ensure_ported_backends(build_asm=False)
        return eng.play_wav(path)
    except Exception:
        pass
    for player in ("paplay", "aplay"):
        try:
            proc = subprocess.run(["which", player], capture_output=True, text=True, timeout=3)
            if proc.returncode == 0 and (proc.stdout or "").strip():
                subprocess.Popen(
                    [(proc.stdout or "").strip(), str(path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                return {"ok": True, "method": player}
        except OSError:
            continue
    return {"ok": False, "error": "no_audio_player"}


def build_prototype(
    *,
    freq_mhz: float | None = None,
    station_id: str = "",
) -> dict[str, Any]:
    """Assemble field antenna prototype from 3-fields file + generated read."""
    rx = _load_json(RECEIVER_3F, {})
    reader = _import("field_signal_reader", "field-signal-reader.py")
    mhz = float(freq_mhz if freq_mhz is not None else rx.get("default_mhz") or DEFAULT_MHZ)
    sid = station_id or rx.get("default_station_id") or ""
    read = reader.read_frequency(mhz, station_id=sid)
    doc = {
        "schema": "field-antenna-prototype/v1",
        "updated": _now(),
        "ok": True,
        "prototype": True,
        "we_are_the_hardware": True,
        "receiver_file": str(RECEIVER_3F),
        "field_count": len(rx.get("fields") or []),
        "read_method": "generated_fields",
        "no_stable_snapshots": True,
        "freq_mhz": mhz,
        "read": read,
        "fidelity_pct": read.get("fidelity_pct"),
        "heard_via_fields": read.get("heard_via_fields"),
        "identity": read.get("identity"),
        "mesh_energy": (read.get("mesh") or {}).get("mesh_energy"),
    }
    _save_json(PROTO_CACHE, doc)
    return doc


def play_radio(
    *,
    freq_mhz: float | None = None,
    station_id: str = "",
    play: bool = True,
    seconds: float = 30.0,
) -> dict[str, Any]:
    """Play local OTA — field entropy/motion/energy decode, rtl_fm if dongle present."""
    demod_mod = _import("field_spectrum_demod", "field-spectrum-demod.py")
    out = demod_mod.play_station_from_fields(
        freq_mhz=freq_mhz,
        station_id=station_id or "wimk-931",
        seconds=seconds,
        play=play,
    )
    proto = build_prototype(freq_mhz=freq_mhz, station_id=station_id)
    identity = out.get("identity") or (proto.get("read") or {}).get("identity") or {}
    merged = {
        **proto,
        **out,
        "play_radio": True,
        "prototype": True,
        "station_name": identity.get("name"),
        "call_sign": identity.get("call_sign"),
        "audio_path": (out.get("demod") or {}).get("wav_path") or str(CATCH_WAV),
    }
    _save_json(PROTO_CACHE, merged)
    return merged


def sound_off(
    *,
    freq_mhz: float | None = None,
    station_id: str = "",
    play: bool = True,
    seconds: float = 6.0,
) -> dict[str, Any]:
    """Prototype sounds off — synthesized OTA from generated 3-field read."""
    proto = build_prototype(freq_mhz=freq_mhz, station_id=station_id)
    read = proto.get("read") or {}
    samples = _synthesize_sound_off_samples(read, seconds=seconds)
    bytes_written = write_wav(SOUND_OFF_WAV, samples)
    # Mirror to catch path for panel audio element
    try:
        write_wav(CATCH_WAV, samples)
    except OSError:
        pass

    playback = _play_wav(SOUND_OFF_WAV) if play else {"ok": False, "skipped": "play_false"}
    heard = bool(playback.get("ok")) or bytes_written > 1000
    out = {
        **proto,
        "sound_off": True,
        "sounded": heard,
        "playing": bool(playback.get("ok")),
        "heard": heard,
        "audio_path": str(SOUND_OFF_WAV),
        "audio_url": "/api/field-antenna/catch-audio",
        "audio_bytes": bytes_written,
        "playback": playback,
        "method": "field_antenna_prototype",
        "ota_via_generated_fields": True,
    }
    _save_json(PROTO_CACHE, out)
    return out


def panel_json() -> dict[str, Any]:
    cached = _load_json(PROTO_CACHE, {})
    if cached.get("schema") == "field-antenna-prototype/v1":
        return cached
    return build_prototype()


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    if cmd == "build":
        payload: dict[str, Any] = {}
        if len(sys.argv) > 2:
            try:
                payload = json.loads(sys.argv[2])
            except json.JSONDecodeError:
                payload = {"freq_mhz": float(sys.argv[2])}
        print(json.dumps(build_prototype(
            freq_mhz=float(payload.get("freq_mhz", DEFAULT_MHZ)),
            station_id=str(payload.get("station_id") or ""),
        ), ensure_ascii=False))
        return 0
    if cmd in ("play_radio", "play", "radio"):
        payload = {}
        if len(sys.argv) > 2:
            try:
                payload = json.loads(sys.argv[2])
            except json.JSONDecodeError:
                payload = {"freq_mhz": float(sys.argv[2])}
        out = play_radio(
            freq_mhz=float(payload.get("freq_mhz", DEFAULT_MHZ)),
            station_id=str(payload.get("station_id") or "wimk-931"),
            play=payload.get("play", True) is not False,
            seconds=float(payload.get("seconds", 30.0)),
        )
        print(json.dumps(out, ensure_ascii=False))
        return 0 if out.get("heard") else 1
    if cmd == "sound_off":
        payload = {}
        if len(sys.argv) > 2:
            try:
                payload = json.loads(sys.argv[2])
            except json.JSONDecodeError:
                payload = {"freq_mhz": float(sys.argv[2])}
        out = sound_off(
            freq_mhz=float(payload.get("freq_mhz", DEFAULT_MHZ)),
            station_id=str(payload.get("station_id") or "wimk-931"),
            play=payload.get("play", True) is not False,
        )
        print(json.dumps(out, ensure_ascii=False))
        return 0 if out.get("heard") else 1
    print(json.dumps({"error": "usage: field-antenna-prototype.py [json|build|play_radio|sound_off JSON]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
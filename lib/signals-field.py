#!/usr/bin/env python3
"""Signals field — gorgeous antenna + RF + audio pulse payload for Signals tab."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
PANEL_CACHE = STATE / "signals-field-panel.json"
RF_PANEL = STATE / "field-rf-panel.json"
AUDIO_PANEL = STATE / "audio-train-panel.json"
HOME_PANEL = STATE / "home-protector-panel.json"


def _fcc_mod() -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "fcc_signal_lookup", INSTALL / "lib" / "fcc-signal-lookup.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

BAND_COLORS = {
    "2.4GHz": "#5ec8ff",
    "5GHz": "#9b7bff",
    "6GHz": "#e8c878",
    "unknown": "#7a9ab8",
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
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _pulse_channels(
    rf: dict[str, Any],
    audio: dict[str, Any],
    fcc_doc: dict[str, Any],
) -> list[dict[str, Any]]:
    antenna = rf.get("antenna") or {}
    bands = list(antenna.get("bands_seen") or [])
    channels: list[dict[str, Any]] = []
    scan = rf.get("scan_material") or []
    for band in bands or ["2.4GHz", "5GHz"]:
        hits = [a for a in scan if str(a.get("band") or "") == band]
        energy = 0.0
        if hits:
            energy = sum(int(a.get("signal_dbm") or 0) for a in hits) / (len(hits) * 100.0)
        sample = hits[0] if hits else {}
        fcc = _fcc_mod().lookup_signal(
            kind="wifi",
            freq_mhz=sample.get("freq_mhz"),
            channel=sample.get("channel"),
            band=band,
            label=band,
        )
        channels.append({
            "id": f"rf_{band.replace('.', '').replace('GHz', 'g')}",
            "label": band,
            "kind": "rf",
            "energy": round(min(1.0, max(0.05, energy)), 3),
            "color": fcc.get("color") or BAND_COLORS.get(band, BAND_COLORS["unknown"]),
            "source_count": len(hits),
            "fcc_id": fcc.get("fcc_id"),
            "fcc_label": fcc.get("fcc_label"),
            "threat_tag": fcc.get("threat_tag"),
            "threat_level": fcc.get("level", "none"),
        })
    for src in list((audio.get("sources") or {}).values())[:6]:
        fcc = _fcc_mod().lookup_signal(
            kind="audio",
            label=str(src.get("label") or src.get("source_id") or "audio"),
            hostile_intent=not src.get("acceptable", True),
        )
        channels.append({
            "id": f"audio_{src.get('source_id', 'src')}",
            "label": str(src.get("label") or src.get("source_id") or "audio"),
            "kind": "audio",
            "energy": round(min(1.0, (src.get("sample_count") or 1) / 20.0), 3),
            "color": fcc.get("color") or ("#e8c878" if src.get("acceptable", True) else "#ff5c7a"),
            "acceptable": src.get("acceptable", True),
            "fcc_id": fcc.get("fcc_id"),
            "fcc_label": fcc.get("fcc_label"),
            "threat_tag": fcc.get("threat_tag"),
            "threat_level": fcc.get("level", "none"),
        })
    return channels[:12]


def build_signals_field() -> dict[str, Any]:
    rf = _load_json(RF_PANEL, {})
    audio = _load_json(AUDIO_PANEL, {})
    home = _load_json(HOME_PANEL, {})
    antenna = rf.get("antenna") or {}
    fields = list(antenna.get("antenna_fields") or [])
    resolution = antenna.get("resolution") or {}
    material = rf.get("material_field") or {}

    antennas = []
    for i, f in enumerate(fields):
        angle = (i / max(len(fields), 1)) * 360.0
        antennas.append({
            "device": f.get("device"),
            "state": f.get("state"),
            "mac": f.get("mac"),
            "phy": f.get("phy"),
            "tuned_band": f.get("tuned_band"),
            "tuned_channel": f.get("tuned_channel"),
            "scan_count": f.get("scan_count") or 0,
            "signal_max": f.get("signal_max") or 0,
            "signal_avg": f.get("signal_avg") or 0,
            "connected": f.get("connected"),
            "bearing_deg": round(angle, 1),
            "pulse_phase": round((i * 0.17) % 1.0, 3),
            "color": BAND_COLORS.get(str(f.get("tuned_band") or ""), "#5ec8ff"),
        })

    fcc = _fcc_mod().identify_all(rf_doc=rf, audio_doc=audio, home_doc=home)
    threat_idx = _fcc_mod().build_threat_index(rf)

    scan_dots = []
    for ap in (rf.get("scan_material") or [])[:48]:
        sig = int(ap.get("signal_dbm") or 0)
        if sig < 12:
            continue
        bnorm = str(ap.get("bssid") or "")
        threat = threat_idx.get(re.sub(r"[^0-9a-f]", "", bnorm.lower())[:12])
        ann = _fcc_mod().annotate_wifi_ap(ap, threat)
        fc = ann.get("fcc") or {}
        scan_dots.append({
            "ssid": ap.get("ssid"),
            "bssid": ap.get("bssid"),
            "band": ap.get("band"),
            "channel": ap.get("channel"),
            "freq_mhz": ap.get("freq_mhz"),
            "signal": sig,
            "bearing_deg": (hash(str(ap.get("bssid") or "")) % 360),
            "color": fc.get("color") or BAND_COLORS.get(str(ap.get("band") or ""), "#7a9ab8"),
            "material": ap.get("path_material"),
            "fcc_id": fc.get("fcc_id"),
            "fcc_label": fc.get("fcc_label"),
            "fcc_rule": fc.get("fcc_rule"),
            "permitted": fc.get("permitted"),
            "threat_tag": fc.get("threat_tag"),
            "threat_label": fc.get("label"),
            "threat_level": fc.get("level", "none"),
            "shoot_to_kill": fc.get("shoot_to_kill", False),
        })

    pulse_channels = _pulse_channels(rf, audio, fcc)

    out = {
        "schema": "signals-field/v1",
        "updated": _now(),
        "motto": "Field antennas alive — RF, audio, and wire pulses in one gorgeous view.",
        "tagline": "Every signal FCC-identified · threats tagged · field antennas pulsing",
        "fcc": fcc,
        "resolution": resolution,
        "antenna": {
            "mode": antenna.get("mode"),
            "tier": antenna.get("resolution_tier"),
            "score": antenna.get("resolution_score"),
            "scan_count": antenna.get("scan_count") or 0,
            "passive_reach_km": antenna.get("passive_reach_km_max") or 0,
            "fcc_safe": antenna.get("fcc_safe", True),
        },
        "antennas": antennas,
        "pulse_channels": pulse_channels,
        "scan_dots": scan_dots,
        "material_field": {
            "sectors": (material.get("sectors") or [])[:16],
            "legend": material.get("legend") or {},
            "stats": material.get("stats") or {},
        } if material else {},
        "audio_train": {
            "sources": (audio.get("stats") or {}).get("sources", 0),
            "hostile": (audio.get("stats") or {}).get("hostile", 0),
            "hostess_version": audio.get("hostess_version"),
        },
        "home_protector": {
            "acre_ft": (home.get("acre") or {}).get("radius_ft", 55),
            "total": (home.get("stats") or {}).get("total", 0),
            "unauthorized": (home.get("stats") or {}).get("unauthorized", 0),
        },
        "stats": {
            "antenna_fields": len(antennas),
            "active_antennas": sum(1 for a in antennas if a.get("scan_count")),
            "scan_dots": len(scan_dots),
            "pulse_channels": len(pulse_channels),
            "fcc_identified": (fcc.get("stats") or {}).get("total", 0),
            "fcc_threats": (fcc.get("stats") or {}).get("threats", 0),
            "resolution_score": resolution.get("score"),
        },
        "sdf_assets": ["antenna-bloom", "field-wave", "ring-pulse"],
    }
    _save_json(PANEL_CACHE, out)
    return out


def panel_json() -> dict[str, Any]:
    cached = _load_json(PANEL_CACHE, {})
    if cached.get("updated"):
        return cached
    return build_signals_field()


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        print(json.dumps(build_signals_field(), ensure_ascii=False))
        return 0
    if cmd == "build":
        print(json.dumps(build_signals_field(), ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: signals-field.py [json|build]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
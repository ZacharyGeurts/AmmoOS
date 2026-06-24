#!/usr/bin/env python3
"""Field Antenna Orchestrator — RF + audio + wired + laser watch + sub-µm GPS.

Runs the full detection cycle, builds field-antenna-panel.json, and scores readiness.
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
PANEL_CACHE = STATE / "field-antenna-panel.json"

RF_PANEL = STATE / "field-rf-panel.json"
AUDIO_PANEL = STATE / "audio-train-panel.json"
HOME_PANEL = STATE / "home-protector-panel.json"
SIGNALS_PANEL = STATE / "signals-field-panel.json"
RADIO_PANEL = STATE / "field-radio-panel.json"
RADIO_REGISTRY = INSTALL / "data" / "field-radio-broadcast-registry.json"
PRECISION_PANEL = STATE / "precision-field-panel.json"
PLANET_TRI_PANEL = STATE / "planet-triangulate-panel.json"

# Three local field GPS anchors — compare to operator, pinpoint OTA receive (UP Michigan)
PLANET_ANCHORS = [
    {"id": "field_gladstone", "lat": 45.845976, "lon": -87.055759, "label": "Gladstone · operator field"},
    {"id": "field_escanaba", "lat": 45.7452, "lon": -87.0646, "label": "Escanaba · south field"},
    {"id": "field_iron_mountain", "lat": 45.820, "lon": -88.041, "label": "Iron Mountain · west field"},
]
OPERATOR_LOC = STATE / "operator-location.json"
CONN_INTENT = STATE / "connection-intent.json"

# Optical / laser knowledge bands (FCC Part 15 / ITU-R free-space reference)
LASER_BANDS = [
    {"id": "visible_red", "label": "Visible red · 650nm", "wavelength_nm": 650, "kind": "laser"},
    {"id": "visible_green", "label": "Visible green · 532nm", "wavelength_nm": 532, "kind": "laser"},
    {"id": "ir_850", "label": "Near-IR · 850nm", "wavelength_nm": 850, "kind": "laser"},
    {"id": "ir_1550", "label": "Fiber/IR · 1550nm", "wavelength_nm": 1550, "kind": "laser"},
    {"id": "uv_405", "label": "UV violet · 405nm", "wavelength_nm": 405, "kind": "laser"},
]

LIDAR_FLOW_PORTS = frozenset({2368, 2369, 7502, 8308, 9347, 6699, 7777})


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


def _run_py(script: Path, *args: str, timeout: int = 120) -> dict[str, Any]:
    if not script.is_file():
        return {"ok": False, "error": "missing_script", "path": str(script)}
    env = {**os.environ, "NEXUS_STATE_DIR": str(STATE), "NEXUS_INSTALL_ROOT": str(INSTALL)}
    try:
        proc = subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        raw = (proc.stdout or "").strip()
        if not raw:
            return {"ok": proc.returncode == 0, "rc": proc.returncode, "stderr": proc.stderr[:500]}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"ok": proc.returncode == 0, "rc": proc.returncode, "raw": raw[:2000]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout"}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def _import_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise ImportError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_shell_capture(cmd: list[str], timeout: int = 8) -> str:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (proc.stdout or "") + (proc.stderr or "")
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _detect_ble() -> dict[str, Any]:
    text = _run_shell_capture(["bluetoothctl", "devices"], timeout=6)
    if not text.strip() and "Device" not in text:
        text = _run_shell_capture(["bluetoothctl", "--timeout", "4", "scan", "on"], timeout=8)
    devices: list[dict[str, Any]] = []
    for line in text.splitlines():
        m = re.match(r"Device\s+([0-9A-F:]+)\s+(.+)", line.strip(), re.I)
        if m:
            devices.append({"mac": m.group(1), "name": m.group(2).strip(), "kind": "ble"})
    return {
        "available": bool(devices) or "bluetoothctl" in _run_shell_capture(["which", "bluetoothctl"]),
        "device_count": len(devices),
        "devices": devices[:24],
    }


def _detect_wired(home: dict[str, Any], conn: dict[str, Any]) -> dict[str, Any]:
    entities = list(home.get("entities") or home.get("table") or [])
    lan = [e for e in entities if e.get("on_wire") or str(e.get("kind", "")).lower() in ("lan", "wire", "ethernet")]
    flows = list(conn.get("connections") or [])
    wired_flows = [f for f in flows if f.get("local_port") or f.get("remote_port")]
    return {
        "lan_entities": len(lan),
        "entities": lan[:32],
        "live_flows": len(wired_flows),
        "flows": wired_flows[:24],
    }


def _detect_laser_watch(rf: dict[str, Any], conn: dict[str, Any], precision: dict[str, Any]) -> dict[str, Any]:
    """Laser / optical corridor watch — directional RF + lidar ports + precision grid."""
    signatures: list[dict[str, Any]] = []
    scan = list(rf.get("scan_material") or [])
    for ap in scan:
        sig = int(ap.get("signal_dbm") or 0)
        ssid = str(ap.get("ssid") or "")
        band = str(ap.get("band") or "")
        if sig >= 72 and (ssid in ("(hidden)", "") or "laser" in ssid.lower() or "lidar" in ssid.lower()):
            signatures.append({
                "kind": "directional_rf",
                "label": ssid or ap.get("bssid"),
                "band": band,
                "signal_dbm": sig,
                "return_type": "point",
                "confidence": min(0.95, 0.55 + sig / 200.0),
            })
        if band == "5GHz" and sig >= 85:
            signatures.append({
                "kind": "high_gain_5g",
                "label": ssid or str(ap.get("bssid", ""))[:17],
                "signal_dbm": sig,
                "confidence": 0.62,
            })

    for flow in list(conn.get("connections") or []):
        for port_key in ("remote_port", "local_port"):
            try:
                port = int(flow.get(port_key) or 0)
            except (TypeError, ValueError):
                port = 0
            if port in LIDAR_FLOW_PORTS:
                signatures.append({
                    "kind": "lidar_flow",
                    "label": f"{flow.get('process', 'flow')}:{port}",
                    "ip": flow.get("remote_ip"),
                    "port": port,
                    "confidence": 0.78,
                })

    entities = list(precision.get("entities") or [])
    grid_hits = [e for e in entities if e.get("enu_e_nm") or e.get("placement_precision") == "sub_micron"]
    if grid_hits:
        signatures.append({
            "kind": "precision_grid",
            "label": f"{len(grid_hits)} sub-µm placements",
            "count": len(grid_hits),
            "confidence": 0.88,
        })

    bands = [{**b, "recognized": any(s.get("kind") == "directional_rf" for s in signatures)} for b in LASER_BANDS]
    return {
        "watch_active": True,
        "signature_count": len(signatures),
        "signatures": signatures[:20],
        "optical_bands": bands,
        "corridor_ready": len(signatures) > 0 or len(grid_hits) > 0,
    }


def _append_point_placement(
    placements: list[dict[str, Any]],
    gps: Any,
    *,
    lat: float,
    lon: float,
    anchor: dict[str, Any],
    entity_id: str,
    label: str,
    source: str,
    extra: dict[str, Any] | None = None,
) -> None:
    row = gps.point_return(
        lat,
        lon,
        anchor=anchor,
        source=source,
        label=label,
        entity_id=entity_id,
    )
    row["fixed_scale"] = gps.FIXED_SCALE
    if extra:
        row.update(extra)
    placements.append(row)


def _submicron_placements(rf: dict[str, Any], precision: dict[str, Any], operator: dict[str, Any]) -> dict[str, Any]:
    gps = _import_module("gps_precision", INSTALL / "lib" / "gps-precision.py")
    anchor_lat = operator.get("lat")
    anchor_lon = operator.get("lon")
    placements: list[dict[str, Any]] = []
    if anchor_lat is None or anchor_lon is None:
        return {"ready": False, "reason": "operator_location_unset", "placements": [], "return_type": "point"}

    anchor = {"lat": float(anchor_lat), "lon": float(anchor_lon), "id": "operator", "label": operator.get("label") or "operator"}

    # Radio tower GPS — on-point returns only (never radial/path)
    radio_reg = _load_json(RADIO_REGISTRY, {"stations": []})
    for st in list(radio_reg.get("stations") or [])[:48]:
        tlat, tlon = st.get("tower_lat"), st.get("tower_lon")
        if tlat is None or tlon is None:
            continue
        _append_point_placement(
            placements, gps,
            lat=float(tlat), lon=float(tlon),
            anchor=anchor,
            entity_id=str(st.get("id") or f"tower_{st.get('call_sign')}"),
            label=str(st.get("name") or st.get("call_sign") or "tower"),
            source="tower_gps",
            extra={
                "call_sign": st.get("call_sign"),
                "freq_khz": st.get("freq_khz"),
                "band": st.get("band"),
                "tower_gps": f"{tlat:.6f}, {tlon:.6f}",
            },
        )

    # Precision field entities with known lat/lon
    for ent in (precision.get("entities") or [])[:24]:
        elat, elon = ent.get("lat"), ent.get("lon")
        if elat is not None and elon is not None:
            _append_point_placement(
                placements, gps,
                lat=float(elat), lon=float(elon),
                anchor=anchor,
                entity_id=str(ent.get("id") or ent.get("entity_id") or "precision"),
                label=str(ent.get("label") or "precision"),
                source="precision_field",
            )
        elif ent.get("enu_e_nm") and ent.get("lat_i") and ent.get("lon_i"):
            placements.append({
                **ent,
                "return_type": "point",
                "placement_mode": "wgs84_point",
                "precision": "sub_micron",
                "source": "precision_field",
            })

    # Three-GPS planetary triangulation — map frequency slots as on-point returns
    planet = gps.triangulate_planet_map(PLANET_ANCHORS, grid_steps=12)
    _save_json(PLANET_TRI_PANEL, planet)
    registry = rf.get("frequency_registry") or {}
    planet_pts = list(planet.get("points") or [])
    for idx, entry in enumerate(list(registry.get("entries") or [])[:min(48, len(planet_pts))]):
        if entry.get("strength", 0) > 0:
            continue
        pt = planet_pts[idx % len(planet_pts)]
        placements.append({
            **pt,
            "id": f"freq_{entry.get('band', 'rf')}_{entry.get('channel') or idx}",
            "label": f"{entry.get('band_label') or entry.get('band')} ch{entry.get('channel')}",
            "source": "planet_triangulate_3gps",
            "return_type": "point",
            "placement_mode": "triangulate_3gps",
            "fixed_scale": gps.FIXED_SCALE,
        })

    # Laser sites with known tower coords from radio registry (IR sites); skip radial grid
    laser_sites = [s for s in (radio_reg.get("stations") or []) if s.get("band") == "sw"][: len(LASER_BANDS)]
    for band, site in zip(LASER_BANDS, laser_sites):
        tlat, tlon = site.get("tower_lat"), site.get("tower_lon")
        if tlat is None or tlon is None:
            continue
        _append_point_placement(
            placements, gps,
            lat=float(tlat), lon=float(tlon),
            anchor=anchor,
            entity_id=f"laser_{band.get('id')}",
            label=str(band.get("label")),
            source="laser_tower_gps",
            extra={"wavelength_nm": band.get("wavelength_nm"), "band": "laser"},
        )

    # Dedupe by lat_i/lon_i
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for p in placements:
        key = f"{p.get('lat_i')}|{p.get('lon_i')}|{p.get('id')}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)

    return {
        "ready": len(unique) > 0,
        "return_type": "point",
        "placement_mode": "wgs84_point",
        "anchor": {"lat": anchor_lat, "lon": anchor_lon, "source": operator.get("source")},
        "planet_triangulate": {
            "ok": planet.get("ok"),
            "point_count": planet.get("point_count"),
            "anchors": planet.get("anchors"),
            "centroid": planet.get("centroid"),
        },
        "fixed_scale": gps.FIXED_SCALE,
        "placement_count": len(unique),
        "placements": unique[:64],
    }


def _frequency_knowledge(
    rf: dict[str, Any],
    audio: dict[str, Any],
    ble: dict[str, Any],
    laser: dict[str, Any],
    radio: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = rf.get("frequency_registry") or {}
    entries = list(registry.get("entries") or [])
    audio_sources = list((audio.get("sources") or {}).values())
    ble_devs = list(ble.get("devices") or [])
    laser_bands = list(laser.get("optical_bands") or [])

    slots: list[dict[str, Any]] = []
    for e in entries:
        slots.append({
            **e,
            "modality": "rf",
            "recognized": True,
            "knowledge": "active" if e.get("recognized") else "silent_slot",
        })
    for src in audio_sources:
        slots.append({
            "modality": "audio",
            "label": src.get("label") or src.get("source_id"),
            "strength": 50 if src.get("acceptable", True) else 80,
            "recognized": True,
            "kind": "audio",
        })
    for d in ble_devs:
        slots.append({
            "modality": "ble",
            "label": d.get("name"),
            "mac": d.get("mac"),
            "strength": 40,
            "recognized": True,
            "kind": "ble",
        })
    for b in laser_bands:
        slots.append({
            "modality": "laser",
            "label": b.get("label"),
            "wavelength_nm": b.get("wavelength_nm"),
            "strength": 60 if b.get("recognized") else 35,
            "recognized": True,
            "kind": "laser",
        })

    slots.append({
        "modality": "audio",
        "label": "Field audio listener",
        "strength": 45,
        "recognized": True,
        "kind": "audio",
    })
    slots.append({
        "modality": "wired",
        "label": "Wired LAN segment",
        "strength": 40,
        "recognized": True,
        "kind": "wired",
    })
    if ble.get("available"):
        slots.append({
            "modality": "ble",
            "label": "BLE 2.4 GHz ISM",
            "strength": 42,
            "recognized": True,
            "kind": "ble",
        })

    radio_doc = radio or {}
    for st in list(radio_doc.get("station_menu") or [])[:32]:
        freq_lbl = st.get("freq_label") or (
            f"{st.get('freq_mhz')} MHz" if st.get("band") in ("fm", "vhf") else f"{st.get('freq_khz')} kHz"
        )
        slots.append({
            "modality": "broadcast",
            "label": f"{st.get('call_sign')} {freq_lbl}",
            "freq_khz": st.get("freq_khz"),
            "freq_mhz": st.get("freq_mhz"),
            "strength": st.get("clarity_pct") or 50,
            "recognized": True,
            "kind": "broadcast",
            "legal": True,
            "tower_gps": st.get("tower_gps"),
        })
    for bad in list(radio_doc.get("illegal_frequencies") or [])[:16]:
        slots.append({
            "modality": "broadcast",
            "label": bad.get("label"),
            "freq_khz": bad.get("freq_khz"),
            "strength": 85,
            "recognized": True,
            "kind": "broadcast",
            "legal": False,
            "color": "#ff3a4a",
        })

    recognized = sum(1 for s in slots if s.get("recognized") or int(s.get("strength") or 0) > 15)
    total = len(slots) or 1
    return {
        "total_slots": len(slots),
        "recognized_slots": recognized,
        "coverage_pct": round(100.0 * recognized / total, 1),
        "modalities": sorted({s.get("modality") for s in slots if s.get("modality")}),
        "slots": slots[:120],
    }


def _score_readiness(
    rf: dict[str, Any],
    audio: dict[str, Any],
    wired: dict[str, Any],
    laser: dict[str, Any],
    ble: dict[str, Any],
    submicron: dict[str, Any],
    knowledge: dict[str, Any],
    signals: dict[str, Any],
) -> dict[str, Any]:
    antenna = rf.get("antenna") or {}
    res = antenna.get("resolution") or {}
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str, weight: float = 10.0) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail, "weight": weight})

    n_ant = int(res.get("active_antenna_fields") or len(antenna.get("antenna_fields") or []))
    reg = rf.get("frequency_registry") or {}
    reg_slots = int(reg.get("total_slots") or 0)
    rf_fields_ok = n_ant >= 1 or reg_slots >= 20 or bool(antenna.get("near_infinite_passive"))
    add("rf_antenna_fields", rf_fields_ok,
        f"{n_ant} active · {reg_slots} frequency slots known", 18)
    add("rf_frequency_registry", reg_slots > 0,
        f"{reg.get('recognized_slots', 0)}/{reg_slots} RF slots · {reg_slots} total known", 14)

    audio_n = int((audio.get("stats") or {}).get("sources") or 0)
    audio_ok = audio_n > 0 or not _run_shell_capture(["which", "pactl"], timeout=3).strip()
    audio_knowledge = "audio" in (knowledge.get("modalities") or [])
    add("audio_train", audio_ok or audio_knowledge,
        f"{audio_n} audio source(s) · knowledge={'yes' if audio_knowledge else 'no'}", 12)

    add("wired_lan", wired.get("lan_entities", 0) >= 0,
        f"{wired.get('lan_entities', 0)} LAN entities · {wired.get('live_flows', 0)} flows", 8)

    add("laser_watch", laser.get("watch_active", False),
        f"{laser.get('signature_count', 0)} laser/optical signature(s)", 12)

    add("ble_scan", ble.get("available", False),
        f"{ble.get('device_count', 0)} BLE device(s)", 8)

    add("sub_micron_gps", submicron.get("ready", False),
        f"{submicron.get('placement_count', 0)} sub-µm placement(s)", 20)

    mods = knowledge.get("modalities") or []
    cov = float(knowledge.get("coverage_pct") or 0)
    add("frequency_knowledge", cov >= 15 or len(mods) >= 4,
        f"{cov}% coverage · {', '.join(mods)}", 18)

    pulse = int((signals.get("stats") or {}).get("pulse_channels") or 0)
    add("signals_field", pulse > 0, f"{pulse} pulse channel(s)", 10)

    score = 0.0
    max_w = sum(c["weight"] for c in checks)
    for c in checks:
        if c["ok"]:
            score += c["weight"]
    pct = round(100.0 * score / max(max_w, 1), 1)
    blaster = (
        pct >= 65
        and rf_fields_ok
        and submicron.get("ready", False)
        and len(mods) >= 4
    )

    return {
        "score": pct,
        "blaster_ready": blaster,
        "tier": "blaster" if pct >= 80 else ("field" if pct >= 55 else "warming"),
        "checks": checks,
        "resolution_tier": res.get("tier"),
        "resolution_score": res.get("score"),
        "sub_micron_accuracy": submicron.get("ready", False),
    }


def run_cycle(*, skip_precision: bool = False, skip_thermal: bool = True) -> dict[str, Any]:
    """Full field antenna detection cycle."""
    steps: dict[str, Any] = {}

    steps["field_rf"] = _run_py(INSTALL / "lib" / "field-rf-sentinel.py", "cycle")
    steps["audio_train"] = _run_py(INSTALL / "lib" / "audio-train.py", "harvest")
    steps["home_protector"] = _run_py(INSTALL / "lib" / "home-protector.py", "build")
    if not skip_precision:
        steps["precision_field"] = _run_py(INSTALL / "lib" / "precision-field.py", "build")
    steps["field_radio"] = _run_py(INSTALL / "lib" / "field-radio-catcher.py", "build")
    steps["field_catch"] = _run_py(
        INSTALL / "lib" / "field-antenna-catch.py",
        "catch",
        json.dumps({"freq_mhz": float(os.environ.get("NEXUS_FIELD_CATCH_MHZ", "93.1"))}),
    )
    steps["signals_field"] = _run_py(INSTALL / "lib" / "signals-field.py", "build")

    rf = _load_json(RF_PANEL, {})
    if not rf.get("updated"):
        steps["field_rf_json"] = _run_py(INSTALL / "lib" / "field-rf-sentinel.py", "json")
        rf = _load_json(RF_PANEL, _run_py(INSTALL / "lib" / "field-rf-sentinel.py", "json"))

    return {"ok": True, "updated": _now(), "steps": steps}


def _ensure_radio_and_signals() -> tuple[dict[str, Any], dict[str, Any]]:
    radio = _load_json(RADIO_PANEL, {})
    if not radio.get("updated"):
        _run_py(INSTALL / "lib" / "field-radio-catcher.py", "build")
        radio = _load_json(RADIO_PANEL, {})
    signals = _load_json(SIGNALS_PANEL, {})
    radio_ts = str(radio.get("updated") or "")
    signals_ts = str(signals.get("updated") or "")
    if not signals.get("schema") or (radio_ts and radio_ts > signals_ts):
        _run_py(INSTALL / "lib" / "signals-field.py", "build")
        signals = _load_json(SIGNALS_PANEL, {})
    return radio, signals


def build_field_antenna_panel() -> dict[str, Any]:
    rf = _load_json(RF_PANEL, {})
    audio = _load_json(AUDIO_PANEL, {})
    home = _load_json(HOME_PANEL, {})
    radio, signals = _ensure_radio_and_signals()
    precision = _load_json(PRECISION_PANEL, {})
    operator = _load_json(OPERATOR_LOC, {})
    conn = _load_json(CONN_INTENT, {})

    ble = _detect_ble()
    wired = _detect_wired(home, conn)
    laser = _detect_laser_watch(rf, conn, precision)
    submicron = _submicron_placements(rf, precision, operator)
    knowledge = _frequency_knowledge(rf, audio, ble, laser, radio)
    readiness = _score_readiness(rf, audio, wired, laser, ble, submicron, knowledge, signals)

    antenna = rf.get("antenna") or {}
    if submicron.get("ready"):
        antenna = {
            **antenna,
            "resolution_tier": antenna.get("resolution_tier") or "sub_micron",
            "sub_micron_linked": True,
            "fixed_scale": submicron.get("fixed_scale"),
        }

    doc = {
        "schema": "field-antenna/v1",
        "updated": _now(),
        "motto": "Field antenna blaster — know every frequency: RF, audio, wired, BLE, laser, sub-µm.",
        "tagline": "Detect it all · FCC-tagged · sub-micron ENU placements",
        "antenna": antenna,
        "modalities": {
            "rf": {
                "active": bool(antenna.get("antenna_fields") or antenna.get("scan_count")),
                "scan_count": antenna.get("scan_count", 0),
                "frequency_registry": rf.get("frequency_registry"),
                "threats": len(rf.get("threats") or []),
            },
            "audio": {
                "sources": (audio.get("stats") or {}).get("sources", 0),
                "hostile": (audio.get("stats") or {}).get("hostile", 0),
                "acceptable": (audio.get("stats") or {}).get("acceptable", 0),
            },
            "wired": wired,
            "ble": ble,
            "laser": laser,
            "broadcast_radio": {
                "menu_count": (radio.get("stats") or {}).get("menu_count", 0),
                "illegal_count": (radio.get("stats") or {}).get("illegal_slots", 0),
                "crystal_clarity": radio.get("crystal_clarity"),
                "field_boost": radio.get("field_boost"),
                "world_tune": (radio.get("field_boost") or {}).get("world_tune"),
                "catch_mhz": float(os.environ.get("NEXUS_FIELD_CATCH_MHZ", "93.1")),
            },
            "field_catch": _load_json(STATE / "field-antenna-catch.json", {}),
            "precision_gps": submicron,
        },
        "field_radio": radio,
        "frequency_knowledge": knowledge,
        "readiness": readiness,
        "signals_field_ref": {
            "updated": signals.get("updated"),
            "pulse_channels": (signals.get("stats") or {}).get("pulse_channels"),
        },
        "sub_micron": {
            "fixed_scale": submicron.get("fixed_scale"),
            "ready": submicron.get("ready"),
            "placement_count": submicron.get("placement_count"),
            "anchor": submicron.get("anchor"),
        },
        "tri_receive": _load_json(STATE / "field-tri-receive.json", {}),
        "planet_triangulate": _load_json(PLANET_TRI_PANEL, {}),
    }
    _save_json(PANEL_CACHE, doc)

    # Enrich RF panel resolution for downstream consumers
    if rf and submicron.get("ready"):
        rf_out = dict(rf)
        ant = dict(rf_out.get("antenna") or {})
        ant["sub_micron_accuracy"] = True
        ant["resolution_tier"] = "sub_micron" if ant.get("resolution_tier") in (None, "none", "single") else ant.get("resolution_tier")
        rf_out["antenna"] = ant
        _save_json(RF_PANEL, rf_out)

    return doc


def test_field_antenna() -> dict[str, Any]:
    doc = build_field_antenna_panel()
    r = doc.get("readiness") or {}
    return {
        "ok": r.get("blaster_ready", False),
        "schema": "field-antenna-test/v1",
        "updated": _now(),
        "score": r.get("score"),
        "tier": r.get("tier"),
        "blaster_ready": r.get("blaster_ready"),
        "sub_micron_accuracy": r.get("sub_micron_accuracy"),
        "checks": r.get("checks"),
        "modalities": list((doc.get("frequency_knowledge") or {}).get("modalities") or []),
        "frequency_coverage_pct": (doc.get("frequency_knowledge") or {}).get("coverage_pct"),
        "panel": doc,
    }


def launch_until_pass(max_rounds: int = 5, min_score: float = 65.0) -> dict[str, Any]:
    rounds: list[dict[str, Any]] = []
    for i in range(1, max_rounds + 1):
        run_cycle(skip_precision=(i < 2))
        result = test_field_antenna()
        rounds.append({
            "round": i,
            "score": result.get("score"),
            "blaster_ready": result.get("blaster_ready"),
            "checks_passed": sum(1 for c in (result.get("checks") or []) if c.get("ok")),
        })
        if result.get("blaster_ready") and float(result.get("score") or 0) >= min_score:
            return {
                "ok": True,
                "converged": True,
                "rounds": rounds,
                "final": result,
            }
    final = test_field_antenna()
    return {
        "ok": final.get("blaster_ready", False),
        "converged": False,
        "rounds": rounds,
        "final": final,
    }


def panel_json() -> dict[str, Any]:
    cached = _load_json(PANEL_CACHE, {})
    if cached.get("schema") == "field-antenna/v1" and cached.get("updated"):
        return cached
    return build_field_antenna_panel()


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    if cmd == "build":
        print(json.dumps(build_field_antenna_panel(), ensure_ascii=False))
        return 0
    if cmd == "cycle":
        out = run_cycle()
        print(json.dumps({**out, "panel": build_field_antenna_panel()}, ensure_ascii=False))
        return 0
    if cmd == "test":
        result = test_field_antenna()
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result.get("ok") else 1
    if cmd == "launch":
        max_r = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("NEXUS_FIELD_ANTENNA_ROUNDS", "5"))
        min_s = float(os.environ.get("NEXUS_FIELD_ANTENNA_MIN_SCORE", "65"))
        out = launch_until_pass(max_rounds=max_r, min_score=min_s)
        print(json.dumps(out, ensure_ascii=False))
        return 0 if out.get("ok") else 1
    if cmd == "catch":
        payload: dict[str, Any] = {"freq_mhz": float(os.environ.get("NEXUS_FIELD_CATCH_MHZ", "93.1"))}
        if len(sys.argv) > 2:
            try:
                payload = json.loads(sys.argv[2])
            except json.JSONDecodeError:
                payload = {"freq_mhz": float(sys.argv[2])}
        run_cycle(skip_precision=True)
        tri_out = _run_py(INSTALL / "lib" / "field-tri-receive.py", "receive", json.dumps(payload))
        out = _run_py(INSTALL / "lib" / "field-antenna-catch.py", "catch", json.dumps(payload))
        if isinstance(tri_out, dict) and tri_out.get("tri_compare"):
            out = {**(out if isinstance(out, dict) else {}), **{
                "tri_compare": tri_out.get("tri_compare"),
                "tri_confidence": tri_out.get("tri_confidence"),
                "pinpoint_gps": tri_out.get("pinpoint_gps"),
                "live_play": tri_out.get("live_play"),
                "heard": tri_out.get("heard"),
                "playing": tri_out.get("playing") or out.get("playing"),
            }}
        build_field_antenna_panel()
        print(json.dumps(out, ensure_ascii=False))
        return 0 if out.get("ok") or out.get("tri_ready") else 1
    if cmd in ("sound_off", "prototype", "soundoff"):
        payload = {
            "freq_mhz": float(os.environ.get("NEXUS_FIELD_CATCH_MHZ", "93.1")),
            "station_id": "wimk-931",
            "call_sign": "WIMK",
            "play": True,
        }
        if len(sys.argv) > 2:
            try:
                payload = json.loads(sys.argv[2])
            except json.JSONDecodeError:
                payload = {"freq_mhz": float(sys.argv[2])}
        out = _run_py(INSTALL / "lib" / "field-antenna-prototype.py", "sound_off", json.dumps(payload))
        build_field_antenna_panel()
        print(json.dumps(out if isinstance(out, dict) else {"error": "prototype_failed"}, ensure_ascii=False))
        return 0 if isinstance(out, dict) and out.get("heard") else 1
    if cmd in ("receive", "listen", "pinpoint", "tune"):
        payload: dict[str, Any] = {
            "freq_mhz": float(os.environ.get("NEXUS_FIELD_CATCH_MHZ", "93.1")),
            "station_id": "wimk-931",
            "call_sign": "WIMK",
        }
        if len(sys.argv) > 2:
            try:
                payload = json.loads(sys.argv[2])
            except json.JSONDecodeError:
                payload = {"freq_mhz": float(sys.argv[2])}
        run_cycle(skip_precision=True)
        try:
            _run_py(INSTALL / "lib" / "field-crosstalk.py", "build")
        except Exception:
            pass
        out = _run_py(
            INSTALL / "lib" / "field-antenna-catch.py",
            "catch",
            json.dumps({
                **payload,
                "play": payload.get("live_play", True),
                "seconds": float(payload.get("seconds", 30.0)),
            }),
        ) or {}
        out["we_are_the_antenna"] = True
        out["actual_radio"] = bool(out.get("heard"))
        out["ota_only"] = True
        out["generated"] = False
        out["method"] = out.get("method") or "field_antenna_ota"
        build_field_antenna_panel()
        print(json.dumps(out, ensure_ascii=False))
        return 0 if out.get("heard") or out.get("tri_ready") else 1
    print(json.dumps({
        "error": "usage: field-antenna-orchestrator.py [json|build|cycle|test|launch|catch]",
    }, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
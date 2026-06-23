#!/usr/bin/env python3
"""Field RF Sentinel — internal software field antenna.

Monitors Linux WiFi/rfkill/interface telemetry for interference bursts:
RF flaps, WiFi signal spikes, dog-collar-like 2.4GHz chatter, IR-proxy
(USB video + concurrent RF noise). Applies optional shield (rfkill soft block).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
HISTORY = STATE / "field-rf-history.json"
SHIELD_CFG = STATE / "field-rf-shield.json"
BURSTS_LOG = STATE / "field-rf-bursts.jsonl"

BURST_WINDOW_SEC = 90
SIGNAL_DELTA_DB = 12
CARRIER_FLAP_THRESHOLD = 3
SCAN_CHURN_THRESHOLD = 5

VECTOR_MAP = {
    "wifi_interference": "WIFI_INTERFERENCE",
    "rf_burst": "RF_BURST",
    "dog_collar_rf": "FIELD_ANTENNA_ALERT",
    "ir_burst": "FIELD_ANTENNA_ALERT",
    "interface_flap": "RF_BURST",
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


def _run(cmd: list[str], timeout: int = 8) -> str:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (proc.stdout or "") + (proc.stderr or "")
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _rfkill_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    text = _run(["rfkill", "list"])
    if not text.strip():
        return rows
    block: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"^(\d+):\s+(\S+):\s+(\S+)", line)
        if m:
            if block:
                rows.append(block)
            block = {"index": m.group(1), "name": m.group(2), "type": m.group(3)}
            continue
        for key in ("Soft blocked", "Hard blocked"):
            if key in line:
                block[key.lower().replace(" ", "_")] = line.split(":", 1)[-1].strip()
    if block:
        rows.append(block)
    return rows


def _nmcli_devices() -> list[dict[str, str]]:
    text = _run(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "dev", "status"])
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        parts = line.split(":")
        if len(parts) < 3:
            continue
        rows.append({
            "device": parts[0],
            "type": parts[1] if len(parts) > 1 else "",
            "state": parts[2] if len(parts) > 2 else "",
            "connection": parts[3] if len(parts) > 3 else "",
        })
    return rows


def _wifi_scan(dev: str) -> list[dict[str, Any]]:
    text = _run(["nmcli", "-t", "-f", "SSID,BSSID,CHAN,FREQ,SIGNAL,SECURITY", "dev", "wifi", "list", "ifname", dev])
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        parts = line.split(":")
        if len(parts) < 5:
            continue
        try:
            signal = int(parts[4] or "0")
        except ValueError:
            signal = 0
        rows.append({
            "ssid": parts[0] or "(hidden)",
            "bssid": parts[1],
            "channel": parts[2],
            "freq_mhz": parts[3],
            "signal_dbm": signal,
            "security": parts[5] if len(parts) > 5 else "",
        })
    return rows


def _iface_carrier(dev: str) -> str | None:
    path = Path(f"/sys/class/net/{dev}/carrier")
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _iface_stats(dev: str) -> dict[str, int]:
    base = Path(f"/sys/class/net/{dev}/statistics")
    out: dict[str, int] = {}
    for key in ("rx_bytes", "tx_bytes", "rx_errors", "tx_errors", "rx_dropped", "tx_dropped"):
        try:
            out[key] = int((base / key).read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            out[key] = 0
    return out


def _usb_video_devices() -> list[str]:
    text = _run(["lsusb"])
    hits: list[str] = []
    for line in text.splitlines():
        low = line.lower()
        if any(k in low for k in ("camera", "webcam", "video", "uvc", "ir ", "infrared")):
            hits.append(line.strip()[:120])
    return hits


def _shield_config() -> dict[str, Any]:
    doc = _load_json(SHIELD_CFG, {"enabled": True, "auto_rfkill": True, "updated": None})
    doc.setdefault("enabled", True)
    doc.setdefault("auto_rfkill", True)
    return doc


def _set_shield(enabled: bool | None = None, auto_rfkill: bool | None = None) -> dict[str, Any]:
    doc = _shield_config()
    if enabled is not None:
        doc["enabled"] = bool(enabled)
    if auto_rfkill is not None:
        doc["auto_rfkill"] = bool(auto_rfkill)
    doc["updated"] = _now()
    _save_json(SHIELD_CFG, doc)
    return doc


def _append_burst(row: dict[str, Any]) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    with BURSTS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    vector = VECTOR_MAP.get(str(row.get("kind") or ""), "RF_BURST")
    script = INSTALL / "lib" / "threat-vectors.sh"
    if script.is_file():
        detail = f"kind={row.get('kind')} dev={row.get('device','')} detail={row.get('detail','')}"
        env = os.environ.copy()
        env["NEXUS_STATE_DIR"] = str(STATE)
        env["NEXUS_INSTALL_ROOT"] = str(INSTALL)
        subprocess.run(
            ["bash", "-c", f'source "{script}" && nexus_threat_record "{vector}" "{row.get("severity","medium")}" "{detail}"'],
            capture_output=True,
            timeout=10,
            env=env,
        )


def _apply_shield(bursts: list[dict[str, Any]]) -> dict[str, Any]:
    cfg = _shield_config()
    if not cfg.get("enabled"):
        return {"active": False, "action": "shield_disabled"}
    severe = [b for b in bursts if b.get("severity") in ("high", "critical")]
    if not severe:
        return {"active": False, "action": "no_severe_burst"}
    if not cfg.get("auto_rfkill"):
        return {"active": True, "action": "alert_only", "burst_count": len(severe)}
    blocked: list[str] = []
    for row in _rfkill_rows():
        if row.get("type") != "wlan":
            continue
        if row.get("soft_blocked") == "yes":
            continue
        idx = row.get("index")
        if idx:
            _run(["rfkill", "block", idx])
            blocked.append(row.get("name") or idx)
    return {"active": True, "action": "rfkill_soft_block", "blocked": blocked, "burst_count": len(severe)}


def _history() -> dict[str, Any]:
    return _load_json(HISTORY, {"samples": [], "rfkill": [], "scans": {}, "carriers": {}})


def _save_history(doc: dict[str, Any]) -> None:
    doc["updated"] = _now()
    samples = doc.get("samples") or []
    doc["samples"] = samples[-120:]
    _save_json(HISTORY, doc)


def _detect_bursts(
    hist: dict[str, Any],
    devices: list[dict[str, str]],
    rfkill: list[dict[str, str]],
    wifi_dev: str | None,
    scan: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    bursts: list[dict[str, Any]] = []
    ts = _now()

    prev_rf = {(r.get("index"), r.get("name")): r.get("soft_blocked") for r in (hist.get("rfkill") or [])}
    for row in rfkill:
        key = (row.get("index"), row.get("name"))
        if key in prev_rf and prev_rf[key] != row.get("soft_blocked"):
            bursts.append({
                "ts": ts,
                "kind": "rf_burst",
                "severity": "high",
                "device": row.get("name"),
                "detail": f"rfkill state change soft={row.get('soft_blocked')}",
            })

    prev_carriers = hist.get("carriers") or {}
    flap_counts: dict[str, int] = {}
    for dev_row in devices:
        dev = dev_row.get("device") or ""
        if not dev or dev == "lo":
            continue
        carrier = _iface_carrier(dev)
        prev = prev_carriers.get(dev)
        if prev is not None and carrier is not None and prev != carrier:
            flap_counts[dev] = flap_counts.get(dev, 0) + 1
            if flap_counts[dev] >= CARRIER_FLAP_THRESHOLD:
                bursts.append({
                    "ts": ts,
                    "kind": "interface_flap",
                    "severity": "medium",
                    "device": dev,
                    "detail": f"carrier flapped {flap_counts[dev]}x",
                })

    if wifi_dev and scan:
        prev_scan = (hist.get("scans") or {}).get(wifi_dev) or []
        prev_bssids = {s.get("bssid") for s in prev_scan}
        cur_bssids = {s.get("bssid") for s in scan}
        churn = len(prev_bssids ^ cur_bssids)
        hidden = sum(1 for s in scan if s.get("ssid") == "(hidden)")
        signals = [int(s.get("signal_dbm") or 0) for s in scan if s.get("signal_dbm")]
        prev_signals = [int(s.get("signal_dbm") or 0) for s in prev_scan if s.get("signal_dbm")]
        if signals and prev_signals:
            delta = abs(max(signals) - max(prev_signals))
            if delta >= SIGNAL_DELTA_DB:
                bursts.append({
                    "ts": ts,
                    "kind": "wifi_interference",
                    "severity": "medium",
                    "device": wifi_dev,
                    "detail": f"signal swing {delta} dBm on {len(scan)} APs",
                })
        if churn >= SCAN_CHURN_THRESHOLD:
            bursts.append({
                "ts": ts,
                "kind": "dog_collar_rf",
                "severity": "high" if hidden >= 2 else "medium",
                "device": wifi_dev,
                "detail": f"2.4/5GHz scan churn {churn} BSSIDs — collar/remote burst heuristic",
            })
        freq_24 = [s for s in scan if str(s.get("freq_mhz") or "").startswith("2")]
        if len(freq_24) >= 8 and churn >= 3:
            bursts.append({
                "ts": ts,
                "kind": "dog_collar_rf",
                "severity": "medium",
                "device": wifi_dev,
                "detail": f"dense 2.4GHz field ({len(freq_24)} APs) with rapid churn",
            })

    usb_ir = _usb_video_devices()
    if usb_ir and bursts:
        bursts.append({
            "ts": ts,
            "kind": "ir_burst",
            "severity": "medium",
            "device": "usb",
            "detail": f"IR/video USB present during RF burst — {usb_ir[0][:80]}",
        })

    return bursts


def sample_cycle() -> dict[str, Any]:
    hist = _history()
    devices = _nmcli_devices()
    rfkill = _rfkill_rows()
    wifi_dev = None
    for row in devices:
        if row.get("type") == "wifi":
            wifi_dev = row.get("device")
            break

    scan: list[dict[str, Any]] = []
    if wifi_dev:
        _run(["nmcli", "dev", "wifi", "rescan", "ifname", wifi_dev], timeout=12)
        scan = _wifi_scan(wifi_dev)

    bursts = _detect_bursts(hist, devices, rfkill, wifi_dev, scan)
    for b in bursts:
        _append_burst(b)

    shield_result = _apply_shield(bursts) if bursts else {"active": _shield_config().get("enabled"), "action": "idle"}

    carriers = {d.get("device", ""): _iface_carrier(d.get("device", "")) for d in devices if d.get("device")}
    stats = {d.get("device", ""): _iface_stats(d.get("device", "")) for d in devices if d.get("device") and d.get("device") != "lo"}

    hist["rfkill"] = rfkill
    hist["carriers"] = carriers
    if wifi_dev:
        scans = hist.get("scans") or {}
        scans[wifi_dev] = scan[:40]
        hist["scans"] = scans
    hist.setdefault("samples", []).append({"ts": _now(), "burst_count": len(bursts)})
    _save_history(hist)

    recent = _recent_bursts(30)
    return {
        "updated": _now(),
        "antenna": {
            "mode": "internal_field",
            "description": "Software field antenna — nmcli/iw/rfkill/sysfs correlation",
            "wifi_device": wifi_dev,
            "scan_count": len(scan),
            "rfkill_count": len(rfkill),
            "usb_ir_proxies": len(_usb_video_devices()),
        },
        "interfaces": devices,
        "rfkill": rfkill,
        "bursts": bursts,
        "recent_bursts": recent,
        "shield": {**_shield_config(), **shield_result},
        "interface_stats": stats,
    }


def _recent_bursts(limit: int = 40) -> list[dict[str, Any]]:
    if not BURSTS_LOG.is_file():
        return []
    lines = deque(maxlen=limit)
    try:
        with BURSTS_LOG.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    lines.append(line)
    except OSError:
        return []
    out: list[dict[str, Any]] = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def panel_json() -> dict[str, Any]:
    doc = _load_json(STATE / "field-rf-panel.json", {})
    if not doc.get("updated"):
        doc = sample_cycle()
        _save_json(STATE / "field-rf-panel.json", doc)
    return {
        "motto": "Internal field antenna — RF, WiFi, dog-collar burst, and IR-proxy detection.",
        "tagline": "We generate our own field sensor from Linux telemetry and shield the operator when bursts spike.",
        "updated": doc.get("updated") or _now(),
        "antenna": doc.get("antenna") or {},
        "interfaces": doc.get("interfaces") or _nmcli_devices(),
        "rfkill": doc.get("rfkill") or _rfkill_rows(),
        "bursts": doc.get("bursts") or [],
        "recent_bursts": doc.get("recent_bursts") or _recent_bursts(),
        "shield": doc.get("shield") or _shield_config(),
        "interface_stats": doc.get("interface_stats") or {},
        "burst_kinds": [
            {"id": "wifi_interference", "label": "WiFi interference", "vector": "WIFI_INTERFERENCE"},
            {"id": "rf_burst", "label": "RF / rfkill burst", "vector": "RF_BURST"},
            {"id": "dog_collar_rf", "label": "Dog-collar / 2.4GHz chatter", "vector": "FIELD_ANTENNA_ALERT"},
            {"id": "ir_burst", "label": "IR burst (USB proxy)", "vector": "FIELD_ANTENNA_ALERT"},
            {"id": "interface_flap", "label": "Interface carrier flap", "vector": "RF_BURST"},
        ],
    }


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    if cmd == "cycle":
        doc = sample_cycle()
        _save_json(STATE / "field-rf-panel.json", doc)
        print(json.dumps(doc, ensure_ascii=False))
        return 0
    if cmd == "shield" and len(sys.argv) >= 3:
        enabled = sys.argv[2].strip().lower() in ("1", "true", "on", "yes")
        auto = True
        if len(sys.argv) >= 4:
            auto = sys.argv[3].strip().lower() in ("1", "true", "on", "yes")
        doc = _set_shield(enabled=enabled, auto_rfkill=auto)
        print(json.dumps({"ok": True, "shield": doc}, ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: field-rf-sentinel.py [json|cycle|shield on|off]"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
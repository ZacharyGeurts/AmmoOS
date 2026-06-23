#!/usr/bin/env python3
"""Field RF Sentinel — FCC-compliant passive wireless threat watch.

Passive global WiFi field scan (receive-only beacon correlation). Detects rogue
APs, evil twins, hostile OUIs, and open downgrades. Lawful kick: disconnect OUR
station from threats, firewall-block correlated hostile IPs, autokill at 100%
certainty — never jamming, bursts, or unsafe RF transmission.
"""
from __future__ import annotations

import importlib.util
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
THREATS_LOG = STATE / "field-rf-threats.jsonl"
PANEL_CACHE = STATE / "field-rf-panel.json"
FCC_POLICY = INSTALL / "data" / "fcc-wireless-policy.json"
HOSTILE_TSV = STATE / "field-hostile.tsv"
HOST_ATTACKS = STATE / "host-attacks.json"
OUI_VENDORS = INSTALL / "data" / "oui-vendors.tsv"

SUSPICIOUS_SSID_RE = re.compile(
    r"(free[\s_-]?wifi|airport|xfinitywifi|attwifi|starbucks|"
    r"setup[\s_-]?router|linksys|netgear|dlink|tp[\s_-]?link|"
    r"evil|honeypot|pineapple|wifi[\s_-]?password|connect[\s_-]?here)",
    re.I,
)
ENTERPRISE_SSID_RE = re.compile(r"(corp|enterprise|vpn|office|company|secure)", re.I)
WEAK_SECURITY = frozenset({"", "--", "open", "wep"})

VECTOR_MAP = {
    "evil_twin": "WIFI_THREAT",
    "rogue_open": "WIFI_THREAT",
    "hostile_oui": "WIFI_THREAT",
    "enterprise_downgrade": "WIFI_THREAT",
    "hidden_surveillance": "WIFI_THREAT",
    "connected_rogue": "WIFI_THREAT",
    "correlated_hostile_ip": "WIFI_THREAT",
    "global_wireless_field": "FIELD_ANTENNA_ALERT",
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


def _norm_mac(mac: str) -> str:
    return re.sub(r"[^0-9a-f]", "", str(mac or "").lower())[:12]


def _mac_oui(mac: str) -> str:
    raw = _norm_mac(mac)
    if len(raw) < 6:
        return ""
    return f"{raw[0:2]}:{raw[2:4]}:{raw[4:6]}".upper()


def _fcc_policy() -> dict[str, Any]:
    doc = _load_json(FCC_POLICY, {})
    if doc.get("schema"):
        return doc
    return {
        "motto": "Passive watch globally. Lawful kick on the wire. No bursts. No jamming.",
        "allowed": ["Passive scan", "Disconnect our station", "Firewall block", "100% autokill"],
        "forbidden": ["Jamming", "Deauth floods", "Burst interference", "Auto rfkill on spikes"],
    }


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
        sec = (parts[5] if len(parts) > 5 else "").strip().lower()
        bssid = parts[1] or ""
        rows.append({
            "ssid": parts[0] or "(hidden)",
            "bssid": bssid,
            "bssid_oui": _mac_oui(bssid),
            "channel": parts[2],
            "freq_mhz": parts[3],
            "band": _band_label(parts[3]),
            "signal_dbm": signal,
            "security": sec,
            "open": sec in WEAK_SECURITY,
        })
    return rows


def _band_label(freq: Any) -> str:
    f = str(freq or "")
    if f.startswith("2"):
        return "2.4GHz"
    if f.startswith("5"):
        return "5GHz"
    if f.startswith("6"):
        return "6GHz"
    return "unknown"


def _active_wifi_connection(wifi_dev: str) -> dict[str, Any] | None:
    text = _run(["nmcli", "-t", "-f", "GENERAL.CONNECTION,GENERAL.STATE,802-11-wireless.ssid,802-11-wireless.bssid", "dev", "show", wifi_dev])
    if not text.strip():
        return None
    doc: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        doc[key.strip()] = val.strip()
    state = doc.get("GENERAL.STATE", "")
    if "connected" not in state.lower():
        return None
    bssid = doc.get("802-11-wireless.bssid", "")
    return {
        "device": wifi_dev,
        "connection": doc.get("GENERAL.CONNECTION", ""),
        "ssid": doc.get("802-11-wireless.ssid", ""),
        "bssid": bssid,
        "bssid_oui": _mac_oui(bssid),
        "state": state,
    }


def _hostile_ips() -> set[str]:
    ips: set[str] = set()
    if not HOSTILE_TSV.is_file():
        return ips
    try:
        for line in HOSTILE_TSV.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) >= 2 and parts[1]:
                ips.add(parts[1].strip())
    except OSError:
        pass
    return ips


def _hostile_macs() -> set[str]:
    macs: set[str] = set()
    hi = INSTALL / "lib" / "host-identity.py"
    if hi.is_file():
        spec = importlib.util.spec_from_file_location("host_identity_rf", hi)
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        for path_fn in (
            lambda: (STATE / "field-storage" / "nexus-target-dossiers.jsonl"),
        ):
            path = path_fn()
            if not path.is_file():
                continue
            try:
                for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    dos = row.get("dossier") if isinstance(row.get("dossier"), dict) else row
                    for key in ("mac", "bssid"):
                        val = dos.get(key) or (dos.get("intel") or {}).get(key)
                        if val:
                            macs.add(_norm_mac(str(val)))
            except (OSError, json.JSONDecodeError):
                continue
    return {m for m in macs if len(m) >= 6}


def _suspicious_ouis() -> dict[str, str]:
    out: dict[str, str] = {}
    if not OUI_VENDORS.is_file():
        return out
    try:
        for line in OUI_VENDORS.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            prefix = parts[0].strip().upper()
            vendor = parts[1].strip()
            cat = parts[2].strip().lower() if len(parts) > 2 else ""
            if cat in ("virtualization",) or "pineapple" in vendor.lower() or "hack" in vendor.lower():
                out[prefix] = vendor
    except OSError:
        pass
    out.setdefault("00:C0:CA", "WiFi Pineapple / Hak5")
    return out


def _correlated_hostile_points() -> list[dict[str, Any]]:
    doc = _load_json(HOST_ATTACKS, {})
    hostile = _hostile_ips()
    out: list[dict[str, Any]] = []
    for p in doc.get("points") or []:
        ip = str(p.get("ip") or "")
        if not ip:
            continue
        if ip in hostile or p.get("strike_certain") or float(p.get("heat") or 0) >= 0.7:
            out.append(p)
    return out


def _shield_config() -> dict[str, Any]:
    doc = _load_json(SHIELD_CFG, {})
    doc.setdefault("enabled", True)
    doc.setdefault("lawful_kick", True)
    doc.setdefault("fcc_passive_only", True)
    doc.setdefault("global_watch", True)
    doc.setdefault("auto_rfkill", False)
    return doc


def _set_shield(
    enabled: bool | None = None,
    auto_rfkill: bool | None = None,
    lawful_kick: bool | None = None,
) -> dict[str, Any]:
    doc = _shield_config()
    if enabled is not None:
        doc["enabled"] = bool(enabled)
    if auto_rfkill is not None:
        doc["auto_rfkill"] = bool(auto_rfkill)
    if lawful_kick is not None:
        doc["lawful_kick"] = bool(lawful_kick)
    doc["fcc_passive_only"] = True
    doc["updated"] = _now()
    _save_json(SHIELD_CFG, doc)
    return doc


def _append_threat(row: dict[str, Any]) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    with THREATS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    vector = VECTOR_MAP.get(str(row.get("kind") or ""), "WIFI_THREAT")
    script = INSTALL / "lib" / "threat-vectors.sh"
    if script.is_file():
        detail = (
            f"kind={row.get('kind')} bssid={row.get('bssid','')} "
            f"ssid={row.get('ssid','')} detail={row.get('detail','')}"
        )
        env = os.environ.copy()
        env["NEXUS_STATE_DIR"] = str(STATE)
        env["NEXUS_INSTALL_ROOT"] = str(INSTALL)
        subprocess.run(
            [
                "bash", "-c",
                f'source "{script}" && nexus_threat_record "{vector}" "{row.get("severity","medium")}" "{detail}"',
            ],
            capture_output=True,
            timeout=10,
            env=env,
        )


def _detect_wireless_threats(
    scan: list[dict[str, Any]],
    active: dict[str, Any] | None,
    hist: dict[str, Any],
) -> list[dict[str, Any]]:
    threats: list[dict[str, Any]] = []
    ts = _now()
    hostile_macs = _hostile_macs()
    suspicious_ouis = _suspicious_ouis()
    trusted_ssids = set(hist.get("trusted_ssids") or [])

    if scan:
        threats.append({
            "ts": ts,
            "kind": "global_wireless_field",
            "severity": "info",
            "detail": f"Passive global field — {len(scan)} APs across bands "
            f"({sum(1 for s in scan if s.get('band') == '2.4GHz')} 2.4 / "
            f"{sum(1 for s in scan if s.get('band') == '5GHz')} 5 / "
            f"{sum(1 for s in scan if s.get('band') == '6GHz')} 6 GHz)",
            "global": True,
        })

    by_ssid: dict[str, list[dict[str, Any]]] = {}
    for ap in scan:
        by_ssid.setdefault(ap.get("ssid") or "(hidden)", []).append(ap)

    for ssid, group in by_ssid.items():
        if ssid == "(hidden)":
            strong_hidden = [a for a in group if int(a.get("signal_dbm") or 0) >= 70]
            if len(strong_hidden) >= 2:
                threats.append({
                    "ts": ts,
                    "kind": "hidden_surveillance",
                    "severity": "medium",
                    "ssid": ssid,
                    "detail": f"{len(strong_hidden)} strong hidden APs in passive scan",
                    "global": True,
                })
            continue
        bssids = {a.get("bssid") for a in group if a.get("bssid")}
        if len(bssids) >= 2:
            open_aps = [a for a in group if a.get("open")]
            secure = [a for a in group if not a.get("open")]
            if open_aps and secure:
                threats.append({
                    "ts": ts,
                    "kind": "evil_twin",
                    "severity": "high",
                    "ssid": ssid,
                    "bssid": open_aps[0].get("bssid"),
                    "detail": f"Evil-twin pattern — open + secure BSSIDs for SSID {ssid[:32]}",
                    "global": True,
                })
        if SUSPICIOUS_SSID_RE.search(ssid):
            for ap in group:
                if ap.get("open"):
                    threats.append({
                        "ts": ts,
                        "kind": "rogue_open",
                        "severity": "high",
                        "ssid": ssid,
                        "bssid": ap.get("bssid"),
                        "detail": f"Open rogue AP mimicking public WiFi — {ssid[:40]}",
                        "global": True,
                    })
        if ENTERPRISE_SSID_RE.search(ssid):
            for ap in group:
                if ap.get("open") or "wep" in str(ap.get("security") or ""):
                    threats.append({
                        "ts": ts,
                        "kind": "enterprise_downgrade",
                        "severity": "high",
                        "ssid": ssid,
                        "bssid": ap.get("bssid"),
                        "detail": f"Enterprise-looking SSID with weak security ({ap.get('security')})",
                        "global": True,
                    })

    for ap in scan:
        oui = str(ap.get("bssid_oui") or "").upper()
        bssid_norm = _norm_mac(str(ap.get("bssid") or ""))
        if bssid_norm and bssid_norm in hostile_macs:
            threats.append({
                "ts": ts,
                "kind": "hostile_oui",
                "severity": "critical",
                "ssid": ap.get("ssid"),
                "bssid": ap.get("bssid"),
                "detail": "BSSID matches archived hostile dossier MAC",
                "global": True,
            })
        if oui in suspicious_ouis:
            threats.append({
                "ts": ts,
                "kind": "hostile_oui",
                "severity": "high",
                "ssid": ap.get("ssid"),
                "bssid": ap.get("bssid"),
                "detail": f"Suspicious OUI {oui} — {suspicious_ouis[oui]}",
                "global": True,
            })

    if active:
        active_bssid = _norm_mac(str(active.get("bssid") or ""))
        for t in threats:
            if t.get("severity") in ("high", "critical") and t.get("bssid"):
                if _norm_mac(str(t.get("bssid"))) == active_bssid:
                    threats.append({
                        "ts": ts,
                        "kind": "connected_rogue",
                        "severity": "critical",
                        "ssid": active.get("ssid"),
                        "bssid": active.get("bssid"),
                        "device": active.get("device"),
                        "detail": f"Connected to flagged AP {active.get('ssid')} — lawful kick eligible",
                        "global": True,
                    })
                    break
        if active.get("ssid") and active.get("ssid") not in trusted_ssids and not SUSPICIOUS_SSID_RE.search(active.get("ssid", "")):
            trusted_ssids.add(active.get("ssid"))

    for point in _correlated_hostile_points()[:12]:
        if point.get("strike_certain"):
            threats.append({
                "ts": ts,
                "kind": "correlated_hostile_ip",
                "severity": "critical",
                "ip": point.get("ip"),
                "detail": f"Monitor host {point.get('ip')} at 100% strike certainty — wire kick eligible",
                "global": True,
                "strike_certain": True,
            })

    hist["trusted_ssids"] = sorted(trusted_ssids)[-40:]
    return [t for t in threats if t.get("severity") != "info" or t.get("kind") == "global_wireless_field"]


def _disconnect_wifi(dev: str, reason: str) -> bool:
    if not dev:
        return False
    out = _run(["nmcli", "dev", "disconnect", dev], timeout=12)
    return "successfully" in out.lower() or dev in out


def _firewall_block_ip(ip: str, reason: str) -> bool:
    script = INSTALL / "lib" / "firewall-sentinel.sh"
    if not script.is_file() or not ip:
        return False
    safe_ip = ip.replace("'", "'\"'\"'")
    safe_reason = reason.replace("'", "'\"'\"'")
    cmd = (
        f"source {INSTALL}/lib/nexus-common.sh && "
        f"source {script} && "
        f"nexus_firewall_block_ip_forever out '{safe_ip}' '{safe_reason}' && "
        f"nexus_firewall_block_ip_forever in '{safe_ip}' '{safe_reason}'"
    )
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL)
    env["NEXUS_STATE_DIR"] = str(STATE)
    proc = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=20, env=env)
    return proc.returncode == 0


def _autokill_ip(ip: str) -> dict[str, Any]:
    script = INSTALL / "lib" / "field-attack-kit.py"
    if not script.is_file() or not ip:
        return {"ok": False, "ip": ip}
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL)
    env["NEXUS_STATE_DIR"] = str(STATE)
    proc = subprocess.run(
        [os.environ.get("PYTHON", "python3"), str(script), "kill", ip, "WIFI_THREAT", "high", "rf_lawful_kick"],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": proc.returncode == 0, "ip": ip}


def _lawful_kick(
    threats: list[dict[str, Any]],
    wifi_dev: str | None,
    active: dict[str, Any] | None,
) -> dict[str, Any]:
    cfg = _shield_config()
    if not cfg.get("enabled") or not cfg.get("lawful_kick"):
        return {"active": False, "action": "lawful_kick_disabled", "fcc_passive_only": True}

    kicks: list[dict[str, Any]] = []
    kicked_ips: set[str] = set()

    kickable = {t.get("kind") for t in threats if t.get("severity") in ("high", "critical")}
    if active and wifi_dev and ("connected_rogue" in kickable or "evil_twin" in kickable or "rogue_open" in kickable):
        if _disconnect_wifi(wifi_dev, "fcc_lawful_kick_rogue_ap"):
            kicks.append({
                "action": "disconnect_rogue_ap",
                "device": wifi_dev,
                "ssid": active.get("ssid"),
                "bssid": active.get("bssid"),
                "fcc": "Part15_device_control",
            })

    for t in threats:
        if t.get("kind") != "correlated_hostile_ip" or not t.get("strike_certain"):
            continue
        ip = str(t.get("ip") or "")
        if not ip or ip in kicked_ips:
            continue
        kicked_ips.add(ip)
        result = _autokill_ip(ip)
        if result.get("ok") or result.get("hardware_destroy"):
            kicks.append({
                "action": "autokill_strike_certain",
                "ip": ip,
                "hardware_destroy": result.get("hardware_destroy"),
                "fcc": "network_layer_only",
            })
        elif _firewall_block_ip(ip, "fcc_wifi_correlated_hostile"):
            kicks.append({
                "action": "firewall_block_correlated_ip",
                "ip": ip,
                "fcc": "network_layer_only",
            })

    for t in threats:
        ip = str(t.get("ip") or "")
        if not ip or ip in kicked_ips or t.get("kind") == "correlated_hostile_ip":
            continue
        if t.get("severity") == "critical" and _firewall_block_ip(ip, "fcc_wifi_threat"):
            kicked_ips.add(ip)
            kicks.append({"action": "firewall_block_correlated_ip", "ip": ip})

    return {
        "active": True,
        "action": "lawful_kick" if kicks else "watch_only",
        "fcc_passive_only": cfg.get("fcc_passive_only", True),
        "kicks": kicks,
        "kick_count": len(kicks),
        "auto_rfkill": False,
    }


def _history() -> dict[str, Any]:
    return _load_json(HISTORY, {"samples": [], "rfkill": [], "scans": {}, "trusted_ssids": []})


def _save_history(doc: dict[str, Any]) -> None:
    doc["updated"] = _now()
    samples = doc.get("samples") or []
    doc["samples"] = samples[-120:]
    _save_json(HISTORY, doc)


def _recent_threats(limit: int = 40) -> list[dict[str, Any]]:
    if not THREATS_LOG.is_file():
        return []
    lines = deque(maxlen=limit)
    try:
        with THREATS_LOG.open(encoding="utf-8") as fh:
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
    active = None
    if wifi_dev:
        _run(["nmcli", "dev", "wifi", "rescan", "ifname", wifi_dev], timeout=12)
        scan = _wifi_scan(wifi_dev)
        active = _active_wifi_connection(wifi_dev)

    threats = _detect_wireless_threats(scan, active, hist)
    for t in threats:
        if t.get("severity") != "info":
            _append_threat(t)

    kick_result = _lawful_kick(threats, wifi_dev, active)

    if wifi_dev:
        scans = hist.get("scans") or {}
        scans[wifi_dev] = scan[:60]
        hist["scans"] = scans
    hist["rfkill"] = rfkill
    hist.setdefault("samples", []).append({
        "ts": _now(),
        "threat_count": sum(1 for t in threats if t.get("severity") != "info"),
        "kick_count": kick_result.get("kick_count", 0),
    })
    _save_history(hist)

    bands = {s.get("band") for s in scan if s.get("band")}
    return {
        "updated": _now(),
        "fcc": _fcc_policy(),
        "antenna": {
            "mode": "fcc_passive_global",
            "description": "Passive global wireless field — FCC Part 15 receive-only scan",
            "wifi_device": wifi_dev,
            "scan_count": len(scan),
            "bands_seen": sorted(b for b in bands if b),
            "rfkill_count": len(rfkill),
            "active_connection": active,
        },
        "interfaces": devices,
        "rfkill": rfkill,
        "threats": [t for t in threats if t.get("severity") != "info"],
        "global_field": next((t for t in threats if t.get("kind") == "global_wireless_field"), None),
        "recent_threats": _recent_threats(30),
        "shield": {**_shield_config(), **kick_result},
        "lawful_kicks": kick_result.get("kicks") or [],
        "bursts": [],
        "recent_bursts": [],
    }


def panel_json() -> dict[str, Any]:
    doc = _load_json(PANEL_CACHE, {})
    if not doc.get("updated"):
        doc = sample_cycle()
        _save_json(PANEL_CACHE, doc)
    return {
        "motto": "FCC-compliant passive global wireless watch — lawful kick on the wire, never jamming.",
        "tagline": "Detect threats worldwide in our scan field. Disconnect rogues. Block hostile IPs. 100% autokill. No bursts.",
        "fcc": doc.get("fcc") or _fcc_policy(),
        "updated": doc.get("updated") or _now(),
        "antenna": doc.get("antenna") or {},
        "interfaces": doc.get("interfaces") or _nmcli_devices(),
        "rfkill": doc.get("rfkill") or _rfkill_rows(),
        "threats": doc.get("threats") or [],
        "global_field": doc.get("global_field"),
        "recent_threats": doc.get("recent_threats") or _recent_threats(),
        "lawful_kicks": doc.get("lawful_kicks") or [],
        "shield": doc.get("shield") or _shield_config(),
        "threat_kinds": [
            {"id": "evil_twin", "label": "Evil twin AP", "vector": "WIFI_THREAT"},
            {"id": "rogue_open", "label": "Rogue open AP", "vector": "WIFI_THREAT"},
            {"id": "hostile_oui", "label": "Hostile / suspicious OUI", "vector": "WIFI_THREAT"},
            {"id": "enterprise_downgrade", "label": "Enterprise downgrade", "vector": "WIFI_THREAT"},
            {"id": "hidden_surveillance", "label": "Hidden AP cluster", "vector": "WIFI_THREAT"},
            {"id": "connected_rogue", "label": "Connected to rogue", "vector": "WIFI_THREAT"},
            {"id": "correlated_hostile_ip", "label": "100% hostile IP (wire kick)", "vector": "WIFI_THREAT"},
            {"id": "global_wireless_field", "label": "Global passive field", "vector": "FIELD_ANTENNA_ALERT"},
        ],
        "bursts": [],
        "recent_bursts": [],
        "burst_kinds": [],
    }


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    if cmd == "cycle":
        doc = sample_cycle()
        _save_json(PANEL_CACHE, doc)
        print(json.dumps(doc, ensure_ascii=False))
        return 0
    if cmd == "shield" and len(sys.argv) >= 3:
        enabled = sys.argv[2].strip().lower() in ("1", "true", "on", "yes")
        auto = False
        lawful = True
        if len(sys.argv) >= 4:
            auto = sys.argv[3].strip().lower() in ("1", "true", "on", "yes")
        if len(sys.argv) >= 5:
            lawful = sys.argv[4].strip().lower() in ("1", "true", "on", "yes", "")
        doc = _set_shield(enabled=enabled, auto_rfkill=auto, lawful_kick=lawful)
        print(json.dumps({"ok": True, "shield": doc, "fcc_passive_only": True}, ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: field-rf-sentinel.py [json|cycle|shield on|off [auto_rfkill] [lawful_kick]]"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
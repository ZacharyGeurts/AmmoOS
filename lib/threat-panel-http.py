#!/usr/bin/env pythong
"""Local threat panel server — HTTP on loopback only (Hostess7-secured)."""

import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9477
PANEL_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("panel")
STATUS_JSON = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("threat-panel.json")
STATE_DIR = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL_ROOT = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
ZNETWORK_STATUS = STATE_DIR / "znetwork-status.json"


def _resolve_hostess7_root() -> Path:
    env = os.environ.get("HOSTESS7_ROOT", "").strip()
    if env:
        return Path(env).expanduser()
    try:
        if str(INSTALL_ROOT / "lib") not in sys.path:
            sys.path.insert(0, str(INSTALL_ROOT / "lib"))
        import sg_paths  # noqa: PLC0415

        return sg_paths.hostess7_root()
    except Exception:
        return INSTALL_ROOT / "Hostess7"


def _h7_library_snapshot_paths() -> list[Path]:
    roots: list[Path] = []
    h7 = _resolve_hostess7_root()
    roots.append(h7 / "cache" / "fieldstorage" / "brain" / "library" / "catalog_snapshot.json")
    team = Path(os.environ.get("HOSTESS7_TEAM_FIELD", "/media/default/HOSTESS7_TEAM/fieldstorage"))
    if team.is_dir():
        roots.append(team / "brain" / "library" / "catalog_snapshot.json")
    return roots


def _load_h7_library_catalog_fast() -> dict | None:
    cached = _panel_slice("h7_library", default={})
    if isinstance(cached, dict) and cached.get("books") and not cached.get("_partial"):
        return cached
    for path in _h7_library_snapshot_paths():
        if not path.is_file():
            continue
        try:
            snap = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(snap, dict) and snap.get("books"):
            snap = dict(snap)
            snap["_catalog_snapshot"] = True
            snap.setdefault("_partial", False)
            snap.setdefault("_incomplete", False)
            return snap
    return None


def _load_plate_meld_cached() -> dict:
    """Hot read — never run full meld() on panel GET (that can take minutes)."""
    candidates = (
        STATE_DIR / "field-plate-meld.json",
        STATE_DIR / "field-plate-meld-runtime.json",
        STATE_DIR / "plate-meld-redundant" / "field-plate-meld.json",
        STATE_DIR / "plate-meld-redundant" / "field-plate-meld.json.bak",
    )
    for path in candidates:
        if not path.is_file():
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(doc, dict) and doc.get("schema"):
            doc = dict(doc)
            doc["_field_cache"] = True
            return doc
    return {}


_LOOPBACK_CLIENTS = frozenset({"127.0.0.1", "::1", "::ffff:127.0.0.1"})

DATA_FILES = {
    "threat-panel": STATE_DIR / "threat-panel.json",
    "threat-vectors": STATE_DIR / "threat-vectors.tsv",
    "firewall-blocks": STATE_DIR / "firewall-blocks.tsv",
    "sanitize-actions": STATE_DIR / "sanitize-actions.tsv",
    "paranoia-incidents": STATE_DIR / "paranoia-incidents.jsonl",
    "paranoia-state": STATE_DIR / "paranoia.state",
    "shutdown-incidents": STATE_DIR / "shutdown-incidents.jsonl",
    "shutdown-state": STATE_DIR / "shutdown.state",
    "nexus-last-alive": STATE_DIR / "nexus-last-alive.json",
    "packet-snapshot": STATE_DIR / "packet.snapshot",
    "packet-field": STATE_DIR / "packet-field.json",
    "packet-field-ring": STATE_DIR / "packet-field.ring.jsonl",
    "arp-snapshot": STATE_DIR / "arp.snapshot",
    "firewall-state": STATE_DIR / "firewall.state",
    "firewall-trusted": STATE_DIR / "firewall-trusted.tsv",
    "vigil-state": STATE_DIR / "vigil.state",
    "human-dossier": STATE_DIR / "human-dossier.json",
}

LOG_FILES = {
    "alerts": Path("/var/log/nexus-alerts.log"),
    "vigil": STATE_DIR / "vigil-alerts.log",
}

# Keys loaded in parallel by the panel — omitted from /api/status unless ?full=1
PANEL_PARALLEL_KEYS = frozenset({
    "field_hardware",
    "field_hazard_onset",
    "lethal_enforcement",
    "hostess7_lethal_insight",
    "hostess7_command",
    "signals_field",
    "field_antenna",
    "field_radio",
    "field_dns",
    "field_outside_talk",
    "field_drive",
    "home_protector",
    "local_services",
    "audio_train",
    "field_rf",
    "terror_spiderweb",
    "precision_field",
    "h7_library",
    "packet_field",
    "port_ddos_shield",
    "packet_deinterlace",
    "field_bus",
    "kernel_meld",
    "firmware_threat",
    "gatekeeper",
    "host_attacks",
    "planetary_observer",
    "us_field",
    "field_command",
    "angel_dossiers",
    "human_dossier",
    "angel_research",
    "browser_awareness",
    "field_queen_browser",
    "field_stack",
    "field_eyeball",
    "trust_strike",
    "field_weapons",
    "settings",
    "field_brain",
})


def _read_install_version() -> str:
    common = INSTALL_ROOT / "lib" / "nexus-common.sh"
    if common.is_file():
        try:
            import re

            m = re.search(
                r'NEXUS_VERSION="([^"]+)"',
                common.read_text(encoding="utf-8", errors="replace"),
            )
            if m:
                return m.group(1)
        except OSError:
            pass
    return os.environ.get("NEXUS_VERSION", "8.2.0")


def _read_nexus_conf() -> dict[str, str]:
    conf = INSTALL_ROOT / "config" / "nexus.conf"
    out: dict[str, str] = {}
    if not conf.is_file():
        return out
    try:
        for line in conf.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            out[key.strip()] = val.strip().strip('"').strip("'")
    except OSError:
        pass
    return out


def _conf_val(key: str, default: str = "") -> str:
    conf = _read_nexus_conf()
    return os.environ.get(key, conf.get(key, default))


def _conf_flag(key: str, default: str = "0") -> bool:
    return _conf_val(key, default) == "1"


def _conf_int(key: str, default: int) -> int:
    try:
        return int(_conf_val(key, str(default)))
    except ValueError:
        return default


def _cpu_vulnerability_json(*, apply: bool = False) -> dict:
    script = INSTALL_ROOT / "lib" / "cpu-vulnerability-shield.py"
    if not script.is_file():
        return {
            "schema": "cpu-vulnerability-shield/v1",
            "ok": False,
            "error": "cpu_vulnerability_shield_missing",
            "verdict": "UNKNOWN",
        }
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    if apply:
        env["NEXUS_CPU_VULN_APPLY"] = "1"
    proc = subprocess.run(
        [sys.executable, str(script), "board" if apply else "json"],
        capture_output=True,
        text=True,
        timeout=45,
        env=env,
    )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": (proc.stderr or "cpu_vuln_bad_json")[:300]}


def _field_polkit_json() -> dict:
    script = INSTALL_ROOT / "lib" / "field-polkit.py"
    if not script.is_file():
        return {
            "schema": "field-polkit/v1",
            "ok": False,
            "error": "field_polkit_missing",
            "verdict": "UNKNOWN",
        }
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    proc = subprocess.run(
        [sys.executable, str(script), "json"],
        capture_output=True,
        text=True,
        timeout=25,
        env=env,
    )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": (proc.stderr or "field_polkit_bad_json")[:300]}


def _field_underlay_json() -> dict:
    script = INSTALL_ROOT / "lib" / "field-underlay.py"
    if not script.is_file():
        return {
            "schema": "field-underlay/v1",
            "ok": False,
            "error": "field_underlay_missing",
            "verdict": "UNKNOWN",
        }
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    proc = subprocess.run(
        [sys.executable, str(script), "json"],
        capture_output=True,
        text=True,
        timeout=40,
        env=env,
    )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": (proc.stderr or "field_underlay_bad_json")[:300]}


def _tristate_installer_json(*, verb: str = "json", body: dict | None = None) -> dict:
    script = INSTALL_ROOT / "lib" / "field-underlay-switch.py"
    if not script.is_file():
        return {
            "schema": "tristate-installer/v1",
            "ok": False,
            "error": "tristate_installer_missing",
        }
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    if body and body.get("choice"):
        env["ZNETWORK_CHOICE"] = str(body.get("choice") or "")
    args = [sys.executable, str(script), verb]
    if body and body.get("confirm"):
        args.append("--confirm")
    if os.environ.get("NEXUS_ELEVATED_ROOT") == "1":
        args.append("--elevated")
    proc = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=600 if verb == "wrdt-apply" else 180,
        env=env,
    )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": (proc.stderr or "tristate_bad_json")[:300]}


def _tristate_elevated_json(verb: str, body: dict | None = None) -> dict:
    if os.geteuid() == 0:
        env = os.environ.copy()
        env["NEXUS_ELEVATED_ROOT"] = "1"
        os.environ.update(env)
        return _tristate_installer_json(verb=verb, body=body)
    bridge = INSTALL_ROOT / "lib" / "nexus-pkexec-bridge.sh"
    if not bridge.is_file():
        return _tristate_installer_json(verb=verb, body=body)
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    args = [str(bridge), "run-underlay", verb]
    if body and body.get("confirm"):
        args.append("--confirm")
    proc = subprocess.run(
        ["pkexec", "--action", "com.nexus.field.underlay", *args],
        capture_output=True,
        text=True,
        timeout=600,
        env=env,
    )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": (proc.stderr or "underlay_elevate_failed")[:300]}


def _native_layer_json(*, audit: bool = False) -> dict:
    script = INSTALL_ROOT / "lib" / "native-layer.py"
    if not script.is_file():
        return {
            "schema": "native-layer/v1",
            "ok": False,
            "error": "native_layer_missing",
            "we_are_the_native": True,
            "flash_chip": False,
        }
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    env.setdefault("SG_ROOT", str(INSTALL_ROOT.parent.parent))
    env.setdefault("KILROY_ROOT", str(Path(env["SG_ROOT"]) / "KILROY"))
    env.setdefault("QUEEN_ROOT", str(INSTALL_ROOT.parent / "Queen"))
    args = [sys.executable, str(script), "json"]
    if audit:
        args.append("--audit")
    proc = subprocess.run(args, capture_output=True, text=True, timeout=60, env=env)
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": (proc.stderr or "native_layer_bad_json")[:300]}


def _ai_integration_json(body: dict | None = None, *, peer: str = "127.0.0.1", headers: dict | None = None) -> dict:
    script = INSTALL_ROOT / "lib" / "ai-integration-hook.py"
    if not script.is_file():
        return {
            "schema": "nexus-ai-integration-hook/v1",
            "ok": False,
            "error": "ai_integration_hook_missing",
            "human_integration": False,
            "policy": "ai_only_never_human",
        }
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    if body is None:
        proc = subprocess.run(
            [sys.executable, str(script), "json"],
            capture_output=True,
            text=True,
            timeout=25,
            env=env,
        )
    else:
        payload = dict(body)
        payload["_peer"] = peer
        if headers:
            payload["_headers"] = headers
        proc = subprocess.run(
            [sys.executable, str(script), "dispatch"],
            input=json.dumps(payload, ensure_ascii=False),
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
        )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": (proc.stderr or "ai_integration_bad_json")[:300]}


def _panel_field_meta() -> dict:
    field_max = _conf_flag("NEXUS_FIELD_MAX")
    refresh_ms = _conf_int("NEXUS_PANEL_REFRESH_MS", 5000)
    if field_max:
        refresh_ms = max(800, min(refresh_ms, 2000))
    quota = _conf_int("NEXUS_CPU_QUOTA_PCT", 85 if field_max else 5)
    return {
        "field_max": field_max,
        "panel_refresh_ms": refresh_ms,
        "amouranthrtx_rainbow": _conf_flag("NEXUS_AMOURANTHRTX_RAINBOW"),
        "event_driven_only": _conf_flag("NEXUS_EVENT_DRIVEN_ONLY"),
        "panel_parallel_workers": _conf_int("NEXUS_PANEL_PARALLEL_WORKERS", 8),
        "cpu_quota_pct": quota,
        "thermal_governor": _conf_flag("NEXUS_THERMAL_GOVERNOR", "1"),
        "field_mode": "smooth_powered" if field_max else "standard",
    }


def _panel_rtx_meta() -> dict:
    field_max = _conf_flag("NEXUS_FIELD_MAX")
    rtx = _conf_flag("NEXUS_PANEL_RTX_ZERO")
    zero = _conf_flag("NEXUS_PANEL_ZERO_COST", "1" if rtx else "0")
    if field_max:
        rtx = False
        zero = False
    try:
        poll_scale = float(_conf_val("NEXUS_PANEL_ZERO_COST_POLL_SCALE", "1.25"))
    except ValueError:
        poll_scale = 1.25
    return {
        "panel_rtx_zero": rtx,
        "panel_zero_cost": zero,
        "panel_zero_cost_poll_scale": poll_scale,
        "panel_build": "underlay-f9",
    }


def _status_shell(*, full: bool = False) -> str:
    version = _read_install_version()
    if full:
        return "{}"
    shell = {
        "field": True,
        "panel_ready": False,
        "version": version,
        "gatekeeper": {"connections": [], "harm_candidates": 0},
    }
    shell.update(_panel_poll_meta(shell))
    shell.update(_panel_rtx_meta())
    shell.update(_panel_field_meta())
    return json.dumps(shell, ensure_ascii=False)


def _read_nexus_poll_seconds() -> dict[str, int]:
    """Adaptive panel poll intervals (seconds) — mirrors nexus.conf defaults."""
    conf = INSTALL_ROOT / "config" / "nexus.conf"
    out = {"calm": 5, "alert": 5, "storm": 3}
    if _conf_flag("NEXUS_FIELD_MAX"):
        return {"calm": 3, "alert": 2, "storm": 1}
    if not conf.is_file():
        return out
    try:
        for line in conf.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key in ("NEXUS_PANEL_POLL_CALM", "NEXUS_BEHAVIOR_POLL_CALM"):
                out["calm"] = max(2, int(val))
            elif key in ("NEXUS_PANEL_POLL_ALERT", "NEXUS_BEHAVIOR_POLL_ALERT"):
                out["alert"] = max(2, int(val))
            elif key in ("NEXUS_PANEL_POLL_STORM", "NEXUS_BEHAVIOR_POLL_STORM"):
                out["storm"] = max(2, int(val))
    except (OSError, ValueError):
        pass
    return out


def _panel_poll_meta(doc: dict | None = None) -> dict:
    base = doc if isinstance(doc, dict) else {}
    mode = str(base.get("vigil_mode") or "calm").lower()
    if mode not in ("calm", "alert", "storm"):
        mode = "calm"
    polls = _read_nexus_poll_seconds()
    sec = polls.get(mode, polls["calm"])
    return {
        "vigil_mode": mode,
        "poll_seconds": sec,
        "poll_ms": sec * 1000,
        "poll_intervals": polls,
    }


def _read_status_json(*, full: bool = False) -> str:
    if not STATUS_JSON.is_file():
        return _status_shell(full=full)
    raw = STATUS_JSON.read_text(encoding="utf-8").strip()
    if not raw:
        return _status_shell(full=full)
    if full:
        try:
            doc = json.loads(raw)
            if isinstance(doc, dict):
                doc.update(_panel_poll_meta(doc))
                doc.update(_panel_rtx_meta())
                doc.update(_panel_field_meta())
                return json.dumps(doc, ensure_ascii=False)
        except json.JSONDecodeError:
            pass
        return raw
    try:
        doc = json.loads(raw)
        if isinstance(doc, dict):
            version = _read_install_version()
            for key in PANEL_PARALLEL_KEYS:
                doc.pop(key, None)
            doc["version"] = version
            doc.update(_panel_poll_meta(doc))
            doc.update(_panel_rtx_meta())
            doc.update(_panel_field_meta())
            return json.dumps(doc, ensure_ascii=False)
    except json.JSONDecodeError:
        pass
    return _status_shell(full=full)


_PANEL_DOC_CACHE: dict | None = None
_PANEL_DOC_MTIME: float = -1.0


def _load_panel_doc() -> dict:
    global _PANEL_DOC_CACHE, _PANEL_DOC_MTIME
    if not STATUS_JSON.is_file():
        return {}
    try:
        mtime = STATUS_JSON.stat().st_mtime
    except OSError:
        return {}
    if _PANEL_DOC_CACHE is not None and mtime == _PANEL_DOC_MTIME:
        return _PANEL_DOC_CACHE
    try:
        raw = STATUS_JSON.read_text(encoding="utf-8")
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError:
            doc, _ = json.JSONDecoder().raw_decode(raw.lstrip())
        if isinstance(doc, dict):
            _PANEL_DOC_CACHE = doc
            _PANEL_DOC_MTIME = mtime
            return doc
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    return {}


def _slice_populated(key: str, val: dict) -> bool:
    if not isinstance(val, dict) or not val:
        return False
    if key == "host_attacks":
        return bool(val.get("updated")) or bool(val.get("schema")) or isinstance(val.get("points"), list)
    if key == "human_registry":
        return bool(val.get("table")) or bool(val.get("humans"))
    if key == "police_agency":
        return bool(val.get("agencies")) or bool(val.get("updated"))
    if key == "angel_research":
        tables = val.get("tables") or {}
        return any(isinstance(v, list) and v for v in tables.values()) or bool(val.get("updated"))
    if key == "census_field":
        return bool(val.get("last_run")) or bool(val.get("operator_gps_ready"))
    if key == "existence_identity":
        return bool(val.get("table")) or bool(val.get("updated"))
    if key == "gov_intel":
        return bool(val.get("records")) or val.get("record_count", 0) > 0
    if key == "program_tags":
        return bool(val.get("tags")) or bool(val.get("recent"))
    if key == "hostess7_command":
        return (
            val.get("schema") == "hostess7-command/v1"
            and (bool(val.get("intel_digest")) or bool(val.get("self_view")) or bool(val.get("transcript")))
        )
    return True


def _panel_slice(
    key: str,
    *,
    live: dict | None = None,
    default: dict | None = None,
) -> dict:
    """Zero-cost read: published field cache first, live builder only on miss."""
    doc = _load_panel_doc()
    val = doc.get(key)
    if isinstance(val, dict) and _slice_populated(key, val):
        out = dict(val)
        out["_field_cache"] = True
        out.setdefault("_incomplete", False)
        out.setdefault("_partial", False)
        return out
    live_ok = (
        isinstance(live, dict)
        and live
        and not live.get("error")
        and live.get("ok") is not False
    )
    if live_ok and (_slice_populated(key, live) or live.get("schema")):
        out = dict(live)
        out["_field_cache"] = False
        out.setdefault("_incomplete", False)
        out.setdefault("_partial", False)
        return out
    reason = "cache_miss_live_fail"
    if isinstance(live, dict) and live:
        reason = str(live.get("error") or live.get("detail") or "live_fail")
    out = dict(default or {})
    out["_incomplete"] = True
    out["_partial"] = True
    out["_slice_reason"] = reason
    out["_slice_key"] = key
    out.setdefault("ok", False)
    out.setdefault("error", reason)
    return out


_FIELD_PANEL_FILES: dict[str, Path] = {
    "field_dns": STATE_DIR / "field-dns-panel.json",
    "field_dhcp": STATE_DIR / "field-dhcp-panel.json",
}


def _read_field_panel_file(key: str) -> dict | None:
    fp = _FIELD_PANEL_FILES.get(key)
    if not fp or not fp.is_file():
        return None
    try:
        doc = json.loads(fp.read_text(encoding="utf-8"))
        if isinstance(doc, dict) and doc.get("schema"):
            out = dict(doc)
            out["_field_cache"] = True
            out.setdefault("_incomplete", False)
            out.setdefault("_partial", False)
            return out
    except (OSError, json.JSONDecodeError):
        pass
    return None


def _sudo_available() -> bool:
    if os.geteuid() == 0:
        return True
    try:
        proc = subprocess.run(
            ["sudo", "-n", "true"],
            capture_output=True,
            timeout=5,
            check=False,
        )
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _read_state_json(name: str, default: dict) -> dict:
    fp = STATE_DIR / name
    if not fp.is_file():
        return default
    try:
        doc = json.loads(fp.read_text(encoding="utf-8"))
        return doc if isinstance(doc, dict) else default
    except (OSError, json.JSONDecodeError):
        return default


def _nexus_shell_json_fn(fn: str, *, sources: list[str] | None = None, timeout: int = 25) -> dict:
    sources = sources or []
    src = " && ".join(f"source '{INSTALL_ROOT}/lib/{s}'" for s in sources)
    inner = (
        f"source '{INSTALL_ROOT}/lib/nexus-common.sh' && nexus_load_config"
        f"{(' && ' + src) if src else ''} && {fn}"
    )
    ok, out = _run_nexus_bash(inner, timeout=timeout)
    if not ok or not (out or "").strip():
        return {}
    try:
        doc = json.loads(out)
        return doc if isinstance(doc, dict) else {}
    except json.JSONDecodeError:
        return {}


def _run_nexus_undo(action_id: str) -> bool:
    script = INSTALL_ROOT / "lib" / "threat-autosanitize.sh"
    if not script.is_file():
        return False
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    cmd = (
        f"source {INSTALL_ROOT}/lib/nexus-common.sh && "
        f"source {INSTALL_ROOT}/lib/firewall-sentinel.sh && "
        f"source {script} && "
        f"nexus_autosanitize_undo {action_id}"
    )
    proc = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True,
        text=True,
        timeout=15,
        env=env,
    )
    return proc.returncode == 0


def _run_nexus_paranoia(cmd: str, arg: str = "") -> bool:
    script = INSTALL_ROOT / "lib" / "paranoia-mode.sh"
    if not script.is_file():
        return False
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    inner = (
        f"source {INSTALL_ROOT}/lib/nexus-common.sh && "
        f"source {INSTALL_ROOT}/lib/firewall-sentinel.sh && "
        f"source {INSTALL_ROOT}/lib/threat-vectors.sh && "
        f"source {INSTALL_ROOT}/lib/packet-oracle.sh && "
        f"source {INSTALL_ROOT}/lib/eternal-vigil.sh && "
        f"source {script} && "
    )
    if cmd == "block_on":
        inner += "nexus_paranoia_set_block 1"
    elif cmd == "block_off":
        inner += "nexus_paranoia_set_block 0"
    elif cmd == "mode_on":
        inner += "nexus_paranoia_set_mode 1"
    elif cmd == "mode_off":
        inner += "nexus_paranoia_set_mode 0"
    elif cmd == "disable" and arg:
        safe = arg.replace("'", "'\"'\"'")
        inner += f"nexus_paranoia_disable_incident '{safe}'"
    elif cmd == "reenable" and arg:
        safe = arg.replace("'", "'\"'\"'")
        inner += f"nexus_paranoia_reenable_incident '{safe}'"
    else:
        return False
    proc = subprocess.run(
        ["bash", "-c", inner],
        capture_output=True,
        text=True,
        timeout=20,
        env=env,
    )
    return proc.returncode == 0


def _run_nexus_firewall_trust(cmd: str, ip: str, direction: str = "out", label: str = "") -> bool:
    script = INSTALL_ROOT / "lib" / "firewall-trust.sh"
    if not script.is_file():
        return False
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    inner = (
        f"source {INSTALL_ROOT}/lib/nexus-common.sh && nexus_load_config && "
        f"source {INSTALL_ROOT}/lib/firewall-sentinel.sh && "
        f"source {script} && "
    )
    safe_ip = ip.replace("'", "'\"'\"'")
    safe_label = label.replace("'", "'\"'\"'")
    if cmd == "authorize":
        inner += f"nexus_firewall_authorize_ip '{safe_ip}' '{direction}' '{safe_label}' 'nexus-panel'"
    elif cmd == "revoke":
        inner += f"nexus_firewall_revoke_trust '{safe_ip}' '{direction}'"
    else:
        return False
    proc = subprocess.run(
        ["bash", "-c", inner],
        capture_output=True,
        text=True,
        timeout=20,
        env=env,
    )
    return proc.returncode == 0


def _run_nexus_bash(inner: str, timeout: int = 30) -> tuple[bool, str]:
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    proc = subprocess.run(
        ["bash", "-c", inner],
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    detail = (proc.stderr or proc.stdout or "").strip()[:400]
    return proc.returncode == 0, detail


def _load_nexus_shield_source() -> str:
    src = os.environ.get("NEXUS_SHIELD_SOURCE", "").strip()
    if src:
        return src
    conf = INSTALL_ROOT / "config" / "nexus.conf"
    if conf.is_file():
        try:
            for line in conf.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if line.startswith("NEXUS_SHIELD_SOURCE="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
        except OSError:
            pass
    return ""


def _resolve_nexus_source_root() -> Path | None:
    """Locate git/dev tree with install-all.sh for UPDATE git fallback."""
    candidates: list[Path] = []
    src = _load_nexus_shield_source()
    if src:
        candidates.append(Path(src))
    candidates.extend([
        INSTALL_ROOT,
        INSTALL_ROOT.parent,
    ])
    staging = STATE_DIR / "update-staging"
    if staging.is_dir():
        for child in sorted(staging.glob("extract-*"), reverse=True):
            if (child / "install-all.sh").is_file() or any(child.rglob("install-all.sh")):
                candidates.append(child)
    seen: set[str] = set()
    for base in candidates:
        if not base:
            continue
        try:
            resolved = base.resolve()
        except OSError:
            continue
        key = str(resolved)
        if key in seen:
            continue
        seen.add(key)
        cur = resolved
        for _ in range(6):
            for name in ("install-all.sh", "stealth_install.sh"):
                install = cur / name
                if install.is_file():
                    return cur
            parent = cur.parent
            if parent == cur:
                break
            cur = parent
    return None


def _nexus_update_check(force: bool = False) -> dict:
    script = INSTALL_ROOT / "lib" / "nexus-update.py"
    if not script.is_file():
        return {"ok": False, "error": "update_checker_missing"}
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    args = [sys.executable, str(script)]
    if force:
        args.append("--force")
    proc = subprocess.run(args, capture_output=True, text=True, timeout=30, env=env)
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": "update_check_failed", "detail": (proc.stderr or "")[:200]}


def _nexus_update_lock(args: list[str], timeout: int = 15) -> dict:
    return _nexus_py_json(INSTALL_ROOT / "lib" / "nexus-update-lock.py", args, timeout=timeout)


def _nexus_update_needs_sudo() -> dict | None:
    fp = STATE_DIR / "update-needs-sudo.json"
    if not fp.is_file():
        return None
    try:
        doc = json.loads(fp.read_text(encoding="utf-8"))
        return doc if isinstance(doc, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _spawn_nexus_update_apply(
    *,
    git_dir: Path | None,
    install_sh: Path | None,
    token: str,
    target: str,
    previous: str,
    tarball_url: str = "",
    update_mode: str = "release",
) -> bool:
    apply_sh = INSTALL_ROOT / "lib" / "nexus-update-apply.sh"
    if not apply_sh.is_file() and git_dir:
        apply_sh = git_dir / "lib" / "nexus-update-apply.sh"
    if not apply_sh.is_file():
        return False
    work_cwd = str(git_dir) if git_dir else str(INSTALL_ROOT)
    log_fp = STATE_DIR / "update-apply.log"
    try:
        log_fp.parent.mkdir(parents=True, exist_ok=True)
        with log_fp.open("a", encoding="utf-8") as lf:
            lf.write(f"\n--- panel spawn update ---\n")
    except OSError:
        pass
    env = os.environ.copy()
    env.update({
        "NEXUS_INSTALL_ROOT": str(INSTALL_ROOT),
        "NEXUS_STATE_DIR": str(STATE_DIR),
        "NEXUS_UPDATE_LOCK_TOKEN": token,
        "NEXUS_UPDATE_TARGET": target,
        "NEXUS_UPDATE_PREVIOUS": previous,
        "NEXUS_UPDATE_MODE": update_mode or "release",
    })
    if tarball_url:
        env["NEXUS_UPDATE_TARBALL_URL"] = tarball_url
    if git_dir:
        env["NEXUS_UPDATE_GIT_DIR"] = str(git_dir)
    if install_sh and install_sh.is_file():
        env["NEXUS_UPDATE_INSTALL_SH"] = str(install_sh)
    for key in ("DISPLAY", "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR", "XDG_CURRENT_DESKTOP", "DBUS_SESSION_BUS_ADDRESS"):
        if key in os.environ:
            env[key] = os.environ[key]
    try:
        with log_fp.open("a", encoding="utf-8") as lf:
            subprocess.Popen(
                ["bash", str(apply_sh)],
                stdout=lf,
                stderr=subprocess.STDOUT,
                env=env,
                start_new_session=True,
                cwd=work_cwd,
            )
        return True
    except OSError:
        return False


def _nexus_shell_publish_panel() -> None:
    script = INSTALL_ROOT / "lib" / "threat-panel.sh"
    if not script.is_file():
        return
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    env["NEXUS_THREAT_PANEL"] = "1"
    subprocess.run(
        [
            "bash", "-c",
            (
                f"source '{INSTALL_ROOT}/lib/nexus-common.sh' && "
                f"source '{script}' && "
                f"nexus_threat_panel_publish"
            ),
        ],
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
    )


def _queen_boot_script() -> Path:
    qr = os.environ.get("QUEEN_ROOT")
    if qr:
        p = Path(qr) / "lib" / "queen-field-boot.py"
        if p.is_file():
            return p
    p = INSTALL_ROOT / "lib" / "queen-field-boot.py"
    if p.is_file():
        return p
    return INSTALL_ROOT.parent / "Queen" / "lib" / "queen-field-boot.py"


def _grok_build_script() -> Path:
    qr = os.environ.get("QUEEN_ROOT")
    if qr:
        p = Path(qr) / "lib" / "grok-build-bridge.py"
        if p.is_file():
            return p
    p = INSTALL_ROOT / "lib" / "grok-build-bridge.py"
    if p.is_file():
        return p
    return INSTALL_ROOT.parent / "Queen" / "lib" / "grok-build-bridge.py"


def _queen_build_script() -> Path:
    qr = os.environ.get("QUEEN_ROOT")
    if qr:
        p = Path(qr) / "lib" / "queen-build.py"
        if p.is_file():
            return p
    p = INSTALL_ROOT / "lib" / "queen-build.py"
    if p.is_file():
        return p
    return INSTALL_ROOT.parent / "Queen" / "lib" / "queen-build.py"


def _queen_root() -> Path:
    qr = os.environ.get("QUEEN_ROOT", "").strip()
    if qr:
        p = Path(qr)
        if p.is_dir():
            return p
    inside = INSTALL_ROOT / ".queen-inside"
    if inside.is_file():
        return INSTALL_ROOT
    candidate = INSTALL_ROOT.parent / "Queen"
    if candidate.is_dir():
        return candidate
    return INSTALL_ROOT


def _queen_eyeball_script() -> Path:
    p = _queen_root() / "lib" / "queen-eyeball.py"
    return p if p.is_file() else INSTALL_ROOT.parent / "Queen" / "lib" / "queen-eyeball.py"


def _field_stack_env() -> dict[str, str]:
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    sg = INSTALL_ROOT.parent if INSTALL_ROOT.name == "NewLatest" else INSTALL_ROOT.parent.parent
    env.setdefault("SG_ROOT", str(sg))
    env.setdefault("QUEEN_ROOT", str(_queen_root()))
    env.setdefault("FINAL_EYE_ROOT", str(sg / "Final_Eye"))
    env.setdefault("HOSTESS7_ROOT", str(INSTALL_ROOT / "Hostess7"))
    return env


def _nexus_py_json(script: Path, args: list[str], timeout: int = 25) -> dict:
    if not script.is_file():
        return {"ok": False, "error": "script_missing"}
    env = _field_stack_env()
    env.setdefault("NEXUS_PROBE_DEPTH", "1")
    try:
        proc = subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout", "script": script.name}
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": "script_failed", "detail": (proc.stderr or "")[:200]}


_FIELD_OPERATOR_MOD: Any = None


def _field_operator_inproc():
    global _FIELD_OPERATOR_MOD
    if _FIELD_OPERATOR_MOD is not None:
        return _FIELD_OPERATOR_MOD
    import importlib.util

    op_py = INSTALL_ROOT / "lib" / "field-operator.py"
    if not op_py.is_file():
        return None
    spec = importlib.util.spec_from_file_location("field_operator_panel", op_py)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        mod.copilot(reload=True)
    except Exception:
        pass
    _FIELD_OPERATOR_MOD = mod
    return mod


def _field_operator_copilot_route(target: str, *, override: str | None = None) -> dict:
    mod = _field_operator_inproc()
    if mod is None:
        return _nexus_py_json(INSTALL_ROOT / "lib" / "field-operator.py", ["route", target], timeout=3)
    if override:
        return mod.route_to_board(target, override=override)
    return mod.copilot_route(target)


def _field_operator_copilot_batch(batch: list[str], *, override: str | None = None) -> dict:
    mod = _field_operator_inproc()
    if mod is None:
        args = ["route-batch", *[str(x) for x in batch if x]]
        return _nexus_py_json(INSTALL_ROOT / "lib" / "field-operator.py", args, timeout=5)
    if override:
        return mod.route_batch(batch, override=override)
    return mod.copilot_batch(batch)


def _field_operator_copilot_status() -> dict:
    mod = _field_operator_inproc()
    if mod is None:
        return _nexus_py_json(INSTALL_ROOT / "lib" / "field-operator.py", ["copilot"], timeout=8)
    return mod.copilot_status()


def _jockey_json(args: list[str], timeout: int = 25) -> dict:
    return _nexus_py_json(INSTALL_ROOT / "lib" / "monitor-jockey.py", args, timeout=timeout)


def _kill_codes_json(args: list[str], timeout: int = 45) -> dict:
    return _nexus_py_json(INSTALL_ROOT / "lib" / "kill-codes.py", args, timeout=timeout)


def _field_plate_script() -> Path:
    if os.environ.get("NEXUS_FIELD_PLATES", "1") == "1":
        p = INSTALL_ROOT / "lib" / "field-panel-field.py"
        if p.is_file():
            return p
    return INSTALL_ROOT / "lib" / "field-panel-parallel.py"


def _field_parallel_payload(*, publish: bool = False) -> dict:
    """Serve stored threat-panel.json; field amplitude publish when publish=1 or store empty."""
    try:
        stale = not STATUS_JSON.is_file() or STATUS_JSON.stat().st_size < 128
    except OSError:
        stale = True
    if publish or stale:
        return _nexus_py_json(_field_plate_script(), ["json"], timeout=120)
    doc = _load_panel_doc()
    keys = [
        k
        for k in doc
        if not str(k).startswith("_") and k not in ("field", "parallel_load", "field_load")
    ]
    return {
        "ok": True,
        "stored": True,
        "mode": "field" if doc.get("field_load") else "legacy",
        "infinite_dimension": bool(doc.get("infinite_dimension")),
        "field_amplitude": doc.get("field_amplitude"),
        "panel": doc,
        "slice_count": len(keys),
        "field_slices_updated": keys,
        "field_slices_failed": [],
    }


def _field_field_payload(*, publish: bool = False) -> dict:
    """Canonical field plate route — infinite dimension amplitude process."""
    return _field_parallel_payload(publish=publish)


def _nexus_host_map_trash_add(pin_id: str) -> bool:
    pin_id = str(pin_id or "").strip()
    if not pin_id:
        return False
    trash_sh = INSTALL_ROOT / "lib" / "host-map-trash.sh"
    if not trash_sh.is_file():
        return False
    safe = pin_id.replace("'", "'\"'\"'")
    inner = (
        f"source {INSTALL_ROOT}/lib/nexus-common.sh && nexus_load_config && "
        f"source {trash_sh} && nexus_host_map_trash_add '{safe}'"
    )
    ok, _ = _run_nexus_bash(inner, timeout=15)
    return ok


def _nexus_shell_prelude() -> str:
    return (
        f"source {INSTALL_ROOT}/lib/nexus-common.sh && nexus_load_config && "
        f"source {INSTALL_ROOT}/lib/firewall-sentinel.sh && "
        f"source {INSTALL_ROOT}/lib/threat-autosanitize.sh && "
        f"source {INSTALL_ROOT}/lib/paranoia-mode.sh && "
        f"source {INSTALL_ROOT}/lib/nexus-settings.sh && "
        f"source {INSTALL_ROOT}/lib/adblock-loader.sh && "
    )


def _run_nexus_settings_set(key: str, val: str) -> bool:
    script = INSTALL_ROOT / "lib" / "nexus-settings.sh"
    if not script.is_file():
        return False
    safe_key = key.replace("'", "'\"'\"'")
    inner = _nexus_shell_prelude() + f"nexus_settings_set '{safe_key}' '{val}'"
    ok, _ = _run_nexus_bash(inner, timeout=45)
    return ok


def _run_nexus_adblock_load(preset: str = "", url: str = "") -> bool:
    script = INSTALL_ROOT / "lib" / "adblock-loader.sh"
    if not script.is_file():
        return False
    inner = _nexus_shell_prelude()
    if preset:
        safe = preset.replace("'", "'\"'\"'")
        inner += f"nexus_adblock_load_preset '{safe}'"
    elif url:
        safe = url.replace("'", "'\"'\"'")
        inner += f"nexus_adblock_load_url '{safe}'"
    else:
        return False
    ok, _ = _run_nexus_bash(inner, timeout=180)
    return ok


def _run_nexus_adblock_apply() -> bool:
    script = INSTALL_ROOT / "lib" / "adblock-loader.sh"
    if not script.is_file():
        return False
    inner = _nexus_shell_prelude() + "nexus_adblock_apply"
    ok, _ = _run_nexus_bash(inner, timeout=120)
    return ok


def _run_nexus_autosanitize_toggle(enabled: bool) -> bool:
    script = INSTALL_ROOT / "lib" / "threat-autosanitize.sh"
    if not script.is_file():
        return False
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
    val = "1" if enabled else "0"
    cmd = (
        f"source {INSTALL_ROOT}/lib/nexus-common.sh && "
        f"source {script} && "
        f"nexus_autosanitize_set_enabled {val}"
    )
    proc = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )
    return proc.returncode == 0


def _tail_file(path: Path, lines: int = 120) -> str:
    if not path.is_file():
        return ""
    try:
        data = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(data[-lines:])
    except OSError:
        return ""


def _panel_static_mime(path: Path) -> str:
    ext = path.suffix.lower()
    return {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".woff2": "font/woff2",
    }.get(ext, "application/octet-stream")


def _serve_panel_html(handler: "Handler", target: Path) -> None:
    if target.suffix == ".html" and target.name == "threat-panel.html":
        try:
            body = target.read_text(encoding="utf-8")
        except OSError:
            handler._send(404, "not found", "text/plain")
            return
        handler._send(200, body, "text/html; charset=utf-8")
        return
    try:
        handler._send(200, target.read_bytes(), _panel_static_mime(target))
    except OSError:
        handler._send(404, "not found", "text/plain")


class Handler(BaseHTTPRequestHandler):
    server_version = "NEXUS-Panel/10"
    sys_version = ""

    def log_message(self, *_):
        return

    @staticmethod
    def _peer_loopback(handler: "Handler") -> bool:
        peer = handler.client_address[0] if handler.client_address else ""
        return peer in _LOOPBACK_CLIENTS or str(peer).startswith("127.")

    def handle(self):
        if not self._peer_loopback(self):
            try:
                self.request.sendall(b"HTTP/1.0 403 Forbidden\r\nConnection: close\r\n\r\n")
            except OSError:
                pass
            return
        super().handle()

    def _send(self, code, body, ctype, extra_headers: dict[str, str] | None = None):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Permissions-Policy",
            "camera=(), microphone=(), display-capture=(), clipboard-read=(), geolocation=()",
        )
        self.send_header("X-Admin-Shield", "keyboard-hooks-blocked")
        self.send_header("X-Smart-Wire", "nexus-keyboard-no-middleman")
        self.send_header("X-Hardware-Wire", "nexus-field-hardware-hooks")
        if extra_headers:
            for hk, hv in extra_headers.items():
                self.send_header(hk, hv)
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    def do_GET(self):
        path = unquote(self.path.split("?", 1)[0])
        query = parse_qs(urlparse(self.path).query)

        if path == "/api/status":
            full = str(query.get("full", ["0"])[0]).strip().lower() in ("1", "true", "yes")
            self._send(200, _read_status_json(full=full), "application/json")
            return

        if path == "/api/nexus-field":
            try:
                store_ready = STATUS_JSON.is_file() and STATUS_JSON.stat().st_size >= 128
            except OSError:
                store_ready = False
            if not store_ready:
                _nexus_shell_publish_panel()
            self._send(200, _read_status_json(full=True), "application/json")
            return

        if path == "/api/threat-panel.json":
            if STATUS_JSON.is_file():
                self._send(200, STATUS_JSON.read_text(encoding="utf-8"), "application/json")
            else:
                self._send(200, "{}", "application/json")
            return

        if path == "/api/gatekeeper":
            payload = _panel_slice(
                "gatekeeper",
                live=_read_state_json(
                    "connection-intent.json",
                    {"connections": [], "harm_candidates": 0, "why_no_auto_block": "No live flows cataloged yet."},
                ),
                default={"connections": [], "harm_candidates": 0},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/host-attacks":
            payload = _panel_slice(
                "host_attacks",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "host-attack-map.py", ["json-panel"]),
                default={"schema": "host-attacks/v1", "points": [], "updated": None, "stats": {"total": 0}},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/us-field":
            payload = _panel_slice(
                "us_field",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-us-intel.py", ["json"]),
                default={"title": "US Field", "page": {}},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-command":
            payload = _panel_slice(
                "field_command",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-command.py", ["json"]),
                default={"good_guy": {"count": 0}, "bad_guy": {"count": 0}, "pulse": {}},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/packet-field":
            payload = _panel_slice(
                "packet_field",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "packet-field.py", ["json"]),
                default={"recent": [], "ports": [], "field_graphics": {}},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/port-ddos":
            payload = _panel_slice(
                "port_ddos_shield",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-port-ddos-shield.py", ["json"]),
                default={"verdict": "GREEN", "ports": [], "wifi": [], "wave_view": {}},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/port-ddos/cycle":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-port-ddos-shield.py", ["cycle"], timeout=45)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/packet-deinterlace":
            payload = _panel_slice(
                "packet_deinterlace",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-packet-deinterlace.py", ["json"]),
                default={"lanes": [], "processed": 0, "secure": 0},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/packet-deinterlace/cycle":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-packet-deinterlace.py", ["cycle"], timeout=60)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/connectivity-laws":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-packet-deinterlace.py", ["laws"], timeout=15)
            self._send(200, json.dumps(payload or {"laws": []}), "application/json")
            return

        if path == "/api/angel-dossiers":
            payload = _read_state_json(
                "angel-dossiers.json",
                {"dossier_count": 0, "dossiers": [], "motto": "Let's Be Angels"},
            )
            if not payload.get("dossiers"):
                built = _nexus_py_json(INSTALL_ROOT / "lib" / "angel-dossier.py", ["dossiers"], timeout=45)
                if built:
                    payload = built
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/angel-research":
            payload = _read_state_json(
                "angel-research.json",
                {"tables": {"mac_vendors": [], "ip_intel": [], "exploit_cve_map": [], "attack_paths": []}},
            )
            if not payload.get("tables"):
                built = _nexus_py_json(INSTALL_ROOT / "lib" / "angel-dossier.py", ["research"], timeout=45)
                if built:
                    payload = built
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/human-dossier":
            fp = DATA_FILES.get("human-dossier")
            if fp and fp.is_file():
                self._send(200, fp.read_text(encoding="utf-8"), "application/json")
                return
            payload = _nexus_shell_json_fn(
                "nexus_human_dossier_json",
                sources=["human-dossier.sh"],
            )
            if not payload:
                payload = {"dossier_version": "7.0", "ip_count": 0, "ips": [], "analyst": "Grok Heavy"}
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/settings":
            payload = _panel_slice(
                "settings",
                live=_nexus_shell_json_fn("nexus_settings_json", sources=["nexus-settings.sh"]),
                default={},
            )
            self._send(200, json.dumps(payload or {}), "application/json")
            return

        if path in ("/api/update/check", "/api/update/status"):
            force = str(query.get("force", ["0"])[0]).strip() in ("1", "true", "yes")
            payload = _nexus_update_check(force=force)
            lock = _nexus_update_lock(["status"])
            payload["update_lock"] = lock
            payload["update_in_progress"] = bool(lock.get("locked"))
            needs_sudo = _nexus_update_needs_sudo()
            if needs_sudo:
                payload["needs_sudo"] = True
                payload["sudo_prompt"] = needs_sudo
            if lock.get("locked"):
                payload["update_available"] = False
                payload["message"] = lock.get("message") or "Update in progress"
            elif needs_sudo:
                payload["message"] = needs_sudo.get("message") or "Administrator password required"
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-toolkit":
            attack_id = str(query.get("id", [""])[0]).strip()
            script = INSTALL_ROOT / "lib" / "field-toolkit-db.py"
            if attack_id:
                payload = _nexus_py_json(script, ["get", attack_id])
            else:
                payload = _nexus_py_json(script, ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/hostile-ai":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostile-ai-destroy.py", ["json"], timeout=45)
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/planetary-observer":
            payload = _panel_slice(
                "planetary_observer",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "planetary-observer.py", ["json"], timeout=60),
                default={"schema": "planetary-observer/v1", "globe": {"total_targets": 0}, "wire": {}},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/operator/location":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "operator-location.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/honorability":
            payload = _panel_slice(
                "browser_awareness",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "browser-awareness.py", ["json"]),
                default={"honorability": {}, "active_sites": []},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/queen-browser":
            payload = _panel_slice(
                "field_queen_browser",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-queen-browser.py", ["json"]),
                default={"queen_verdict": "QUEEN_WARMING", "gates": {"all_held": True}},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/logic-gate":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "nexus-logic-gate.py", ["json"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/queen/root-threats":
            qr = _queen_root()
            script = qr / "lib" / "queen-root-threats.py"
            if script.is_file():
                payload = _nexus_py_json(script, ["json"], timeout=20)
            else:
                payload = {"ok": False, "error": "queen_root_threats_missing"}
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-stack":
            payload = _panel_slice(
                "field_stack",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "queen_field_nexus.py", ["json"], timeout=120),
                default={"schema": "nexus-field-stack/v1", "queen_verdict": "QUEEN_WARMING"},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/admin-shield":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "admin-window-shield.py", ["json"], timeout=20)
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/hardware-wire":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hardware-wire.py", ["json"], timeout=25)
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/smart-wire":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "smart-wire.py", ["json"], timeout=25)
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/front-hook":
            hook_file = STATE_DIR / "front-hook.json"
            if hook_file.is_file():
                try:
                    self._send(200, hook_file.read_text(encoding="utf-8"), "application/json")
                    return
                except OSError:
                    pass
            self._send(
                200,
                json.dumps({
                    "schema": "nexus-front-hook/v1",
                    "boarded": False,
                    "owner": "nexus",
                    "pass_through": False,
                    "policy": "front_hook_never_pass_off",
                }),
                "application/json",
            )
            return

        if path == "/api/ai-integration":
            peer = self.client_address[0] if self.client_address else "127.0.0.1"
            payload = _ai_integration_json(peer=str(peer))
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/native-layer":
            query = parse_qs(urlparse(self.path).query)
            audit = str(query.get("audit", ["0"])[0]).strip().lower() in ("1", "true", "yes")
            payload = _native_layer_json(audit=audit)
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/cpu-vulnerability":
            query = parse_qs(urlparse(self.path).query)
            apply = str(query.get("apply", ["0"])[0]).strip().lower() in ("1", "true", "yes")
            payload = _cpu_vulnerability_json(apply=apply)
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-polkit":
            payload = _field_polkit_json()
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-underlay":
            payload = _field_underlay_json()
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-operator":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "field-operator.py",
                ["board", "--no-hw-wire"],
                timeout=15,
            )
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-operator/scan":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-operator.py", ["scan"], timeout=10)
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-operator/clock":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-operator.py", ["clock"], timeout=8)
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-operator/route":
            query = parse_qs(urlparse(self.path).query)
            target = str(query.get("id") or query.get("target") or [""])[0].strip()
            if not target:
                self._send(400, json.dumps({"ok": False, "error": "missing id"}), "application/json")
                return
            payload = _field_operator_copilot_route(target)
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-operator/copilot":
            payload = _field_operator_copilot_status()
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-bus":
            payload = _panel_slice(
                "field_bus",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-unified-bus.py", ["json"]),
                default={"bus_size": 64, "data_bus": [], "lanes": []},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-bus/cycle":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-unified-bus.py", ["cycle"], timeout=45)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/field-bus/copilot":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-unified-bus.py", ["copilot"], timeout=15)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/universal-protector", "/api/universal-protector/status"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "universal-protector.py", ["json"], timeout=30)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/universal-protector/meld":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "universal-protector.py", ["meld"], timeout=90)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/field-spatial", "/api/spatial-field"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-spatial-cognition.py", ["json"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/humanoid-motion", "/api/humanoid-motion/status"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "humanoid-motion-training.py", ["json"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/humanoid-motion/catalog":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "humanoid-motion-training.py", ["catalog"], timeout=15)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/humanoid-motion/wireframe":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "humanoid-motion-training.py", ["wireframe"], timeout=30)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/humanoid-motion/data-all", "/api/humanoid-motion/data"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "humanoid-motion-training.py", ["data-all"], timeout=45)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/plate-meld":
            refresh = str(query.get("refresh", ["0"])[0]).strip().lower() in ("1", "true", "yes")
            cached = _load_plate_meld_cached()
            if not refresh:
                if cached.get("schema"):
                    self._send(200, json.dumps(cached), "application/json")
                    return
                self._send(
                    200,
                    json.dumps({
                        "schema": "field-plate-meld/v1",
                        "ok": False,
                        "error": "meld_not_published",
                        "hint": "POST /api/plate-meld/cycle or wait for vigil meld tick",
                    }),
                    "application/json",
                )
                return
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "field-plate-meld.py",
                ["meld"],
                timeout=180,
            )
            if not payload or not payload.get("schema"):
                if cached.get("schema"):
                    payload = cached
            self._send(200, json.dumps(payload or {"ok": False, "error": "meld_unavailable"}), "application/json")
            return

        if path == "/api/plate-meld/cycle":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "field-plate-meld.py",
                ["meld"],
                timeout=180,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/iron-plate/motion-resolve", "/api/iron-plate/resolve"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "iron-plate-motion-resolve.py", ["resolve"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/iron-plate/goals":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "iron-plate-motion-resolve.py", ["goals"], timeout=20)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/iron-plate/assemblage":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "iron-plate-motion-resolve.py", ["assemblage"], timeout=20)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/iron-plate/full-meld", "/api/full-assemblage-meld"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "iron-plate-motion-resolve.py", ["full-meld"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/brain-guard", "/api/hostess7-brain-guard"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-brain-guard.py", ["json"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/brain-guard/verify":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-brain-guard.py", ["verify"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/brain-guard/witness", "/api/hostess7-brain-guard/witness"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-brain-guard.py", ["witness"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/self-view", "/api/hostess7-self-view"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-self-view.py", ["json"], timeout=60)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/appearance", "/api/hostess7-operator-appearance"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-self-view.py", ["deliver"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/core-of-truth", "/api/hostess7-core-of-truth"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-self-view.py", ["truth"], timeout=45)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/operator-lookup", "/api/hostess7-operator-lookup"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-self-view.py", ["lookup"], timeout=45)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/programming", "/api/hostess7-programming"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-programming.py", ["json"], timeout=30)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/programming/explain":
            qparams = parse_qs(urlparse(self.path).query)
            q = (qparams.get("q") or qparams.get("query") or [""])[0]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-programming.py",
                ["explain", str(q or "better than assistant")],
                timeout=25,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/g16", "/api/hostess7-g16"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-g16.py", ["json"], timeout=35)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/codecraft", "/api/hostess7-codecraft"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-codecraft.py", ["json"], timeout=90)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/codecraft/explain":
            qparams = parse_qs(urlparse(self.path).query)
            q = (qparams.get("q") or qparams.get("query") or [""])[0]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-codecraft.py",
                ["teach", str(q or "codecraft mastery")],
                timeout=45,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/codecraft/testing-center":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-codecraft.py",
                ["testing-center", "--fast"],
                timeout=180,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/ironclad", "/api/ironclad/plate"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "ironclad-plate.py", ["json"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/ironclad/grounding", "/api/ironclad/bible"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "ironclad-plate.py", ["grounding"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/ironclad/verify":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "ironclad-plate.py", ["verify"], timeout=15)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/training", "/api/hostess7-training"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-training.py", ["json"], timeout=30)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/training/bundle", "/api/hostess7-training/bundle"):
            refresh = str(query.get("refresh", ["0"])[0]).strip().lower() in ("1", "true", "yes")
            cache_path = STATE_DIR / "hostess7-training-bundle-cache.json"
            if not refresh and cache_path.is_file():
                try:
                    cached = json.loads(cache_path.read_text(encoding="utf-8"))
                    if isinstance(cached, dict) and cached.get("schema"):
                        cached["_panel_cache"] = True
                        self._send(200, json.dumps(cached), "application/json")
                        return
                except (OSError, json.JSONDecodeError):
                    pass
            args = ["bundle"] + (["--refresh"] if refresh else [])
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-training-bundle.py", args, timeout=60)
            if isinstance(payload, dict) and payload.get("schema"):
                try:
                    cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                except OSError:
                    pass
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/training/runtime", "/api/hostess7-training/runtime"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-training.py", ["runtime"], timeout=10)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/training/graphs", "/api/hostess7-training/graphs"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-training.py", ["graphs"], timeout=45)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/training/complete":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-training.py", ["complete"], timeout=600)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/calculator", "/api/hostess7-calculator"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-calculator.py", ["json"], timeout=60)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/calculator/ocr-ingest":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-calculator.py", ["ocr-ingest"], timeout=120)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/calculator/ocr-train":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-calculator.py", ["ocr-train"], timeout=180)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/calculator/ocr-status":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-calculator.py", ["ocr-status"], timeout=30)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/calculator/compute":
            qparams = parse_qs(urlparse(self.path).query)
            q = (qparams.get("q") or qparams.get("query") or [""])[0]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-calculator.py",
                ["calc", str(q or "2+2")],
                timeout=45,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/calculator/explain":
            qparams = parse_qs(urlparse(self.path).query)
            q = (qparams.get("q") or qparams.get("query") or [""])[0]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-calculator.py",
                ["teach", str(q or "perfect calculator")],
                timeout=30,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/biology", "/api/hostess7-biology"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-biology.py", ["json"], timeout=60)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/biology/ocr-ingest":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-biology.py", ["ocr-ingest"], timeout=120)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/biology/ocr-train":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-biology.py", ["ocr-train"], timeout=180)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/biology/ocr-status":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-biology.py", ["ocr-status"], timeout=30)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/biology/search":
            qparams = parse_qs(urlparse(self.path).query)
            q = (qparams.get("q") or qparams.get("query") or [""])[0]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-biology.py",
                ["search", str(q or "mitochondria")],
                timeout=45,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/biology/explain":
            qparams = parse_qs(urlparse(self.path).query)
            q = (qparams.get("q") or qparams.get("query") or [""])[0]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-biology.py",
                ["teach", str(q or "biology fluency")],
                timeout=30,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/engineering", "/api/hostess7-engineering"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-engineering.py", ["json"], timeout=60)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/engineering/ocr-ingest":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-engineering.py", ["ocr-ingest"], timeout=120)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/engineering/ocr-train":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-engineering.py", ["ocr-train"], timeout=180)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/engineering/ocr-status":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-engineering.py", ["ocr-status"], timeout=30)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/engineering/search":
            qparams = parse_qs(urlparse(self.path).query)
            q = (qparams.get("q") or qparams.get("query") or [""])[0]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-engineering.py",
                ["search", str(q or "torque gear ratio")],
                timeout=45,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/engineering/explain":
            qparams = parse_qs(urlparse(self.path).query)
            q = (qparams.get("q") or qparams.get("query") or [""])[0]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-engineering.py",
                ["teach", str(q or "engineering fluency")],
                timeout=30,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/combat", "/api/hostess7-combat"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-combat.py", ["json"], timeout=60)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/combat/ocr-ingest":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-combat.py", ["ocr-ingest"], timeout=120)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/combat/ocr-train":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-combat.py", ["ocr-train"], timeout=180)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/combat/ocr-status":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-combat.py", ["ocr-status"], timeout=30)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/combat/search":
            qparams = parse_qs(urlparse(self.path).query)
            q = (qparams.get("q") or qparams.get("query") or [""])[0]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-combat.py",
                ["search", str(q or "mma sprawl")],
                timeout=45,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/combat/explain":
            qparams = parse_qs(urlparse(self.path).query)
            q = (qparams.get("q") or qparams.get("query") or [""])[0]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-combat.py",
                ["teach", str(q or "combat fluency")],
                timeout=30,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/mos", "/api/hostess7-mos"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-mos.py", ["json"], timeout=60)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/mos/assist":
            qparams = parse_qs(urlparse(self.path).query)
            q = (qparams.get("q") or qparams.get("query") or [""])[0]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-mos.py",
                ["assist", str(q or "assist 11B infantryman")],
                timeout=45,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/mos/catalog":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-mos.py", ["catalog"], timeout=30)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/mos/explain":
            qparams = parse_qs(urlparse(self.path).query)
            q = (qparams.get("q") or qparams.get("query") or [""])[0]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-mos.py",
                ["teach", str(q or "mos fluency")],
                timeout=30,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7/g16/explain":
            qparams = parse_qs(urlparse(self.path).query)
            q = (qparams.get("q") or qparams.get("query") or [""])[0]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-g16.py",
                ["teach", str(q or "g16 compiler fluency")],
                timeout=30,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/creatable-lives", "/api/creatable-lives/status"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "creatable-lives-assist.py", ["json"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/creatable-lives/assist":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "creatable-lives-assist.py", ["assist"], timeout=20)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/creatable-lives/registry":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "creatable-lives-assist.py", ["registry"], timeout=20)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/creatable-lives/sustain":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "creatable-lives-assist.py", ["sustain"], timeout=20)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/right-to-exist", "/api/right-to-exist/mandate"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "right-to-exist-mandate.py", ["json"], timeout=20)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/right-to-exist/evaluate":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "right-to-exist-mandate.py", ["evaluate"], timeout=20)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/kernel-meld":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-kernel-meld.py", ["json"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/kernel-meld/cycle":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-kernel-meld.py", ["meld"], timeout=60)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/firmware-threat":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-firmware-threat-removal.py", ["json"], timeout=30)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/firmware-threat/cycle":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-firmware-threat-removal.py", ["cycle"], timeout=90)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/sense-package":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-sense-package-meld.py", ["json"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/sense-package/meld":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-sense-package-meld.py", ["meld"], timeout=45)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path.startswith("/api/field-bus/route/"):
            parts = [p for p in path.split("/") if p]
            if len(parts) >= 5:
                lane, key = parts[3], parts[4]
                payload = _nexus_py_json(
                    INSTALL_ROOT / "lib" / "field-unified-bus.py",
                    ["route", lane, key],
                    timeout=5,
                )
                self._send(200, json.dumps(payload or {"ok": False}), "application/json")
                return

        if path == "/api/sovereign-time":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "sovereign-time.py", ["status"], timeout=8)
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/sovereign-gate":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-sovereign-gate.py", ["json"], timeout=8)
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/sovereign-sync":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-sovereign-sync.py", ["json"], timeout=10)
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-services":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-services-2026.py", ["json"], timeout=12)
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-ntp":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-ntp-2026.py", ["json"], timeout=8)
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-operator/fast":
            profiles = [p for p in path.split("/") if p and p not in ("api", "field-operator", "fast")]
            args = ["fast", "--amazing"] + (profiles if profiles else [])
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-operator.py", args, timeout=10)
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-operator/iron-plate":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-operator.py", ["iron-plate"], timeout=10)
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/tristate-installer":
            payload = _tristate_installer_json()
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-perimeter":
            script = INSTALL_ROOT / "lib" / "field-perimeter-shield.py"
            if script.is_file():
                payload = _nexus_py_json(script, ["json"], timeout=45)
            else:
                payload = {"schema": "field-perimeter/v1", "ok": False, "error": "field_perimeter_missing"}
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/znetwork":
            if ZNETWORK_STATUS.is_file():
                try:
                    self._send(200, ZNETWORK_STATUS.read_text(encoding="utf-8"), "application/json")
                except OSError:
                    self._send(503, '{"ok":false,"error":"znetwork store unreadable"}', "application/json")
            else:
                self._send(
                    200,
                    json.dumps({
                        "schema": "znetwork-status/v1",
                        "ok": False,
                        "ready": False,
                        "hint": "Run ./nexus.sh --restart to publish ZNetwork status",
                    }),
                    "application/json",
                )
            return

        if path == "/api/queen-eyeball":
            payload = _panel_slice(
                "field_eyeball",
                live=_nexus_py_json(_queen_eyeball_script(), ["json"], timeout=120),
                default={"schema": "queen-eyeball-arm/v1", "posture": "assistive"},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/trust-strike":
            payload = _panel_slice(
                "trust_strike",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "trust-strike-engine.py", ["summary"], timeout=45),
                default={"schema": "trust-strike/v1", "strikes": []},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-weapons":
            stack = _panel_slice(
                "field_stack",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "queen_field_nexus.py", ["json"], timeout=120),
                default={"schema": "nexus-field-stack/v1"},
            )
            payload = {
                "schema": "nexus-field-weapons/v1",
                "nexus_defenses": stack.get("nexus_defenses") or {},
                "final_eye_weapons": stack.get("final_eye_weapons") or {},
                "trust_strike": stack.get("trust_strike") or {},
                "eyeball": stack.get("eyeball") or {},
                "gates_held": stack.get("gates_held"),
                "queen_verdict": stack.get("queen_verdict"),
            }
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/queen-boot":
            qb = _queen_boot_script()
            if qb.is_file():
                payload = _nexus_py_json(qb, ["json"], timeout=45)
            else:
                payload = {"schema": "queen-field-boot/v1", "error": "boot_missing"}
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/grok-build":
            gb = _grok_build_script()
            if gb.is_file():
                payload = _nexus_py_json(gb, ["json"])
            else:
                payload = {"schema": "grok-build-bridge/v1", "secure_channel": False, "error": "bridge_missing"}
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/queen-build":
            qb = _queen_build_script()
            if qb.is_file():
                payload = _nexus_py_json(qb, ["json"])
            else:
                payload = {
                    "schema": "queen-build/v1",
                    "inside": False,
                    "motto": "Run Queen/scripts/install-inside.sh",
                    "stages": [],
                }
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-rf":
            payload = _panel_slice(
                "field_rf",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-rf-sentinel.py", ["json"]),
                default={"antenna": {"mode": "standby"}, "bursts": []},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/plugins":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "nexus-plugins.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/plugins/registry":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "nexus-plugins.py", ["registry"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/terror-spiderweb":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "terror-spiderweb.py",
                ["json"],
                timeout=8,
            )
            if not isinstance(payload, dict) or not payload.get("schema"):
                payload = _panel_slice(
                    "terror_spiderweb",
                    default={"schema": "terror-spiderweb/v2", "mode": "idle", "nodes": [], "edges": [], "stats": {"idle": True}},
                )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/terror-spiderweb/sections":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "terror-spiderweb.py",
                ["sections"],
                timeout=5,
            )
            self._send(200, json.dumps(payload or {"sections": [], "ascii": "", "idle": True}), "application/json")
            return

        if path == "/api/terror-spiderweb/gps-table":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "terror-spiderweb.py", ["gps-table"], timeout=5)
            self._send(200, json.dumps(payload or {"homes": [], "count": 0}), "application/json")
            return

        if path == "/api/terror-spiderweb/registry":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "terror-spiderweb.py", ["registry"], timeout=5)
            self._send(200, json.dumps(payload or {}), "application/json")
            return

        if path == "/api/hostility-priority":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostility-priority.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/census-field":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "census-field-populate.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/thermal-earth":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "thermal-earth-field.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/thermal-earth/bodies":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "thermal-earth-field.py", ["bodies"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/precision-field":
            payload = _panel_slice(
                "precision_field",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "precision-field.py", ["json"]),
                default={"entities": [], "edges": [], "stats": {}},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/gps-precision":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "gps-precision.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/human-registry":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "human-registry.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/audio-train":
            payload = _panel_slice(
                "audio_train",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "audio-train.py", ["json"]),
                default={"schema": "audio-train/v1", "stats": {}},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/pet-signal-guard":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "pet-signal-guard.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/home-protector":
            force_scan = str(query.get("scan", query.get("harvest", ["0"]))[0]).strip().lower() in (
                "1", "true", "yes", "on",
            )
            if force_scan:
                payload = _nexus_py_json(
                    INSTALL_ROOT / "lib" / "home-protector.py",
                    ["json"],
                ) or {"schema": "home-protector/v1", "stats": {}}
            else:
                payload = _panel_slice(
                    "home_protector",
                    live=_nexus_py_json(INSTALL_ROOT / "lib" / "home-protector.py", ["json"]),
                    default={"schema": "home-protector/v1", "stats": {}},
                )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/local-services":
            force_scan = str(query.get("scan", query.get("build", ["0"]))[0]).strip().lower() in (
                "1", "true", "yes", "on",
            )
            if force_scan:
                payload = _nexus_py_json(
                    INSTALL_ROOT / "lib" / "local-services-audit.py",
                    ["build"],
                ) or {"schema": "local-services/v1", "stats": {}}
            else:
                payload = _panel_slice(
                    "local_services",
                    live=_nexus_py_json(INSTALL_ROOT / "lib" / "local-services-audit.py", ["json"]),
                    default={"schema": "local-services/v1", "stats": {}},
                )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/signals-field":
            payload = _panel_slice(
                "signals_field",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "signals-field.py", ["json"]),
                default={"schema": "signals-field/v1", "stats": {}, "antennas": []},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path in ("/api/field/field", "/api/field/plate-field"):
            publish = str(query.get("publish", ["0"])[0]).strip().lower() in ("1", "true", "yes")
            payload = _field_field_payload(publish=publish)
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field/parallel":
            publish = str(query.get("publish", ["0"])[0]).strip().lower() in ("1", "true", "yes")
            payload = _field_parallel_payload(publish=publish)
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-plate-field":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-plate-field.py", ["json"], timeout=25)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/field-hardware":
            payload = _panel_slice(
                "field_hardware",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-hardware-probe.py", ["json"]),
                default={"schema": "field-hardware-probe/v1"},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-hazard-onset":
            payload = _panel_slice(
                "field_hazard_onset",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-hazard-onset.py", ["panel"]),
                default={"schema": "field-hazard-onset-panel/v1"},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/lethal-enforcement":
            payload = _panel_slice(
                "lethal_enforcement",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "lethal-enforcement.py", ["panel"]),
                default={"schema": "lethal-enforcement-panel/v1", "merciless": True},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/hostess7-lethal-insight":
            payload = _panel_slice(
                "hostess7_lethal_insight",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-lethal-insight.py", ["panel"]),
                default={"schema": "hostess7-lethal-insight-panel/v1"},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path.startswith("/api/kill-codes"):
            if path == "/api/kill-codes":
                payload = _kill_codes_json(["catalog"], timeout=30)
                self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
                return
            if path == "/api/kill-codes/recommend":
                alert_id = str(query.get("alert", [""])[0]).strip()
                alert_json = "{}"
                if alert_id:
                    doc = _jockey_json(["alerts"], timeout=30)
                    found = next(
                        (
                            a
                            for a in (doc.get("all_alerts") or doc.get("jockey_alerts") or [])
                            if a.get("id") == alert_id
                        ),
                        None,
                    )
                    if found:
                        alert_json = json.dumps(found, ensure_ascii=False)
                payload = _kill_codes_json(["recommend", alert_json], timeout=30)
                self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
                return

        if path.startswith("/api/jockey/"):
            if path == "/api/jockey/alerts":
                payload = _jockey_json(["alerts"], timeout=30)
                self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
                return
            if path == "/api/jockey/actions":
                alert_id = str(query.get("alert", [""])[0]).strip()
                args = ["actions"]
                if alert_id:
                    args.append(alert_id)
                payload = _jockey_json(args, timeout=30)
                self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
                return

        if path == "/api/hostess7-autonomous":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-autonomous.py",
                ["status"],
                timeout=30,
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/hostess7-growth":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-growth.py",
                ["status"],
                timeout=30,
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/hostess7-neural":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-neural.py",
                ["status"],
                timeout=45,
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/hostess7-master":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-master.py",
                ["panel"],
                timeout=45,
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/hostess7-truth":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-truth-rating.py",
                ["status"],
                timeout=30,
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/hostess7-questionnaire":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-truth-rating.py",
                ["questionnaire"],
                timeout=600,
            )
            self._send(200, json.dumps(payload), "application/json")
            return
        if path == "/api/hostess7-master-sim":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-master-sim.py",
                ["status"],
                timeout=30,
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/hostess7-command/sketch":
            sketch = STATE_DIR / "hostess7-sketches" / "latest.png"
            if sketch.is_file():
                try:
                    self._send(200, sketch.read_bytes(), "image/png")
                except OSError:
                    self._send(404, "sketch unreadable", "text/plain")
            else:
                self._send(404, "no sketch", "text/plain")
            return

        if path == "/api/hostess7-command":
            refresh = str(query.get("refresh", ["0"])[0]).strip().lower() in ("1", "true", "yes")
            cache_path = STATE_DIR / "hostess7-command-panel.json"
            if not refresh and cache_path.is_file():
                try:
                    cached = json.loads(cache_path.read_text(encoding="utf-8"))
                    if isinstance(cached, dict) and cached.get("schema") == "hostess7-command/v1":
                        cached["_panel_cache"] = True
                        self._send(200, json.dumps(cached), "application/json")
                        return
                except (OSError, json.JSONDecodeError):
                    pass
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-command.py",
                ["panel"],
                timeout=60,
            ) or _panel_slice(
                "hostess7_command",
                live=None,
                default={"schema": "hostess7-command/v1", "transcript": [], "proposed_updates": []},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-antenna":
            payload = _panel_slice(
                "field_antenna",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-antenna-orchestrator.py", ["json"]),
                default={"schema": "field-antenna/v1"},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-antenna/catch-audio":
            wav = STATE_DIR / "field-antenna-catch.wav"
            if wav.is_file():
                try:
                    data = wav.read_bytes()
                    self._send(200, data, "audio/wav")
                except OSError:
                    self._send(404, json.dumps({"error": "catch_audio_unreadable"}), "application/json")
            else:
                self._send(404, json.dumps({"error": "no_catch_audio"}), "application/json")
            return

        if path == "/api/field-radio":
            payload = _panel_slice(
                "field_radio",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-radio-catcher.py", ["json"]),
                default={"schema": "field-radio-catcher/v1", "station_menu": []},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-dns":
            payload = _read_field_panel_file("field_dns")
            if payload is None:
                live = _nexus_py_json(INSTALL_ROOT / "lib" / "field-dns.py", ["json"])
                payload = _panel_slice(
                    "field_dns",
                    live=live,
                    default={"schema": "field-dns/v2"},
                )
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/field-outside-talk":
            payload = _panel_slice(
                "field_outside_talk",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-outside-talk.py", ["json"]),
                default={"schema": "field-outside-talk/v1"},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-drive":
            payload = _panel_slice(
                "field_drive",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-drive-system.py", ["json"]),
                default={"schema": "field-drive-system/v1", "drives": []},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-brain":
            payload = _panel_slice(
                "field_brain",
                live=_nexus_py_json(INSTALL_ROOT / "lib" / "field-brain-panel.py", ["json"]),
                default={"schema": "field-brain/v1", "ok": True, "github_library_books": 0, "manifest_count": 0},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-drive/drives":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "field-drive-system.py",
                ["talk", json.dumps({"op": "drives"})],
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/hostess-profile":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess-profile.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/panel-language":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "panel-i18n.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/host-security-tier":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "host-security-tier.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/fcc-signal-lookup":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "fcc-signal-lookup.py", ["identify"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/heavyboi/status":
            pending = STATE_DIR / "nexus-kill-intel-pending.json"
            log_path = STATE_DIR / "heavyboi-ingest-log.jsonl"
            lines = 0
            try:
                if log_path.is_file():
                    lines = sum(1 for _ in log_path.open(encoding="utf-8"))
            except OSError:
                lines = 0
            payload = {
                "ok": True,
                "version": "7.8.0",
                "hostess_version": "7",
                "pending": pending.is_file(),
                "ingest_log_lines": lines,
            }
            self._send(200, json.dumps(payload), "application/json")
            return

        if path.startswith("/api/human-registry/resolve"):
            ip = str(query.get("ip", [""])[0]).strip()
            if not ip:
                self._send(400, json.dumps({"error": "missing ip"}), "application/json")
                return
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "human-registry.py", ["resolve", ip])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/existence-identity":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "existence-identity.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/existence-identity/table":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "existence-identity.py", ["table"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/police-agencies":
            region = str(query.get("region", [""])[0]).strip() or None
            script = INSTALL_ROOT / "lib" / "police-agency-db.py"
            if region:
                payload = _nexus_py_json(script, ["list", region])
            else:
                payload = _nexus_py_json(script, ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/gov-intel":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "gov-intel-db.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/program-tags":
            program_id = str(query.get("id", [""])[0]).strip()
            script = INSTALL_ROOT / "lib" / "program-tags-db.py"
            if program_id:
                payload = _nexus_py_json(script, ["get", program_id])
            else:
                payload = _nexus_py_json(script, ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/gov-intel/image":
            rel = str(query.get("path", [""])[0]).strip()
            if not rel:
                self._send(400, "missing path", "text/plain")
                return
            gi_py = INSTALL_ROOT / "lib" / "gov-intel-db.py"
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("gov_intel_db", gi_py)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                got = mod.get_image(rel)
                if not got:
                    self._send(404, "not found", "text/plain")
                    return
                data, ctype = got
                self._send(200, data, ctype)
            except Exception:
                self._send(404, "not found", "text/plain")
            return

        if path == "/api/field":
            full = str(query.get("full", ["1"])[0]).strip().lower() in ("1", "true", "yes")
            self._send(200, _read_status_json(full=full), "application/json")
            return

        if path.startswith("/api/library/"):
            script = INSTALL_ROOT / "lib" / "h7-library-bridge.py"
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            env.setdefault("HOSTESS7_ROOT", str(_resolve_hostess7_root()))
            env.setdefault("HOSTESS7_TEAM_FIELD", "/media/default/HOSTESS7_TEAM/fieldstorage")

            def _lib_json(args: list[str], *, timeout: int = 45) -> dict:
                if not script.is_file():
                    return {"ok": False, "error": "library_bridge_missing"}
                proc = subprocess.run(
                    [sys.executable, str(script), *args],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=env,
                )
                try:
                    return json.loads(proc.stdout or "{}")
                except json.JSONDecodeError:
                    return {"ok": False, "error": "library_read_failed", "detail": (proc.stderr or "")[:400]}

            if path == "/api/library/page":
                book_id = str(query.get("book", [""])[0]).strip()
                page = int(query.get("page", ["1"])[0] or "1")
                chars = str(query.get("chars", [""])[0]).strip()
                if not book_id:
                    self._send(400, json.dumps({"ok": False, "error": "missing book"}), "application/json")
                    return
                args = ["page", book_id, str(page)]
                if chars.isdigit():
                    args.append(chars)
                payload = _lib_json(args)
                self._send(200 if payload.get("ok") else 404, json.dumps(payload), "application/json")
                return

            if path == "/api/library/full":
                book_id = str(query.get("book", [""])[0]).strip()
                if not book_id:
                    self._send(400, json.dumps({"ok": False, "error": "missing book"}), "application/json")
                    return
                payload = _lib_json(["full", book_id], timeout=120)
                self._send(200 if payload.get("ok") else 404, json.dumps(payload), "application/json")
                return

            if path == "/api/library/catalog":
                refresh = str(query.get("refresh", ["0"])[0]).strip().lower() in ("1", "true", "yes")
                profile = str(query.get("profile", [""])[0]).strip()
                if not refresh and not profile:
                    fast = _load_h7_library_catalog_fast()
                    if fast:
                        self._send(200, json.dumps(fast), "application/json")
                        return
                args = ["build"]
                if profile:
                    args.extend(["--profile", profile])
                if refresh:
                    args.append("--force")
                payload = _lib_json(args, timeout=90)
                self._send(200, json.dumps(payload), "application/json")
                return

            if path == "/api/library/profiles":
                payload = _lib_json(["profiles"])
                self._send(200, json.dumps(payload), "application/json")
                return

            if path == "/api/library/war":
                payload = _lib_json(["war"], timeout=90)
                self._send(200, json.dumps(payload), "application/json")
                return

            if path == "/api/library/search":
                q = str(query.get("q", query.get("query", [""]))[0]).strip()
                if not q:
                    self._send(400, json.dumps({"ok": False, "error": "missing query"}), "application/json")
                    return
                payload = _lib_json(["search", q])
                self._send(200, json.dumps(payload), "application/json")
                return

            if path == "/api/library/dewey":
                profile = str(query.get("profile", [""])[0]).strip()
                args = ["dewey"]
                if profile:
                    args.extend(["--profile", profile])
                payload = _lib_json(args, timeout=90)
                self._send(200, json.dumps(payload), "application/json")
                return

            if path == "/api/library/fonts":
                payload = _lib_json(["fonts"])
                self._send(200, json.dumps(payload), "application/json")
                return

            if path == "/api/library/fingerprint":
                payload = _lib_json(["fingerprint"])
                self._send(200, json.dumps(payload), "application/json")
                return

            if path == "/api/library/cover":
                book_id = str(query.get("book", [""])[0]).strip()
                side = str(query.get("side", ["front"])[0]).strip() or "front"
                fmt = str(query.get("format", ["png"])[0]).strip() or "png"
                if not book_id:
                    self._send(400, "missing book", "text/plain")
                    return
                try:
                    import importlib.util
                    lib_py = INSTALL_ROOT / "lib" / "h7-library-librarian.py"
                    spec = importlib.util.spec_from_file_location("h7_library_librarian", lib_py)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    got = mod.get_cover_bytes(book_id, side, fmt=fmt)
                    if not got and fmt == "png":
                        cov_py = INSTALL_ROOT / "lib" / "sdf-book-covers.py"
                        bib = mod.load_bibliography_index().get(book_id) or mod.enrich_record(book_id)
                        subprocess.run(
                            [sys.executable, str(cov_py), book_id, side],
                            capture_output=True,
                            timeout=30,
                            env=env,
                        )
                        got = mod.get_cover_bytes(book_id, side, fmt=fmt)
                    if not got:
                        self._send(404, "cover not on field drive", "text/plain")
                        return
                    data, ctype = got
                    self._send(200, data, ctype)
                except Exception:
                    self._send(404, "cover not found", "text/plain")
                return

        if path == "/api/data":
            items = []
            for key, fp in DATA_FILES.items():
                items.append({
                    "id": key,
                    "path": str(fp),
                    "exists": fp.is_file(),
                    "size": fp.stat().st_size if fp.is_file() else 0,
                    "url": f"/api/data/{key}",
                })
            self._send(200, json.dumps({"files": items}), "application/json")
            return

        if path.startswith("/api/data/"):
            key = path.split("/api/data/", 1)[1]
            panel_key = key.replace("-", "_")
            if panel_key in PANEL_PARALLEL_KEYS:
                cached = _panel_slice(panel_key, default={})
                if cached.get("_field_cache"):
                    self._send(200, json.dumps(cached), "application/json")
                    return
            fp = DATA_FILES.get(key)
            if not fp or not fp.is_file():
                self._send(404, "not found", "text/plain")
                return
            ctype = "application/json" if fp.suffix == ".json" else "text/plain"
            self._send(200, fp.read_text(encoding="utf-8", errors="replace"), ctype)
            return

        if path == "/api/logs":
            catalog = {k: {"path": str(v), "exists": v.is_file()} for k, v in LOG_FILES.items()}
            self._send(200, json.dumps(catalog), "application/json")
            return

        if path.startswith("/api/logs/"):
            key = path.split("/api/logs/", 1)[1]
            fp = LOG_FILES.get(key)
            if not fp:
                self._send(404, "not found", "text/plain")
                return
            lines = int(query.get("lines", ["120"])[0])
            self._send(200, _tail_file(fp, lines), "text/plain")
            return

        if path == "/api/intel/scour":
            script = INSTALL_ROOT / "lib" / "vector-intel.py"
            if not script.is_file():
                self._send(404, json.dumps({"ok": False, "error": "vector-intel missing"}), "application/json")
                return
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            proc = subprocess.run(
                ["pythong", str(script), "scour"],
                capture_output=True,
                text=True,
                timeout=90,
                env=env,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                self._send(200, proc.stdout, "application/json")
            else:
                self._send(500, json.dumps({"ok": False, "error": "scour failed"}), "application/json")
            return

        if path == "/api/intel/lookup":
            ip = str(query.get("ip", [""])[0]).strip()
            if not ip:
                self._send(400, json.dumps({"ok": False, "error": "missing ip"}), "application/json")
                return
            script = INSTALL_ROOT / "lib" / "vector-intel.py"
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            proc = subprocess.run(
                ["pythong", str(script), "lookup", ip],
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
            )
            if proc.returncode == 0:
                self._send(200, proc.stdout, "application/json")
            else:
                self._send(500, json.dumps({"ok": False, "error": "lookup failed"}), "application/json")
            return

        if path in ("/field-talk", "/field-talk/"):
            target = PANEL_DIR / "field-talk.html"
        elif path in (
            "/underlay-f9", "/underlay-f9/",
            "/tristate-installer", "/tristate-installer/",
            "/install-underlay", "/install-underlay/",
            "/field-modern", "/field-modern/",
        ):
            target = PANEL_DIR / "underlay-f9.html"
        elif path in (
            "/field", "/field/", "/app", "/app/", "/", "/index.html",
            "/field-legacy", "/field-legacy/",
        ):
            target = PANEL_DIR / "threat-panel.html"
            if target.is_file():
                _serve_panel_html(self, target)
                return
        else:
            target = (PANEL_DIR / path.lstrip("/")).resolve()
            if PANEL_DIR.resolve() not in target.parents and target != PANEL_DIR.resolve():
                self._send(403, "forbidden", "text/plain")
                return
        if target.is_file():
            if target.suffix == ".html" and target.name == "threat-panel.html":
                _serve_panel_html(self, target)
            else:
                self._send(200, target.read_bytes(), _panel_static_mime(target))
            return
        self._send(404, "not found", "text/plain")

    def do_POST(self):
        path = unquote(self.path.split("?", 1)[0])
        max_body = 8_388_608 if path.startswith("/api/library/") else 65536
        if self.headers.get("Content-Length"):
            try:
                length = int(self.headers.get("Content-Length", 0))
            except ValueError:
                length = 0
            if length > max_body:
                self._send(413, "payload too large", "text/plain")
                return
        body = self._read_json_body()

        if path == "/api/ai-integration":
            peer = self.client_address[0] if self.client_address else "127.0.0.1"
            hdrs = {k: v for k, v in self.headers.items()}
            payload = _ai_integration_json(body, peer=str(peer), headers=hdrs)
            code = 200 if payload.get("ok") or str(payload.get("action", "")) in ("status", "json", "posture") else 403
            if payload.get("error") == "human_integration_forbidden":
                code = 403
            self._send(code, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path.startswith("/api/tristate-installer"):
            sub = path[len("/api/tristate-installer") :].strip("/") or "status"
            if sub in ("", "status"):
                payload = _tristate_installer_json()
            elif sub == "scan-wrdt":
                payload = _tristate_installer_json(verb="scan-wrdt")
            elif sub == "refield":
                payload = _nexus_py_json(
                    INSTALL_ROOT / "lib" / "field-drive-converter.py",
                    ["refield"],
                    timeout=120,
                )
                if isinstance(payload, dict) and "posture" not in payload:
                    payload["posture"] = _tristate_installer_json()
            elif sub == "drive-restore-scan":
                payload = _nexus_py_json(
                    INSTALL_ROOT / "lib" / "field-drive-converter.py",
                    ["scan-restore"],
                    timeout=180,
                )
                if isinstance(payload, dict):
                    payload["posture"] = _tristate_installer_json()
            elif sub == "drive-restore":
                dc_py = INSTALL_ROOT / "lib" / "field-drive-converter.py"
                if body.get("dry_run"):
                    payload = _nexus_py_json(dc_py, ["restore-out"], timeout=600)
                else:
                    payload = _nexus_py_json(
                        dc_py,
                        ["restore-out", "--apply", "--confirm"],
                        timeout=900,
                    )
                if isinstance(payload, dict) and "posture" not in payload:
                    payload["posture"] = _tristate_installer_json()
            elif sub == "drive-audit":
                payload = _nexus_py_json(
                    INSTALL_ROOT / "lib" / "field-drive-converter.py",
                    ["audit"],
                    timeout=120,
                )
                if isinstance(payload, dict):
                    payload["posture"] = _tristate_installer_json()
            elif sub == "drive-convert":
                dc_py = INSTALL_ROOT / "lib" / "field-drive-converter.py"
                if body.get("dry_run"):
                    payload = _nexus_py_json(dc_py, ["dry-run"], timeout=600)
                else:
                    payload = _tristate_elevated_json("wrdt-apply", body)
                if isinstance(payload, dict) and "posture" not in payload:
                    payload["posture"] = _tristate_installer_json()
            elif sub == "commit":
                payload = _tristate_elevated_json("commit", body)
            elif sub == "wrdt-apply":
                payload = _tristate_elevated_json("wrdt-apply", body)
            elif sub == "reboot":
                payload = _tristate_elevated_json("reboot", body)
            elif sub == "grok-prep":
                payload = _tristate_elevated_json("grok-prep", body)
            elif sub == "znetwork-offer":
                payload = _tristate_installer_json(verb="znetwork-offer", body=body)
                if isinstance(payload, dict) and "posture" not in payload:
                    payload["posture"] = _tristate_installer_json()
            elif sub == "znetwork-choice":
                payload = _tristate_installer_json(verb="znetwork-choice", body=body)
                if isinstance(payload, dict) and "posture" not in payload:
                    payload["posture"] = _tristate_installer_json()
            elif sub == "install-nexus":
                installer = INSTALL_ROOT / "install-all.sh"
                if not installer.is_file():
                    installer = INSTALL_ROOT / "install-all.sh"
                dev = INSTALL_ROOT.parent / "install-all.sh"
                if not installer.is_file() and dev.is_file():
                    installer = dev
                bridge = INSTALL_ROOT / "lib" / "nexus-pkexec-bridge.sh"
                if installer.is_file() and bridge.is_file():
                    subprocess.Popen(
                        [
                            "pkexec",
                            "--action",
                            "com.nexus.field.install",
                            str(bridge),
                            "run-install",
                            str(installer),
                        ],
                        env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL_ROOT)},
                    )
                    payload = {"ok": True, "started": True, "installer": str(installer)}
                else:
                    payload = {
                        "ok": False,
                        "error": "installer_missing",
                        "hint": "Run ./install-all.sh from NewLatest",
                    }
            else:
                self._send(404, json.dumps({"ok": False, "error": "unknown tristate action"}), "application/json")
                return
            code = 200 if payload.get("ok", True) else 400
            self._send(code, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path.startswith("/api/field-operator"):
            sub = path[len("/api/field-operator") :].strip("/") or "board"
            op_py = INSTALL_ROOT / "lib" / "field-operator.py"
            if sub in ("", "board", "iron-plate"):
                args = ["iron-plate"] if sub == "iron-plate" else ["board"]
                if body.get("override"):
                    args.extend(["--override", str(body.get("override"))])
                payload = _nexus_py_json(op_py, args, timeout=60)
            elif sub == "communicate":
                target = str(body.get("id") or body.get("path") or "").strip()
                args = ["communicate", target] if target else ["json"]
                if body.get("override"):
                    args.extend(["--override", str(body.get("override"))])
                payload = _nexus_py_json(op_py, args, timeout=30)
            elif sub == "fast":
                names = body.get("profiles") or []
                args = ["fast"] + [str(n) for n in names if n]
                payload = _nexus_py_json(op_py, args or ["fast"], timeout=30)
            elif sub == "route":
                target = str(body.get("id") or body.get("target") or "").strip()
                if not target:
                    self._send(400, json.dumps({"ok": False, "error": "missing id"}), "application/json")
                    return
                override = str(body.get("override") or "").strip() or None
                payload = _field_operator_copilot_route(target, override=override)
            elif sub == "route-batch":
                batch = body.get("batch") or body.get("targets") or []
                if not batch:
                    self._send(400, json.dumps({"ok": False, "error": "missing batch"}), "application/json")
                    return
                override = str(body.get("override") or "").strip() or None
                payload = _field_operator_copilot_batch([str(x) for x in batch if x], override=override)
            elif sub == "copilot":
                payload = _field_operator_copilot_status()
            else:
                self._send(404, json.dumps({"ok": False, "error": "unknown operator action"}), "application/json")
                return
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/kill-codes/execute":
            code = str(body.get("code") or "").strip()
            if not code:
                self._send(400, json.dumps({"ok": False, "error": "missing code"}), "application/json")
                return
            payload = _kill_codes_json(["execute", json.dumps(body, ensure_ascii=False)], timeout=90)
            code_http = 200 if payload.get("ok") else (403 if payload.get("friendly_refused") else 400)
            self._send(code_http, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/jockey/ack":
            alert_id = str(body.get("alert_id") or "").strip()[:256]
            response = str(body.get("response") or "seen").strip().lower()
            if not alert_id:
                self._send(400, json.dumps({"ok": False, "error": "missing alert_id"}), "application/json")
                return
            if response not in ("seen", "needs_action", "needs_more_action"):
                self._send(400, json.dumps({"ok": False, "error": "invalid response"}), "application/json")
                return
            payload = _jockey_json(["ack", alert_id, response], timeout=15)
            code = 200 if payload.get("ok") else 400
            self._send(code, json.dumps(payload, ensure_ascii=False), "application/json")
            return

        if path == "/api/packet-field/capture":
            script = INSTALL_ROOT / "lib" / "packet-field.py"
            if not script.is_file():
                self._send(404, json.dumps({"ok": False, "error": "packet_field_missing"}), "application/json")
                return
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            proc = subprocess.run(
                [sys.executable, str(script), "capture"],
                capture_output=True,
                text=True,
                timeout=12,
                env=env,
            )
            try:
                doc = json.loads(proc.stdout or "{}")
            except json.JSONDecodeError:
                doc = {"ok": False, "error": (proc.stderr or "capture_failed")[:300]}
            if isinstance(doc, dict):
                doc["ok"] = proc.returncode == 0
            self._send(200 if proc.returncode == 0 else 500, json.dumps(doc), "application/json")
            return

        if path.startswith("/api/library/"):
            script = INSTALL_ROOT / "lib" / "h7-library-bridge.py"
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            env.setdefault("HOSTESS7_ROOT", str(_resolve_hostess7_root()))
            env.setdefault("HOSTESS7_TEAM_FIELD", "/media/default/HOSTESS7_TEAM/fieldstorage")

            if path == "/api/library/upload":
                if not script.is_file():
                    self._send(500, json.dumps({"ok": False, "error": "library_bridge_missing"}), "application/json")
                    return
                proc = subprocess.run(
                    [sys.executable, str(script), "upload", json.dumps(body)],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env=env,
                )
                try:
                    payload = json.loads(proc.stdout or "{}")
                except json.JSONDecodeError:
                    payload = {"ok": False, "error": "upload_failed"}
                self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
                return

        if path == "/api/update/apply":
            lock = _nexus_update_lock(["status"])
            if lock.get("locked"):
                self._send(
                    409,
                    json.dumps({
                        "ok": False,
                        "error": "update_in_progress",
                        "update_in_progress": True,
                        "message": lock.get("message") or "Update already running",
                        "update_lock": lock,
                    }),
                    "application/json",
                )
                return
            try:
                STATE_DIR.joinpath("update-needs-sudo.json").unlink(missing_ok=True)
            except OSError:
                pass
            upd = _nexus_update_check(force=True)
            if upd.get("update_in_progress"):
                self._send(
                    409,
                    json.dumps({
                        "ok": False,
                        "error": "update_in_progress",
                        "update_in_progress": True,
                        "message": upd.get("label") or "Update in progress",
                        "update_lock": upd.get("update_lock"),
                    }),
                    "application/json",
                )
                return
            if not upd.get("update_available"):
                self._send(200, json.dumps({"ok": True, "already_current": True, **upd}), "application/json")
                return
            target = str(upd.get("latest") or "")
            previous = str(upd.get("previous") or upd.get("current") or "")
            lock_phase = "download_tarball" if str(upd.get("update_mode") or "release") == "release" else "git_fetch"
            acq = _nexus_update_lock([
                "acquire",
                "--holder=panel",
                f"--phase={lock_phase}",
                f"--target={target}",
                f"--previous={previous}",
            ])
            if not acq.get("ok"):
                self._send(
                    409,
                    json.dumps({
                        "ok": False,
                        "error": acq.get("error") or "update_in_progress",
                        "update_in_progress": True,
                        "message": acq.get("message") or "Could not acquire update lock",
                    }),
                    "application/json",
                )
                return
            token = str(acq.get("token") or "")
            update_mode = str(upd.get("update_mode") or os.environ.get("NEXUS_UPDATE_MODE", "release"))
            tarball_url = str(upd.get("source_tarball") or "")
            git_dir = _resolve_nexus_source_root()
            install_sh = None
            if git_dir:
                for name in ("install-all.sh", "stealth_install.sh"):
                    candidate = git_dir / name
                    if candidate.is_file():
                        install_sh = candidate
                        break
            if update_mode == "release" and not tarball_url:
                _nexus_update_lock(["release", f"--token={token}"])
                self._send(
                    500,
                    json.dumps({
                        "ok": False,
                        "applied": False,
                        "error": "release_tarball_missing",
                        "message": "No release tarball URL — check GitHub release assets",
                        "release_url": upd.get("release_url"),
                    }),
                    "application/json",
                )
                return
            if update_mode != "release" and (not git_dir or not install_sh):
                _nexus_update_lock(["release", f"--token={token}"])
                self._send(
                    500,
                    json.dumps({
                        "ok": False,
                        "applied": False,
                        "error": "install_tree_missing",
                        "message": "install-all.sh not found — set NEXUS_SHIELD_SOURCE or use release mode",
                        "install_root": str(INSTALL_ROOT),
                    }),
                    "application/json",
                )
                return
            started = _spawn_nexus_update_apply(
                git_dir=git_dir,
                install_sh=install_sh,
                token=token,
                target=target,
                previous=previous,
                tarball_url=tarball_url,
                update_mode=update_mode,
            )
            if not started:
                _nexus_update_lock(["release", f"--token={token}"])
                self._send(
                    500,
                    json.dumps({
                        "ok": False,
                        "error": "update_spawn_failed",
                        "message": "Could not start background update — see update-apply.log",
                    }),
                    "application/json",
                )
                return
            lock_now = _nexus_update_lock(["status"])
            self._send(
                202,
                json.dumps({
                    "ok": True,
                    "started": True,
                    "update_in_progress": True,
                    "reload_panel": True,
                    "message": (
                        f"Release installer started — {previous} → {target}"
                        if update_mode == "release"
                        else f"Update started — {previous} → {target}"
                    ),
                    "previous": previous,
                    "latest": target,
                    "update_mode": update_mode,
                    "apply_via": upd.get("apply_via") or ("release_tarball" if update_mode == "release" else "git_tree"),
                    "source_tarball": tarball_url or None,
                    "tristate_installer_url": upd.get("tristate_installer_url"),
                    "source_root": str(git_dir) if git_dir else None,
                    "update_lock": lock_now,
                    "log": str(STATE_DIR / "update-apply.log"),
                }),
                "application/json",
            )
            return

        if path == "/api/update/sudo-prompt":
            lock = _nexus_update_lock(["status"])
            needs = _nexus_update_needs_sudo()
            if not needs and not lock.get("locked"):
                self._send(
                    400,
                    json.dumps({"ok": False, "error": "no_pending_sudo"}),
                    "application/json",
                )
                return
            git_dir = _resolve_nexus_source_root()
            install_sh = None
            if git_dir:
                for name in ("install-all.sh", "stealth_install.sh"):
                    candidate = git_dir / name
                    if candidate.is_file():
                        install_sh = candidate
                        break
            token = str(lock.get("token") or os.environ.get("NEXUS_UPDATE_LOCK_TOKEN", ""))
            previous = str(lock.get("previous_version") or (needs.get("previous") if needs else ""))
            target = str(lock.get("target_version") or (needs.get("target") if needs else ""))
            update_mode = str(
                os.environ.get("NEXUS_UPDATE_MODE", "release")
                if not needs else needs.get("update_mode") or os.environ.get("NEXUS_UPDATE_MODE", "release")
            )
            env = os.environ.copy()
            env.update({
                "NEXUS_INSTALL_ROOT": str(INSTALL_ROOT),
                "NEXUS_STATE_DIR": str(STATE_DIR),
                "NEXUS_UPDATE_LOCK_TOKEN": token,
                "NEXUS_UPDATE_TARGET": target,
                "NEXUS_UPDATE_PREVIOUS": previous,
                "NEXUS_UPDATE_MODE": update_mode,
            })
            if git_dir:
                env["NEXUS_UPDATE_GIT_DIR"] = str(git_dir)
            if install_sh and install_sh.is_file():
                env["NEXUS_UPDATE_INSTALL_SH"] = str(install_sh)
            cache_upd = _nexus_update_check()
            if cache_upd.get("source_tarball"):
                env["NEXUS_UPDATE_TARBALL_URL"] = str(cache_upd["source_tarball"])
            helper = INSTALL_ROOT / "lib" / "nexus-update-apply.sh"
            try:
                subprocess.Popen(
                    ["bash", str(helper)],
                    env=env,
                    start_new_session=True,
                    cwd=str(git_dir),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self._send(
                    202,
                    json.dumps({
                        "ok": True,
                        "prompt_started": True,
                        "message": "Password prompt opened — complete sudo to finish update",
                    }),
                    "application/json",
                )
            except OSError as exc:
                self._send(
                    500,
                    json.dumps({"ok": False, "error": str(exc)}),
                    "application/json",
                )
            return

        if path == "/api/home-protector/block":
            entity_id = str(body.get("entity_id", body.get("id", ""))).strip()
            if not entity_id:
                self._send(400, json.dumps({"ok": False, "error": "missing entity_id"}), "application/json")
                return
            force = body.get("force") in (True, 1, "1", "true", "yes", "on")
            args = ["block", entity_id]
            if force:
                args.append("--force")
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "home-protector.py", args)
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/home-protector/permit":
            entity_id = str(body.get("entity_id", body.get("id", ""))).strip()
            if not entity_id:
                self._send(400, json.dumps({"ok": False, "error": "missing entity_id"}), "application/json")
                return
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "home-protector.py", ["permit", entity_id])
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/home-protector/block-all":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "home-protector.py", ["block-all"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/local-services/close":
            listener_id = str(body.get("listener_id", body.get("id", ""))).strip()
            if not listener_id:
                self._send(400, json.dumps({"ok": False, "error": "missing listener_id"}), "application/json")
                return
            force = body.get("force") in (True, 1, "1", "true", "yes", "on")
            args = ["close", listener_id]
            if force:
                args.append("--force")
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "local-services-audit.py", args)
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/local-services/permit":
            listener_id = str(body.get("listener_id", body.get("id", ""))).strip()
            if not listener_id:
                self._send(400, json.dumps({"ok": False, "error": "missing listener_id"}), "application/json")
                return
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "local-services-audit.py", ["permit", listener_id])
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/local-services/close-all":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "local-services-audit.py", ["close-all"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/heavyboi/ingest":
            intel = body if isinstance(body, dict) else {}
            if not intel.get("kill_orders") and not intel.get("orders"):
                self._send(400, json.dumps({"ok": False, "error": "missing kill_orders"}), "application/json")
                return
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "heavyboi-importer.py",
                ["ingest", "--json", json.dumps(intel)],
            )
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/heavyboi/pending":
            intel = body if isinstance(body, dict) else {}
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "heavyboi-importer.py",
                ["pending", json.dumps(intel)],
            )
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/signals-field":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "signals-field.py", ["build"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path in ("/api/field/field", "/api/field/plate-field", "/api/field/parallel"):
            publish = str(body.get("publish", "0")).strip().lower() in ("1", "true", "yes")
            payload = _field_field_payload(publish=publish)
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field":
            _nexus_shell_publish_panel()
            if STATUS_JSON.is_file():
                self._send(200, STATUS_JSON.read_text(encoding="utf-8"), "application/json")
            else:
                self._send(200, '{"field":true,"panel_ready":false}', "application/json")
            return

        if path == "/api/field-radio":
            action = str(body.get("action") or "build").strip().lower()
            if action == "tune":
                tune_body = {
                    "station_id": body.get("station_id") or body.get("id") or "",
                    "call_sign": body.get("call_sign") or "",
                    "freq_mhz": body.get("freq_mhz"),
                }
                payload = _nexus_py_json(
                    INSTALL_ROOT / "lib" / "field-radio-catcher.py",
                    ["tune", json.dumps(tune_body)],
                )
                self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
                return
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-radio-catcher.py", ["build"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-antenna":
            action = str(body.get("action") or "build").strip().lower()
            if action in ("sound_off", "soundoff", "prototype"):
                catch_body = {
                    "freq_mhz": body.get("freq_mhz", os.environ.get("NEXUS_FIELD_CATCH_MHZ", "93.1")),
                    "station_id": body.get("station_id") or "wimk-931",
                    "call_sign": body.get("call_sign") or "WIMK",
                    "play": body.get("play", True),
                }
                payload = _nexus_py_json(
                    INSTALL_ROOT / "lib" / "field-antenna-orchestrator.py",
                    ["sound_off", json.dumps(catch_body)],
                )
                self._send(200 if payload.get("heard") or payload.get("ok") else 400, json.dumps(payload), "application/json")
                return
            if action in ("catch", "listen", "receive", "pinpoint"):
                catch_body = {
                    "freq_mhz": body.get("freq_mhz"),
                    "freq_khz": body.get("freq_khz"),
                    "station_id": body.get("station_id") or "",
                    "call_sign": body.get("call_sign") or "",
                    "live_play": body.get("live_play", True),
                }
                if catch_body["freq_mhz"] is None and catch_body["freq_khz"] is None:
                    catch_body["freq_mhz"] = body.get("freq_mhz", os.environ.get("NEXUS_FIELD_CATCH_MHZ", "93.1"))
                orch_cmd = "listen" if action in ("listen", "receive", "pinpoint") else "catch"
                payload = _nexus_py_json(
                    INSTALL_ROOT / "lib" / "field-antenna-orchestrator.py",
                    [orch_cmd, json.dumps(catch_body)],
                )
                self._send(200 if payload.get("ok") or payload.get("tri_ready") else 400, json.dumps(payload), "application/json")
                return
            if action in ("cycle", "test", "launch"):
                extra = []
                if action == "launch":
                    extra = [str(body.get("max_rounds") or os.environ.get("NEXUS_FIELD_ANTENNA_ROUNDS", "12"))]
                payload = _nexus_py_json(
                    INSTALL_ROOT / "lib" / "field-antenna-orchestrator.py",
                    [action, *extra],
                )
            else:
                payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-antenna-orchestrator.py", ["build"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-dns":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-dns.py", ["build"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-outside-talk":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-outside-talk.py", ["build"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-outside-talk/connect":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "field-outside-talk.py",
                ["connect", json.dumps(body if isinstance(body, dict) else {})],
            )
            self._send(200 if payload.get("ok") or payload.get("session_id") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/field-outside-talk/probe":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "field-outside-talk.py",
                ["probe", json.dumps(body if isinstance(body, dict) else {})],
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-outside-talk/disconnect":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "field-outside-talk.py",
                ["disconnect", json.dumps(body if isinstance(body, dict) else {})],
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-drive":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-drive-system.py", ["build"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-drive/talk":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "field-drive-system.py",
                ["talk", json.dumps(body if isinstance(body, dict) else {})],
            )
            self._send(200 if payload.get("ok") is not False else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/panel-language":
            code = str((body or {}).get("code") or "").strip()
            if not code:
                self._send(400, json.dumps({"ok": False, "error": "missing code"}), "application/json")
                return
            remember = (body or {}).get("remember", True)
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "panel-i18n.py",
                ["set", code, json.dumps({"code": code, "remember": remember})],
            )
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/hostess-profile":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess-profile.py",
                ["save", json.dumps(body if isinstance(body, dict) else {})],
            )
            if payload.get("extreme_active") or int(payload.get("host_star_tier") or 0) >= 4:
                inner = _nexus_shell_prelude() + "nexus_host_extreme_apply_if_eligible"
                _run_nexus_bash(inner, timeout=60)
                tier = _nexus_py_json(INSTALL_ROOT / "lib" / "host-security-tier.py", ["publish"])
                payload["extreme_applied"] = bool(tier.get("extreme_active"))
                payload["host_security"] = tier
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/humanoid-motion/load":
            skill_id = str(body.get("skill_id") or body.get("skill") or "").strip()
            if not skill_id:
                self._send(400, json.dumps({"ok": False, "error": "missing skill_id"}), "application/json")
                return
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "humanoid-motion-training.py",
                ["load", skill_id],
                timeout=30,
            )
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/humanoid-motion/train":
            skill_id = str(body.get("skill_id") or body.get("skill") or "").strip()
            ticks = int(body.get("ticks") or body.get("duration_ticks") or 0)
            args = ["train"]
            if skill_id:
                args.append(skill_id)
            if ticks > 0:
                args.append(str(ticks))
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "humanoid-motion-training.py",
                args,
                timeout=90,
            )
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path in ("/api/humanoid-motion/train-blast", "/api/humanoid-motion/blast"):
            skill_id = str(body.get("skill_id") or body.get("skill") or "").strip()
            ticks = int(body.get("ticks") or body.get("blast_ticks") or 0)
            args = ["blast"]
            if skill_id:
                args.append(skill_id)
            if ticks > 0:
                args.append(str(ticks))
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "humanoid-motion-training.py",
                args,
                timeout=30,
            )
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/audio-train/ingest":
            sample = body.get("sample") or body
            sid = str(body.get("source_id") or sample.get("source_id") or "manual").strip()
            ingest_body = json.dumps({
                "source_id": sid,
                "label": body.get("label") or sample.get("label") or sid,
                "kind": body.get("kind") or sample.get("kind") or "",
                "sample": sample if isinstance(sample, dict) else body,
            })
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "audio-train.py", ["ingest", ingest_body])
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/field-toolkit/defense":
            defense_id = str(body.get("defense_id", body.get("id", ""))).strip()
            if not defense_id:
                self._send(400, json.dumps({"ok": False, "error": "missing defense_id"}), "application/json")
                return
            enabled = body.get("enabled")
            args = ["toggle", defense_id]
            if enabled is not None:
                args.append("on" if enabled else "off")
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-toolkit-db.py", args)
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path in (
            "/api/field-toolkit/sever",
            "/api/field-toolkit/regional-disable",
            "/api/field-toolkit/human-threat",
            "/api/field-toolkit/hell-rip",
            "/api/field-toolkit/field-die",
            "/api/field-toolkit/laser-corridor",
            "/api/field-toolkit/disable",
        ):
            script = INSTALL_ROOT / "lib" / "field-toolkit-db.py"
            if path == "/api/field-toolkit/sever":
                ip = str(body.get("ip", "")).strip()
                if not ip:
                    self._send(400, json.dumps({"ok": False, "error": "missing ip"}), "application/json")
                    return
                payload = _nexus_py_json(script, ["sever", ip])
            elif path == "/api/field-toolkit/regional-disable":
                region = str(body.get("region", body.get("value", ""))).strip()
                if not region:
                    self._send(400, json.dumps({"ok": False, "error": "missing region"}), "application/json")
                    return
                args = ["regional", region]
                if body.get("field") and ":" not in region:
                    args.append(str(body.get("field")))
                payload = _nexus_py_json(script, args)
            elif path == "/api/field-toolkit/human-threat":
                payload = _nexus_py_json(script, ["human-threat"])
            elif path == "/api/field-toolkit/hell-rip":
                payload = _nexus_py_json(script, ["hell-rip"])
            elif path == "/api/field-toolkit/field-die":
                ip = str(body.get("ip", "")).strip()
                payload = _nexus_py_json(script, ["field-die"] + ([ip] if ip else []))
            elif path == "/api/field-toolkit/laser-corridor":
                ip = str(body.get("ip", "")).strip()
                if not ip:
                    self._send(400, json.dumps({"ok": False, "error": "missing ip"}), "application/json")
                    return
                payload = _nexus_py_json(script, ["laser-corridor", ip])
            else:
                payload = _nexus_py_json(
                    script,
                    ["disable", json.dumps(body, ensure_ascii=False)],
                )
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/host-attack/trash":
            pin_id = str(body.get("id", "")).strip()
            if not pin_id:
                self._send(400, json.dumps({"ok": False, "error": "missing id"}), "application/json")
                return
            ok = _nexus_host_map_trash_add(pin_id)
            if ok:
                map_py = INSTALL_ROOT / "lib" / "host-attack-map.py"
                if map_py.is_file():
                    env = os.environ.copy()
                    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
                    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
                    subprocess.run(
                        [sys.executable, str(map_py), "build-fast"],
                        capture_output=True,
                        timeout=45,
                        env=env,
                    )
            self._send(200 if ok else 500, json.dumps({"ok": ok, "id": pin_id}), "application/json")
            return

        if path == "/api/honorability/accept":
            domain = str(body.get("domain", body.get("host", ""))).strip().lower()
            if not domain:
                self._send(400, json.dumps({"ok": False, "error": "missing domain"}), "application/json")
                return
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "honorability-db.py", ["accept", domain])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/honorability/rate":
            domain = str(body.get("domain", "")).strip().lower()
            stars = body.get("stars")
            if not domain or stars is None:
                self._send(400, json.dumps({"ok": False, "error": "missing domain or stars"}), "application/json")
                return
            note = str(body.get("note", ""))[:200]
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "honorability-db.py",
                ["rate", domain, str(int(stars)), note],
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-rf/shield":
            enabled = body.get("enabled")
            auto_rfkill = body.get("auto_rfkill")
            lawful_kick = body.get("lawful_kick")
            shoot_to_kill = body.get("shoot_to_kill")
            if enabled is None:
                self._send(400, json.dumps({"ok": False, "error": "missing enabled"}), "application/json")
                return
            flag = "on" if enabled in (True, 1, "1", "true", "yes", "on") else "off"
            auto_flag = "on" if auto_rfkill in (True, 1, "1", "true", "yes", "on") else "off"
            lawful_flag = "on" if lawful_kick in (True, 1, "1", "true", "yes", "on", None) else "off"
            shoot_flag = "on" if shoot_to_kill in (True, 1, "1", "true", "yes", "on", None) else "off"
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "field-rf-sentinel.py",
                ["shield", flag, auto_flag, lawful_flag, shoot_flag],
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-rf/cycle":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-rf-sentinel.py", ["cycle"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/terror-spiderweb/rebuild":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "terror-spiderweb.py",
                ["build"],
                timeout=120,
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/lethal-enforcement/cycle":
            dry = body.get("dry_run") in (True, 1, "1", "true")
            args = ["cycle"] + (["--dry-run"] if dry else [])
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "lethal-enforcement.py", args)
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/hostess7-lethal-insight/ask":
            claim = str(body.get("claim") or "MERCILESS lethal heaven hell spatial trespass").strip()
            target = body.get("target") if isinstance(body.get("target"), dict) else {}
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-lethal-insight.py",
                ["ask", claim, json.dumps(target)],
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/queen-boot":
            script = _queen_boot_script()
            if not script.is_file():
                self._send(500, json.dumps({"ok": False, "error": "queen_boot_missing"}), "application/json")
                return
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            env.setdefault("QUEEN_ROOT", str(INSTALL_ROOT if (INSTALL_ROOT / ".queen-inside").is_file() else INSTALL_ROOT.parent / "Queen"))
            env.setdefault("HOSTESS7_ROOT", str(INSTALL_ROOT / "Hostess7"))
            for k in ("NEXUS_AI_SECURE_CHANNEL", "QUEEN_AI_TELEMETRY_OK", "QUEEN_GROK_BUILD", "QUEEN_GROK_BUILD_SECURE", "QUEEN_FIELD_GPU"):
                env.setdefault(k, "1")
            act = str(body.get("action") or "").lower()
            timeout = 7200 if act in ("rebuild", "build", "full-boot", "boot") else 600 if act in ("login", "zac_restore") else 60
            try:
                proc = subprocess.run(
                    [sys.executable, str(script), "dispatch"],
                    input=json.dumps(body if isinstance(body, dict) else {}),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=env,
                )
                payload = json.loads(proc.stdout or "{}")
            except subprocess.TimeoutExpired:
                payload = {"ok": False, "error": "timeout"}
            except json.JSONDecodeError:
                payload = {"ok": False, "error": "dispatch_failed"}
            self._send(200 if payload.get("ok", True) else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/grok-build":
            script = _grok_build_script()
            if not script.is_file():
                self._send(500, json.dumps({"ok": False, "error": "grok_build_missing"}), "application/json")
                return
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            env.setdefault("QUEEN_ROOT", str(INSTALL_ROOT if (INSTALL_ROOT / ".queen-inside").is_file() else INSTALL_ROOT.parent / "Queen"))
            for k in ("NEXUS_AI_SECURE_CHANNEL", "QUEEN_AI_TELEMETRY_OK", "QUEEN_GROK_BUILD", "QUEEN_GROK_BUILD_SECURE"):
                env.setdefault(k, "1")
            timeout = 120 if str(body.get("action") or "").lower() in ("acp_start", "start") else 30
            try:
                proc = subprocess.run(
                    [sys.executable, str(script), "dispatch"],
                    input=json.dumps(body if isinstance(body, dict) else {}),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=env,
                )
                payload = json.loads(proc.stdout or "{}")
            except subprocess.TimeoutExpired:
                payload = {"ok": False, "error": "timeout"}
            except json.JSONDecodeError:
                payload = {"ok": False, "error": "dispatch_failed"}
            self._send(200 if payload.get("ok", True) else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/queen-build":
            script = _queen_build_script()
            if not script.is_file():
                self._send(500, json.dumps({"ok": False, "error": "queen_build_missing"}), "application/json")
                return
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            env.setdefault("QUEEN_ROOT", str(INSTALL_ROOT if (INSTALL_ROOT / ".queen-inside").is_file() else INSTALL_ROOT.parent / "Queen"))
            timeout = 3700 if str(body.get("action") or "").lower() in ("run", "run-all", "run_all", "build", "build_all") else 60
            try:
                proc = subprocess.run(
                    [sys.executable, str(script), "dispatch"],
                    input=json.dumps(body if isinstance(body, dict) else {}),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=env,
                )
                payload = json.loads(proc.stdout or "{}")
            except subprocess.TimeoutExpired:
                payload = {"ok": False, "error": "timeout"}
            except json.JSONDecodeError:
                payload = {"ok": False, "error": "dispatch_failed"}
            self._send(200 if payload.get("ok", True) else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/logic-gate/ingress":
            gate_body = body if isinstance(body, dict) else {}
            payload = str(
                gate_body.get("payload") or gate_body.get("message") or gate_body.get("text") or ""
            )
            proc = subprocess.run(
                [sys.executable, str(INSTALL_ROOT / "lib" / "nexus-logic-gate.py"), "ingress"],
                input=json.dumps(gate_body),
                capture_output=True,
                text=True,
                timeout=20,
                env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL_ROOT), "NEXUS_STATE_DIR": str(STATE_DIR)},
            )
            try:
                gate_out = json.loads(proc.stdout or "{}")
            except json.JSONDecodeError:
                gate_out = {"ok": False, "error": "logic_gate_failed"}
            self._send(200 if gate_out.get("permit") else 403, json.dumps(gate_out), "application/json")
            return

        if path == "/api/logic-gate/egress":
            gate_body = body if isinstance(body, dict) else {}
            proc = subprocess.run(
                [sys.executable, str(INSTALL_ROOT / "lib" / "nexus-logic-gate.py"), "egress"],
                input=json.dumps(gate_body),
                capture_output=True,
                text=True,
                timeout=20,
                env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL_ROOT), "NEXUS_STATE_DIR": str(STATE_DIR)},
            )
            try:
                gate_out = json.loads(proc.stdout or "{}")
            except json.JSONDecodeError:
                gate_out = {"ok": False, "error": "logic_gate_failed"}
            self._send(200 if gate_out.get("permit") else 403, json.dumps(gate_out), "application/json")
            return

        _TRAIN_TRACK_TIMEOUTS = {
            "master_curriculum": 150,
            "curriculum": 150,
            "codecraft": 240,
            "iq_battery": 200,
            "self_interaction": 200,
            "turing_battery": 300,
            "neural_suite": 180,
            "omnibus": 240,
            "calculator": 200,
            "biology": 200,
            "engineering": 200,
            "combat": 200,
            "mos": 200,
        }

        if path in ("/api/ironclad/realize", "/api/ironclad/seal"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "ironclad-plate.py", ["realize"], timeout=30)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/training/assess", "/api/hostess7-training/assess"):
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess7-training.py", ["assess"], timeout=60)
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/training/solidify", "/api/hostess7/training/complete"):
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-training.py",
                ["complete", "--skip-omnibus"],
                timeout=600,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/training/self-interaction", "/api/hostess7-training/self-interaction"):
            rounds = int(body.get("rounds") or 6)
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-training.py",
                ["self-interaction", str(rounds)],
                timeout=200,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/training/author", "/api/hostess7-training/author"):
            track = str(body.get("track") or body.get("track_id") or "").strip()
            args = ["author"]
            if track:
                args.append(track)
            if body.get("force"):
                args.append("--force")
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-training-author.py",
                args,
                timeout=120,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/training/gaps", "/api/hostess7-training/gaps"):
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-training-author.py",
                ["gaps"],
                timeout=90,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/training/curriculum-step", "/api/hostess7-training/curriculum-step"):
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-training.py",
                ["curriculum-step"],
                timeout=150,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path in ("/api/hostess7/training/iq", "/api/hostess7-training/iq"):
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-truth-rating.py",
                ["iq-test"],
                timeout=300,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path.startswith("/api/hostess7/training/track/") or path.startswith("/api/hostess7-training/track/"):
            track_id = path.split("/track/", 1)[-1].strip("/")
            if not track_id:
                self._send(400, json.dumps({"ok": False, "error": "track_required"}), "application/json")
                return
            args = ["track", track_id]
            if body.get("ocr_train"):
                args.append("--ocr-train")
            timeout = _TRAIN_TRACK_TIMEOUTS.get(track_id, 180)
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "hostess7-training.py",
                args,
                timeout=timeout,
            )
            self._send(200, json.dumps(payload or {"ok": False}), "application/json")
            return

        if path == "/api/hostess7-command":
            script = INSTALL_ROOT / "lib" / "hostess7-command.py"
            if not script.is_file():
                self._send(500, json.dumps({"ok": False, "error": "script_missing"}), "application/json")
                return
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            env.setdefault("HOSTESS7_ROOT", str(_resolve_hostess7_root()))
            if os.environ.get("NEXUS_LOGIC_GATE", "1") == "1":
                msg = str(body.get("message") or body.get("query") or "")
                if msg.strip() and str(body.get("action") or "ask").lower() in ("ask", "message", "chat"):
                    gate = _nexus_py_json(
                        INSTALL_ROOT / "lib" / "nexus-logic-gate.py",
                        ["ingress", msg],
                        timeout=15,
                    )
                    if not gate.get("permit"):
                        self._send(
                            403,
                            json.dumps({
                                "ok": False,
                                "logic_gate": gate,
                                "reply": "Equipment logic gate held inbound message.",
                                "threat_warn_level": "high",
                            }),
                            "application/json",
                        )
                        return
            timeout = 180 if str(body.get("action") or "").lower() in ("teach-art", "teach_art") else 120
            try:
                proc = subprocess.run(
                    [sys.executable, str(script), "dispatch"],
                    input=json.dumps(body if isinstance(body, dict) else {}),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=env,
                )
                payload = json.loads(proc.stdout or "{}")
            except subprocess.TimeoutExpired:
                payload = {"ok": False, "error": "timeout"}
            except json.JSONDecodeError:
                payload = {"ok": False, "error": "dispatch_failed"}
            self._send(200 if payload.get("ok", True) else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/plugins/toggle":
            plugin_id = str(body.get("id", body.get("plugin_id", ""))).strip()
            if not plugin_id:
                self._send(400, json.dumps({"ok": False, "error": "missing id"}), "application/json")
                return
            enabled = body.get("enabled") in (True, 1, "1", "true", "yes", "on")
            flag = "on" if enabled else "off"
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "nexus-plugins.py",
                ["enable", flag, plugin_id],
            )
            if payload.get("ok"):
                _nexus_py_json(INSTALL_ROOT / "lib" / "nexus-plugins.py", ["merge"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/police-agencies/select":
            agency_id = str(body.get("agency_id", body.get("id", ""))).strip()
            if not agency_id:
                self._send(400, json.dumps({"ok": False, "error": "missing agency_id"}), "application/json")
                return
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "police-agency-db.py", ["select", agency_id])
            self._send(200 if payload.get("ok") else 404, json.dumps(payload), "application/json")
            return

        if path == "/api/police-agencies/import":
            agency_id = str(body.get("agency_id", "")).strip()
            format_id = str(body.get("format_id", "")).strip()
            payload_text = str(body.get("payload", body.get("data", "")))
            filename = str(body.get("filename", ""))[:120]
            images = body.get("images") if isinstance(body.get("images"), list) else None
            if not agency_id or not format_id or not payload_text:
                self._send(400, json.dumps({"ok": False, "error": "missing agency_id, format_id, or payload"}), "application/json")
                return
            import_doc = {
                "agency_id": agency_id,
                "format_id": format_id,
                "payload": payload_text,
                "filename": filename,
                "images": images,
            }
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            proc = subprocess.run(
                [sys.executable, str(INSTALL_ROOT / "lib" / "police-agency-db.py"), "import-json", json.dumps(import_doc)],
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
            )
            try:
                result = json.loads(proc.stdout or "{}")
            except json.JSONDecodeError:
                result = {"ok": False, "error": "import_failed"}
            self._send(200 if result.get("ok") else 400, json.dumps(result), "application/json")
            return

        if path == "/api/program-tags/apply":
            tag_ids = body.get("tag_ids") or body.get("tags")
            if isinstance(tag_ids, str):
                tag_ids = [t.strip() for t in tag_ids.split(",") if t.strip()]
            if not tag_ids:
                self._send(400, json.dumps({"ok": False, "error": "missing tag_ids"}), "application/json")
                return
            apply_doc = {
                "tag_ids": tag_ids,
                "record_key": str(body.get("record_key", "")).strip(),
                "lat": body.get("lat"),
                "lon": body.get("lon"),
                "coords": str(body.get("coords", "")),
                "place": str(body.get("place", "")),
                "address": str(body.get("address", "")),
                "city": str(body.get("city", "")),
                "country": str(body.get("country", "")),
                "label": str(body.get("label", "")),
                "notes": str(body.get("notes", "")),
            }
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            proc = subprocess.run(
                [sys.executable, str(INSTALL_ROOT / "lib" / "program-tags-db.py"), "apply-json", json.dumps(apply_doc)],
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
            )
            try:
                result = json.loads(proc.stdout or "{}")
            except json.JSONDecodeError:
                result = {"ok": False, "error": "tag_apply_failed"}
            self._send(200 if result.get("ok") else 400, json.dumps(result), "application/json")
            return

        if path == "/api/operator/location":
            mode = str(body.get("mode", "gps")).strip().lower()
            loc_py = INSTALL_ROOT / "lib" / "operator-location.py"
            if mode == "wireless":
                payload = _nexus_py_json(loc_py, ["wireless"])
            elif mode == "address":
                address = str(body.get("address", "")).strip()
                if not address:
                    self._send(400, json.dumps({"ok": False, "error": "missing address"}), "application/json")
                    return
                payload = _nexus_py_json(loc_py, ["address", address])
            elif mode == "gps":
                lat = body.get("lat")
                lon = body.get("lon")
                if lat is None or lon is None:
                    self._send(400, json.dumps({"ok": False, "error": "missing lat/lon"}), "application/json")
                    return
                label = str(body.get("label", ""))[:120]
                args = ["gps", str(lat), str(lon)]
                if label:
                    args.append(label)
                payload = _nexus_py_json(loc_py, args)
            else:
                self._send(400, json.dumps({"ok": False, "error": "invalid mode"}), "application/json")
                return
            if payload.get("ok") is False and payload.get("error"):
                self._send(500, json.dumps(payload), "application/json")
                return
            map_py = INSTALL_ROOT / "lib" / "host-attack-map.py"
            if map_py.is_file():
                env = os.environ.copy()
                env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
                env["NEXUS_STATE_DIR"] = str(STATE_DIR)
                subprocess.run(
                    [sys.executable, str(map_py), "build-fast"],
                    capture_output=True,
                    timeout=45,
                    env=env,
                )
            census_py = INSTALL_ROOT / "lib" / "census-field-populate.py"
            if census_py.is_file() and mode in ("address", "gps", "wireless"):
                env = os.environ.copy()
                env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
                env["NEXUS_STATE_DIR"] = str(STATE_DIR)
                subprocess.run(
                    [sys.executable, str(census_py), "populate"],
                    capture_output=True,
                    timeout=60,
                    env=env,
                )
            self._send(200, json.dumps({"ok": True, **payload}), "application/json")
            return

        if path == "/api/census-field/populate":
            census_py = INSTALL_ROOT / "lib" / "census-field-populate.py"
            address = str(body.get("address", "")).strip()
            args = ["populate"]
            if address:
                args.append(address)
            payload = _nexus_py_json(census_py, args)
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/thermal-earth/rebuild":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "thermal-earth-field.py", ["build"])
            self._send(200 if payload.get("schema") else 500, json.dumps(payload), "application/json")
            return

        if path == "/api/precision-field/rebuild":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "precision-field.py", ["build"])
            self._send(200 if payload.get("schema") else 500, json.dumps(payload), "application/json")
            return

        if path == "/api/precision-field/place":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "precision-field.py",
                ["place", json.dumps(body)],
            )
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/autosanitize/toggle":
            enabled = bool(body.get("enabled", True))
            ok = _run_nexus_autosanitize_toggle(enabled)
            self._send(200 if ok else 500, json.dumps({"ok": ok, "enabled": enabled}), "application/json")
            return

        if path == "/api/autosanitize/undo":
            action_id = str(body.get("id", "")).strip()
            if not action_id:
                self._send(400, json.dumps({"ok": False, "error": "missing id"}), "application/json")
                return
            ok = _run_nexus_undo(action_id)
            self._send(200 if ok else 404, json.dumps({"ok": ok, "id": action_id}), "application/json")
            return

        if path == "/api/paranoia/toggle":
            block = bool(body.get("block", False))
            ok = _run_nexus_paranoia("block_on" if block else "block_off")
            self._send(200 if ok else 500, json.dumps({"ok": ok, "block": block}), "application/json")
            return

        if path == "/api/paranoia/disable":
            incident_id = str(body.get("id", "")).strip()
            if not incident_id:
                self._send(400, json.dumps({"ok": False, "error": "missing id"}), "application/json")
                return
            ok = _run_nexus_paranoia("disable", incident_id)
            self._send(200 if ok else 404, json.dumps({"ok": ok, "id": incident_id}), "application/json")
            return

        if path == "/api/nexus/restart":
            policy = str(body.get("policy", "block")).strip().lower()
            offender = str(body.get("offender_ip", body.get("offender", ""))).strip()
            script = INSTALL_ROOT / "lib" / "shutdown-guard.sh"
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            cmd = (
                f"source {INSTALL_ROOT}/lib/nexus-common.sh && "
                f"source {INSTALL_ROOT}/lib/firewall-sentinel.sh && "
                f"source {INSTALL_ROOT}/lib/threat-vectors.sh && "
                f"source {INSTALL_ROOT}/lib/packet-oracle.sh && "
                f"source {INSTALL_ROOT}/lib/paranoia-mode.sh && "
                f"source {script} && "
                f"nexus_shutdown_restart '{policy}' '{offender}'"
            )
            proc = subprocess.run(
                ["bash", "-c", cmd],
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
            )
            ok = proc.returncode == 0
            self._send(
                200 if ok else 500,
                json.dumps({"ok": ok, "policy": policy, "offender_ip": offender}),
                "application/json",
            )
            return

        if path == "/api/firewall/authorize":
            ip = str(body.get("ip", "")).strip()
            direction = str(body.get("direction", "out")).strip().lower() or "out"
            label = str(body.get("label", "")).strip()
            if not ip:
                self._send(400, json.dumps({"ok": False, "error": "missing ip"}), "application/json")
                return
            if direction not in ("in", "out", "both"):
                direction = "out"
            ok = _run_nexus_firewall_trust("authorize", ip, direction, label)
            self._send(
                200 if ok else 500,
                json.dumps({"ok": ok, "ip": ip, "direction": direction, "label": label}),
                "application/json",
            )
            return

        if path == "/api/firewall/block":
            ip = str(body.get("ip", "")).strip()
            direction = str(body.get("direction", "out")).strip().lower() or "out"
            reason = str(body.get("reason", "harm_candidate")).strip()
            duration = str(body.get("duration", "day")).strip().lower() or "day"
            if not ip:
                self._send(400, json.dumps({"ok": False, "error": "missing ip"}), "application/json")
                return
            script = INSTALL_ROOT / "lib" / "firewall-sentinel.sh"
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            safe_ip = ip.replace("'", "'\"'\"'")
            if duration in ("forever", "permanent"):
                block_fn = f"nexus_firewall_block_ip_forever {direction} '{safe_ip}' '{reason}'"
            else:
                timeout = str(body.get("timeout", 86400))
                block_fn = f"nexus_firewall_block_ip {direction} '{safe_ip}' {timeout} '{reason}'"
            cmd = (
                f"source {INSTALL_ROOT}/lib/nexus-common.sh && nexus_load_config && "
                f"source {script} && {block_fn}"
            )
            proc = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=20, env=env)
            ok = proc.returncode == 0
            self._send(
                200 if ok else 500,
                json.dumps({"ok": ok, "ip": ip, "duration": duration}),
                "application/json",
            )
            return

        if path == "/api/firewall/unblock":
            ip = str(body.get("ip", "")).strip()
            direction = str(body.get("direction", "out")).strip().lower() or "out"
            duration = str(body.get("duration", "day")).strip().lower() or "day"
            if not ip:
                self._send(400, json.dumps({"ok": False, "error": "missing ip"}), "application/json")
                return
            script = INSTALL_ROOT / "lib" / "firewall-sentinel.sh"
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            safe_ip = ip.replace("'", "'\"'\"'")
            if duration in ("day", "1day", "24h"):
                unblock_fn = f"nexus_firewall_temp_allow_ip {direction} '{safe_ip}' 86400"
            else:
                unblock_fn = f"nexus_firewall_unblock_ip {direction} '{safe_ip}'"
            cmd = (
                f"source {INSTALL_ROOT}/lib/nexus-common.sh && nexus_load_config && "
                f"source {script} && {unblock_fn}"
            )
            proc = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=20, env=env)
            ok = proc.returncode == 0
            self._send(
                200 if ok else 500,
                json.dumps({"ok": ok, "ip": ip, "duration": duration}),
                "application/json",
            )
            return

        if path in ("/api/attack-kit/disable", "/api/attack-kit/kill"):
            ip = str(body.get("ip", "")).strip()
            vector = str(body.get("vector", "HOSTILE")).strip() or "HOSTILE"
            severity = str(body.get("severity", "high")).strip() or "high"
            reason = str(body.get("reason", "target_kill" if path.endswith("/kill") else "operator_disable")).strip()
            reason = reason or ("target_kill" if path.endswith("/kill") else "operator_disable")
            if not ip:
                self._send(400, json.dumps({"ok": False, "error": "missing ip"}), "application/json")
                return
            guard_script = INSTALL_ROOT / "lib" / "friendly-guard.py"
            if guard_script.is_file():
                import importlib.util

                spec = importlib.util.spec_from_file_location("friendly_guard_http", guard_script)
                fg_mod = importlib.util.module_from_spec(spec)
                assert spec and spec.loader
                spec.loader.exec_module(fg_mod)
                monitor = body.get("monitor") if isinstance(body.get("monitor"), dict) else None
                refuse, guard_reason = fg_mod.refuse_kill(ip, monitor=monitor)
                if refuse:
                    self._send(
                        403,
                        json.dumps({
                            "ok": False,
                            "friendly_refused": True,
                            "immutable": True,
                            "reason": guard_reason,
                            "ip": ip,
                        }),
                        "application/json",
                    )
                    return
            script = INSTALL_ROOT / "lib" / "field-attack-kit.py"
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            cmd = "kill" if path.endswith("/kill") else "disable"
            proc = subprocess.run(
                [sys.executable, str(script), cmd, ip, vector, severity],
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
            )
            ok = proc.returncode == 0
            try:
                payload = json.loads(proc.stdout or "{}")
            except json.JSONDecodeError:
                payload = {"ok": ok, "ip": ip, "killed": ok}
            self._send(200 if ok else 500, json.dumps(payload), "application/json")
            return

        if path == "/api/attack-kit/crush-hot":
            script = INSTALL_ROOT / "lib" / "field-attack-kit.py"
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            proc = subprocess.run(
                [sys.executable, str(script), "crush-hot"],
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
            )
            ok = proc.returncode == 0
            try:
                payload = json.loads(proc.stdout or "{}")
            except json.JSONDecodeError:
                payload = {"ok": ok}
            self._send(200 if ok else 500, json.dumps(payload), "application/json")
            return

        if path == "/api/attack-kit/check-online":
            ip = str(body.get("ip", "")).strip()
            if not ip:
                self._send(400, json.dumps({"ok": False, "error": "missing ip"}), "application/json")
                return
            script = INSTALL_ROOT / "lib" / "field-attack-kit.py"
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            proc = subprocess.run(
                [sys.executable, str(script), "check-online", ip],
                capture_output=True,
                text=True,
                timeout=45,
                env=env,
            )
            try:
                payload = json.loads(proc.stdout or "{}")
            except json.JSONDecodeError:
                payload = {"ok": False, "ip": ip}
            self._send(200 if proc.returncode == 0 else 500, json.dumps(payload), "application/json")
            return

        if path == "/api/attack-kit/nokill":
            ip = str(body.get("ip", "")).strip()
            vector = str(body.get("vector", "HOSTILE")).strip() or "HOSTILE"
            severity = str(body.get("severity", "high")).strip() or "high"
            reason = str(body.get("reason", "operator_nokill")).strip() or "operator_nokill"
            if not ip:
                self._send(400, json.dumps({"ok": False, "error": "missing ip"}), "application/json")
                return
            script = INSTALL_ROOT / "lib" / "field-attack-kit.py"
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            proc = subprocess.run(
                [sys.executable, str(script), "nokill", ip, vector, severity, reason],
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
            )
            try:
                payload = json.loads(proc.stdout or "{}")
            except json.JSONDecodeError:
                payload = {"ok": proc.returncode == 0, "ip": ip}
            self._send(200 if proc.returncode == 0 else 500, json.dumps(payload), "application/json")
            return

        if path == "/api/attack-kit/rekill":
            ip = str(body.get("ip", "")).strip()
            vector = str(body.get("vector", "HOSTILE")).strip() or "HOSTILE"
            severity = str(body.get("severity", "high")).strip() or "high"
            if not ip:
                self._send(400, json.dumps({"ok": False, "error": "missing ip"}), "application/json")
                return
            guard_script = INSTALL_ROOT / "lib" / "friendly-guard.py"
            if guard_script.is_file():
                import importlib.util

                spec = importlib.util.spec_from_file_location("friendly_guard_rekill", guard_script)
                fg_mod = importlib.util.module_from_spec(spec)
                assert spec and spec.loader
                spec.loader.exec_module(fg_mod)
                refuse, guard_reason = fg_mod.refuse_kill(ip)
                if refuse:
                    self._send(
                        403,
                        json.dumps({
                            "ok": False,
                            "friendly_refused": True,
                            "reason": guard_reason,
                            "ip": ip,
                        }),
                        "application/json",
                    )
                    return
            script = INSTALL_ROOT / "lib" / "field-attack-kit.py"
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            proc = subprocess.run(
                [sys.executable, str(script), "rekill", ip, vector, severity],
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
            )
            try:
                payload = json.loads(proc.stdout or "{}")
            except json.JSONDecodeError:
                payload = {"ok": proc.returncode == 0, "ip": ip}
            self._send(200 if proc.returncode == 0 else 500, json.dumps(payload), "application/json")
            return

        if path == "/api/attack-kit/sync-field":
            kit = INSTALL_ROOT / "lib" / "field-attack-kit.sh"
            ok, _ = _run_nexus_bash(
                f"source {INSTALL_ROOT}/lib/nexus-settings.sh && "
                f"source {kit} && nexus_field_attack_sync_from_memory && nexus_field_attack_apply_registry",
                timeout=60,
            )
            self._send(200 if ok else 500, json.dumps({"ok": ok}), "application/json")
            return

        if path == "/api/hostile-ai/destroy":
            script = INSTALL_ROOT / "lib" / "hostile-ai-destroy.py"
            payload = _nexus_py_json(
                script,
                ["destroy", json.dumps(body, ensure_ascii=False)],
                timeout=90,
            )
            self._send(200 if payload.get("ok") else 400, json.dumps(payload), "application/json")
            return

        if path == "/api/planetary-observer/cycle":
            payload = _nexus_py_json(
                INSTALL_ROOT / "lib" / "planetary-observer.py",
                ["cycle"],
                timeout=120,
            )
            self._send(200 if payload.get("ok", True) else 500, json.dumps(payload), "application/json")
            return

        if path == "/api/firewall/revoke":
            ip = str(body.get("ip", "")).strip()
            direction = str(body.get("direction", "both")).strip().lower() or "both"
            if not ip:
                self._send(400, json.dumps({"ok": False, "error": "missing ip"}), "application/json")
                return
            ok = _run_nexus_firewall_trust("revoke", ip, direction)
            self._send(
                200 if ok else 500,
                json.dumps({"ok": ok, "ip": ip, "direction": direction}),
                "application/json",
            )
            return

        if path == "/api/paranoia/reenable":
            incident_id = str(body.get("id", "")).strip()
            if not incident_id:
                self._send(400, json.dumps({"ok": False, "error": "missing id"}), "application/json")
                return
            ok = _run_nexus_paranoia("reenable", incident_id)
            self._send(200 if ok else 404, json.dumps({"ok": ok, "id": incident_id}), "application/json")
            return

        if path == "/api/settings":
            key = str(body.get("key", "")).strip()
            val = str(body.get("value", body.get("val", ""))).strip()
            bulk = body.get("settings")
            if isinstance(bulk, dict) and bulk:
                ok_all = True
                for k, v in bulk.items():
                    if not _run_nexus_settings_set(str(k), str(v)):
                        ok_all = False
                self._send(200 if ok_all else 500, json.dumps({"ok": ok_all}), "application/json")
                return
            if not key:
                self._send(400, json.dumps({"ok": False, "error": "missing key"}), "application/json")
                return
            if val not in ("0", "1"):
                self._send(400, json.dumps({"ok": False, "error": "value must be 0 or 1"}), "application/json")
                return
            ok = _run_nexus_settings_set(key, val)
            self._send(200 if ok else 500, json.dumps({"ok": ok, "key": key, "value": val}), "application/json")
            return

        if path == "/api/adblock/load":
            preset = str(body.get("preset", "")).strip()
            url = str(body.get("url", "")).strip()
            if not preset and not url:
                self._send(400, json.dumps({"ok": False, "error": "preset or url required"}), "application/json")
                return
            ok = _run_nexus_adblock_load(preset=preset, url=url)
            if ok and body.get("apply", True):
                _run_nexus_adblock_apply()
            self._send(200 if ok else 500, json.dumps({"ok": ok, "preset": preset, "url": url}), "application/json")
            return

        if path == "/api/adblock/toggle":
            enabled = bool(body.get("enabled", body.get("value", "0") in ("1", True, "true")))
            ok = _run_nexus_settings_set("NEXUS_ADBLOCK", "1" if enabled else "0")
            self._send(200 if ok else 500, json.dumps({"ok": ok, "enabled": enabled}), "application/json")
            return

        if path == "/api/adblock/apply":
            ok = _run_nexus_adblock_apply()
            self._send(200 if ok else 500, json.dumps({"ok": ok}), "application/json")
            return

        if path == "/api/adblock/policy":
            policy = str(body.get("policy", "annoyance")).strip().lower()
            if policy not in ("annoyance", "fair", "strict"):
                self._send(400, json.dumps({"ok": False, "error": "invalid policy"}), "application/json")
                return
            inner = _nexus_shell_prelude() + f"nexus_adblock_set_policy '{policy}'"
            ok, _ = _run_nexus_bash(inner, timeout=120)
            self._send(200 if ok else 500, json.dumps({"ok": ok, "policy": policy}), "application/json")
            return

        if path == "/api/adblock/site-policy":
            domain = str(body.get("domain", "")).strip().lower()
            policy = str(body.get("policy", "ads_required")).strip().lower()
            note = str(body.get("note", "")).strip()
            if not domain:
                self._send(400, json.dumps({"ok": False, "error": "missing domain"}), "application/json")
                return
            safe_d = domain.replace("'", "'\"'\"'")
            safe_p = policy.replace("'", "'\"'\"'")
            safe_n = note.replace("'", "'\"'\"'")
            inner = _nexus_shell_prelude() + f"nexus_adblock_site_policy '{safe_d}' '{safe_p}' '{safe_n}'"
            ok, _ = _run_nexus_bash(inner, timeout=30)
            if ok:
                _run_nexus_adblock_apply()
            self._send(200 if ok else 500, json.dumps({"ok": ok, "domain": domain, "policy": policy}), "application/json")
            return

        if path == "/api/pest/eradicate":
            ip = str(body.get("ip", "")).strip()
            pid = str(body.get("pid", body.get("process_id", "0"))).strip() or "0"
            vector = str(body.get("vector", "HARM_CANDIDATE")).strip()
            exe = str(body.get("exe", body.get("path", ""))).strip()
            if not ip and pid == "0":
                self._send(400, json.dumps({"ok": False, "error": "ip or pid required"}), "application/json")
                return
            safe_ip = ip.replace("'", "'\"'\"'")
            safe_exe = exe.replace("'", "'\"'\"'")
            inner = (
                f"source {INSTALL_ROOT}/lib/nexus-common.sh && nexus_load_config && "
                f"source {INSTALL_ROOT}/lib/firewall-sentinel.sh && "
                f"source {INSTALL_ROOT}/lib/firewall-trust.sh && "
                f"source {INSTALL_ROOT}/lib/self-access.sh && "
                f"source {INSTALL_ROOT}/lib/pest-arsenal.sh && "
                f"nexus_pest_eradicate '{safe_ip}' '{pid}' '{vector}' '{safe_exe}'"
            )
            ok, _ = _run_nexus_bash(inner, timeout=45)
            self._send(
                200 if ok else 500,
                json.dumps({"ok": ok, "ip": ip, "pid": pid, "vector": vector}),
                "application/json",
            )
            return

        self._send(404, "not found", "text/plain")


def main():
    os.chdir(PANEL_DIR)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
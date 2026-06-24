#!/usr/bin/env python3
"""Local threat panel server — HTTPS on localhost only (Hostess7-secured)."""

import json
import os
import ssl
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9477
_BOOT = Path.cwd()
PANEL_DIR = (Path(sys.argv[2]) if len(sys.argv) > 2 else Path("panel")).resolve()
STATUS_JSON = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("threat-panel.json")
STATE_DIR = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL_ROOT = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
_TLS_CERT_ARG = Path(sys.argv[4]).expanduser() if len(sys.argv) > 4 and sys.argv[4] else None
_TLS_KEY_ARG = Path(sys.argv[5]).expanduser() if len(sys.argv) > 5 and sys.argv[5] else None
USE_TLS = os.environ.get("NEXUS_PANEL_TLS", "1") == "1"


def _readable(path: Path) -> bool:
    try:
        return path.is_file() and os.access(path, os.R_OK)
    except OSError:
        return False


def _resolve_tls_paths() -> tuple[Path | None, Path | None]:
    """Absolute cert/key paths — must run before chdir(PANEL_DIR). Prefer readable certs."""
    cert_candidates: list[Path] = []
    key_candidates: list[Path] = []
    if _TLS_CERT_ARG:
        cert_candidates.append(_TLS_CERT_ARG if _TLS_CERT_ARG.is_absolute() else (_BOOT / _TLS_CERT_ARG).resolve())
    if _TLS_KEY_ARG:
        key_candidates.append(_TLS_KEY_ARG if _TLS_KEY_ARG.is_absolute() else (_BOOT / _TLS_KEY_ARG).resolve())
    for base in (INSTALL_ROOT / ".nexus-state", _BOOT / ".nexus-state", STATE_DIR):
        cert_candidates.append((base / "tls" / "nexus-panel.crt").resolve())
        key_candidates.append((base / "tls" / "nexus-panel.key").resolve())
    cert = next((p for p in cert_candidates if _readable(p)), None)
    key = next((p for p in key_candidates if _readable(p)), None)
    if cert and key:
        return cert, key
    cert = next((p for p in cert_candidates if p.is_file()), None)
    key = next((p for p in key_candidates if p.is_file()), None)
    return cert, key

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
    "gatekeeper",
    "host_attacks",
    "planetary_observer",
    "us_field",
    "field_command",
    "angel_dossiers",
    "human_dossier",
    "angel_research",
    "browser_awareness",
    "settings",
    "field_brain",
})


def _read_install_version() -> str:
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "nexus_version", INSTALL_ROOT / "lib" / "nexus_version.py",
        )
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.read_version(str(INSTALL_ROOT))
    except Exception:
        pass
    return os.environ.get("NEXUS_VERSION", "unknown")


def _read_nexus_poll_seconds() -> dict[str, int]:
    """Adaptive panel poll intervals (seconds) — mirrors nexus.conf defaults."""
    conf = INSTALL_ROOT / "config" / "nexus.conf"
    out = {"calm": 5, "alert": 5, "storm": 3}
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
    version = _read_install_version()
    if not STATUS_JSON.is_file():
        if full:
            return "{}"
        shell = {
            "field": True,
            "panel_ready": False,
            "version": version,
            "panel_build": "military-v82",
            "gatekeeper": {"connections": [], "harm_candidates": 0},
        }
        shell.update(_panel_poll_meta(shell))
        return json.dumps(shell, ensure_ascii=False)
    raw = STATUS_JSON.read_text(encoding="utf-8")
    if full:
        try:
            doc = json.loads(raw)
            if isinstance(doc, dict):
                doc.update(_panel_poll_meta(doc))
                return json.dumps(doc, ensure_ascii=False)
        except json.JSONDecodeError:
            pass
        return raw
    try:
        doc = json.loads(raw)
        if isinstance(doc, dict):
            for key in PANEL_PARALLEL_KEYS:
                doc.pop(key, None)
            doc["version"] = version
            doc["panel_build"] = "military-v82"
            doc.update(_panel_poll_meta(doc))
        return json.dumps(doc, ensure_ascii=False)
    except json.JSONDecodeError:
        return raw


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
        return bool(val.get("points")) or bool(val.get("updated"))
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
        return bool(val.get("intel_digest")) and bool(val.get("capabilities"))
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
    """Locate git tree with stealth_install.sh for panel UPDATE apply."""
    candidates: list[Path] = []
    src = _load_nexus_shield_source()
    if src:
        candidates.append(Path(src))
    candidates.extend([
        INSTALL_ROOT,
        INSTALL_ROOT.parent,
        Path("/home/default/Desktop/SG/Latest/NEXUS-Shield"),
        Path("/home/default/Desktop/SG/NEXUS-Shield"),
    ])
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
        for _ in range(5):
            install = cur / "stealth_install.sh"
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
    git_dir: Path,
    install_sh: Path,
    token: str,
    target: str,
    previous: str,
) -> bool:
    apply_sh = INSTALL_ROOT / "lib" / "nexus-update-apply.sh"
    if not apply_sh.is_file():
        apply_sh = git_dir / "lib" / "nexus-update-apply.sh"
    if not apply_sh.is_file():
        return False
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
        "NEXUS_UPDATE_GIT_DIR": str(git_dir),
        "NEXUS_UPDATE_TARGET": target,
        "NEXUS_UPDATE_PREVIOUS": previous,
        "NEXUS_UPDATE_INSTALL_SH": str(install_sh),
    })
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
                cwd=str(git_dir),
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


def _nexus_py_json(script: Path, args: list[str], timeout: int = 25) -> dict:
    if not script.is_file():
        return {"ok": False, "error": "script_missing"}
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
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


def _serve_panel_html(handler: "Handler", target: Path) -> None:
    if target.suffix == ".html" and target.name == "threat-panel.html":
        try:
            body = target.read_text(encoding="utf-8")
        except OSError:
            handler._send(404, "not found", "text/plain")
            return
        handler._send(200, body, "text/html")
        return
    try:
        handler._send(200, target.read_bytes(), "text/html" if target.suffix == ".html" else "application/octet-stream")
    except OSError:
        handler._send(404, "not found", "text/plain")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        return

    def _send(self, code, body, ctype, extra_headers: dict[str, str] | None = None):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
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
                if not STATUS_JSON.is_file() or STATUS_JSON.stat().st_size < 128:
                    _nexus_shell_publish_panel()
            except OSError:
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
                default={"points": [], "updated": None},
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
            payload = _panel_slice(
                "terror_spiderweb",
                live=_nexus_py_json(
                    INSTALL_ROOT / "lib" / "terror-spiderweb.py",
                    ["json"],
                    timeout=60,
                ),
                default={"schema": "terror-spiderweb/v2", "nodes": [], "edges": [], "stats": {}},
            )
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/terror-spiderweb/gps-table":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "terror-spiderweb.py", ["gps-table"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/terror-spiderweb/registry":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "terror-spiderweb.py", ["registry"])
            self._send(200, json.dumps(payload), "application/json")
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

        if path == "/api/field/parallel":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-panel-parallel.py", ["json"], timeout=120)
            self._send(200, json.dumps(payload), "application/json")
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
                default={"schema": "field-brain/v1", "ok": False},
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
            env.setdefault("HOSTESS7_ROOT", "/home/default/Desktop/SG/Hostess7")
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
                cached = _panel_slice("h7_library", default={})
                if cached.get("_field_cache") and cached.get("books"):
                    self._send(200, json.dumps(cached), "application/json")
                    return
                profile = str(query.get("profile", [""])[0]).strip()
                args = ["build"]
                if profile:
                    args.extend(["--profile", profile])
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
                ["python3", str(script), "scour"],
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
                ["python3", str(script), "lookup", ip],
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
        elif path in ("/field", "/field/", "/app", "/app/", "/", "/index.html"):
            target = PANEL_DIR / "threat-panel.html"
        else:
            target = (PANEL_DIR / path.lstrip("/")).resolve()
            if PANEL_DIR.resolve() not in target.parents and target != PANEL_DIR.resolve():
                self._send(403, "forbidden", "text/plain")
                return
        if target.is_file():
            if target.suffix == ".html" and target.name == "threat-panel.html":
                _serve_panel_html(self, target)
            else:
                ctype = "text/html" if target.suffix == ".html" else "application/octet-stream"
                self._send(200, target.read_bytes(), ctype)
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
            env.setdefault("HOSTESS7_ROOT", "/home/default/Desktop/SG/Hostess7")
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
            acq = _nexus_update_lock([
                "acquire",
                "--holder=panel",
                "--phase=git_fetch",
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
            git_dir = _resolve_nexus_source_root()
            install_sh = (git_dir / "stealth_install.sh") if git_dir else None
            if not git_dir or not install_sh or not install_sh.is_file():
                _nexus_update_lock(["release", f"--token={token}"])
                self._send(
                    500,
                    json.dumps({
                        "ok": False,
                        "applied": False,
                        "error": "stealth_install_missing",
                        "message": "stealth_install.sh not found — set NEXUS_SHIELD_SOURCE in config/nexus.conf",
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
                    "message": f"Update started — github-update.lock held · {previous} → {target}",
                    "previous": previous,
                    "latest": target,
                    "source_root": str(git_dir),
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
            install_sh = (git_dir / "stealth_install.sh") if git_dir else None
            token = str(lock.get("token") or os.environ.get("NEXUS_UPDATE_LOCK_TOKEN", ""))
            previous = str(lock.get("previous_version") or needs.get("previous") if needs else "")
            target = str(lock.get("target_version") or needs.get("target") if needs else "")
            if not git_dir or not install_sh or not install_sh.is_file():
                self._send(
                    500,
                    json.dumps({"ok": False, "error": "stealth_install_missing"}),
                    "application/json",
                )
                return
            env = os.environ.copy()
            env.update({
                "NEXUS_INSTALL_ROOT": str(INSTALL_ROOT),
                "NEXUS_STATE_DIR": str(STATE_DIR),
                "NEXUS_UPDATE_LOCK_TOKEN": token,
                "NEXUS_UPDATE_GIT_DIR": str(git_dir),
                "NEXUS_UPDATE_TARGET": target,
                "NEXUS_UPDATE_PREVIOUS": previous,
                "NEXUS_UPDATE_INSTALL_SH": str(install_sh),
            })
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

        if path == "/api/field/parallel":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-panel-parallel.py", ["json"], timeout=120)
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

        if path == "/api/hostess7-command":
            script = INSTALL_ROOT / "lib" / "hostess7-command.py"
            if not script.is_file():
                self._send(500, json.dumps({"ok": False, "error": "script_missing"}), "application/json")
                return
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            env.setdefault("HOSTESS7_ROOT", "/home/default/Desktop/SG/Hostess7")
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
    tls_cert, tls_key = _resolve_tls_paths()
    os.chdir(PANEL_DIR)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    if USE_TLS:
        if not tls_cert or not tls_key:
            sys.stderr.write(
                "FATAL: NEXUS_PANEL_TLS=1 but nexus-panel.crt/key not found "
                f"(searched STATE={STATE_DIR}, INSTALL={INSTALL_ROOT})\n"
            )
            raise SystemExit(2)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(str(tls_cert), str(tls_key))
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
        sys.stderr.write(f"NEXUS panel TLS on 127.0.0.1:{PORT} cert={tls_cert}\n")
    else:
        sys.stderr.write(f"NEXUS panel HTTP (no TLS) on 127.0.0.1:{PORT}\n")
    server.serve_forever()


if __name__ == "__main__":
    main()
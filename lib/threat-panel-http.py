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
PANEL_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("panel")
STATUS_JSON = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("threat-panel.json")
STATE_DIR = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL_ROOT = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
TLS_CERT = Path(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] else None
TLS_KEY = Path(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5] else None
if not TLS_CERT or not TLS_KEY:
    TLS_CERT = STATE_DIR / "tls" / "nexus-panel.crt"
    TLS_KEY = STATE_DIR / "tls" / "nexus-panel.key"
USE_TLS = os.environ.get("NEXUS_PANEL_TLS", "1") == "1"

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


def _run_nexus_bash(inner: str, timeout: int = 30) -> bool:
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
    return proc.returncode == 0


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


def _nexus_py_json(script: Path, args: list[str], timeout: int = 25) -> dict:
    if not script.is_file():
        return {"ok": False, "error": "script_missing"}
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
    env["NEXUS_STATE_DIR"] = str(STATE_DIR)
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
    return _run_nexus_bash(inner, timeout=15)


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
    return _run_nexus_bash(inner, timeout=45)


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
    return _run_nexus_bash(inner, timeout=180)


def _run_nexus_adblock_apply() -> bool:
    script = INSTALL_ROOT / "lib" / "adblock-loader.sh"
    if not script.is_file():
        return False
    inner = _nexus_shell_prelude() + "nexus_adblock_apply"
    return _run_nexus_bash(inner, timeout=120)


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

    def _send(self, code, body, ctype):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
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

        if path in ("/api/status", "/api/threat-panel.json"):
            if STATUS_JSON.is_file():
                self._send(200, STATUS_JSON.read_text(encoding="utf-8"), "application/json")
            else:
                self._send(200, "{}", "application/json")
            return

        if path in ("/api/update/check", "/api/update/status"):
            force = str(query.get("force", ["0"])[0]).strip() in ("1", "true", "yes")
            payload = _nexus_update_check(force=force)
            lock = _nexus_update_lock(["status"])
            payload["update_lock"] = lock
            payload["update_in_progress"] = bool(lock.get("locked"))
            if lock.get("locked"):
                payload["update_available"] = False
                payload["message"] = lock.get("message") or "Update in progress"
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

        if path == "/api/operator/location":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "operator-location.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/honorability":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "browser-awareness.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-rf":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-rf-sentinel.py", ["json"])
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
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "terror-spiderweb.py", ["json"])
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
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "precision-field.py", ["json"])
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
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "audio-train.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/pet-signal-guard":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "pet-signal-guard.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/home-protector":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "home-protector.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/signals-field":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "signals-field.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/field-dns":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-dns.py", ["json"])
            self._send(200, json.dumps(payload), "application/json")
            return

        if path == "/api/hostess-profile":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "hostess-profile.py", ["json"])
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
                "version": "7.4.0",
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
            if STATUS_JSON.is_file():
                self._send(200, STATUS_JSON.read_text(encoding="utf-8"), "application/json")
            else:
                self._send(200, '{"field":true,"panel_ready":false,"gatekeeper":{"connections":[]}}', "application/json")
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
                payload = _lib_json(["build"], timeout=90)
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
                payload = _lib_json(["dewey"], timeout=90)
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

        if path in ("/field", "/field/", "/app", "/app/", "/", "/index.html"):
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
            install_sh = INSTALL_ROOT.parent / "stealth_install.sh"
            if not install_sh.is_file():
                for candidate in (
                    Path("/home/default/Desktop/SG/Latest/NEXUS-Shield/stealth_install.sh"),
                    INSTALL_ROOT / "stealth_install.sh",
                ):
                    if candidate.is_file():
                        install_sh = candidate
                        break
            git_dir = install_sh.parent if install_sh.is_file() else None
            applied = False
            detail = ""
            try:
                _nexus_update_lock(["phase", "git_fetch", f"--token={token}"])
                install_inner = f"export NEXUS_UPDATE_LOCK_TOKEN='{token}'; export NEXUS_UPDATE_PREVIOUS_VERSION='{previous}'; bash '{install_sh}'"
                if os.geteuid() != 0:
                    install_inner = f"export NEXUS_UPDATE_LOCK_TOKEN='{token}'; export NEXUS_UPDATE_PREVIOUS_VERSION='{previous}'; sudo -n bash '{install_sh}'"
                if git_dir and (git_dir / ".git").is_dir() and install_sh.is_file():
                    _nexus_update_lock(["phase", "git_pull", f"--token={token}"])
                    inner = (
                        f"cd '{git_dir}' && git fetch --tags origin 2>/dev/null && "
                        f"git pull --ff-only origin main 2>/dev/null && "
                        f"{install_inner}"
                    )
                    _nexus_update_lock(["phase", "stealth_install", f"--token={token}"])
                    applied = _run_nexus_bash(inner, timeout=300)
                    detail = "git_pull_stealth_install"
                elif install_sh.is_file():
                    _nexus_update_lock(["phase", "stealth_install", f"--token={token}"])
                    applied = _run_nexus_bash(install_inner, timeout=300)
                    detail = "stealth_install_only"
            finally:
                _nexus_update_lock(["release", f"--token={token}"])
            payload = {
                "ok": True,
                "applied": applied,
                "reload_panel": applied,
                "detail": detail,
                "release_url": upd.get("release_url"),
                "previous": previous,
                "latest": target,
            }
            self._send(200, json.dumps(payload), "application/json")
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

        if path == "/api/field-dns":
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "field-dns.py", ["build"])
            self._send(200, json.dumps(payload), "application/json")
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
            payload = _nexus_py_json(INSTALL_ROOT / "lib" / "terror-spiderweb.py", ["build"])
            self._send(200, json.dumps(payload), "application/json")
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
            ok = _run_nexus_bash(
                f"source {INSTALL_ROOT}/lib/nexus-settings.sh && "
                f"source {kit} && nexus_field_attack_sync_from_memory && nexus_field_attack_apply_registry",
                timeout=60,
            )
            self._send(200 if ok else 500, json.dumps({"ok": ok}), "application/json")
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
            ok = _run_nexus_bash(inner, timeout=120)
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
            ok = _run_nexus_bash(inner, timeout=30)
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
            ok = _run_nexus_bash(inner, timeout=45)
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
    if USE_TLS and TLS_CERT and TLS_KEY and TLS_CERT.is_file() and TLS_KEY.is_file():
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(str(TLS_CERT), str(TLS_KEY))
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
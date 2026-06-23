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
    "arp-snapshot": STATE_DIR / "arp.snapshot",
    "firewall-state": STATE_DIR / "firewall.state",
    "firewall-trusted": STATE_DIR / "firewall-trusted.tsv",
    "vigil-state": STATE_DIR / "vigil.state",
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

        if path in ("/", "/index.html"):
            target = PANEL_DIR / "threat-panel.html"
        else:
            target = (PANEL_DIR / path.lstrip("/")).resolve()
            if PANEL_DIR.resolve() not in target.parents and target != PANEL_DIR.resolve():
                self._send(403, "forbidden", "text/plain")
                return
        if target.is_file():
            ctype = "text/html" if target.suffix == ".html" else "application/octet-stream"
            self._send(200, target.read_bytes(), ctype)
            return
        self._send(404, "not found", "text/plain")

    def do_POST(self):
        path = unquote(self.path.split("?", 1)[0])
        if self.headers.get("Content-Length"):
            try:
                length = int(self.headers.get("Content-Length", 0))
            except ValueError:
                length = 0
            if length > 65536:
                self._send(413, "payload too large", "text/plain")
                return
        body = self._read_json_body()

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
            if not ip:
                self._send(400, json.dumps({"ok": False, "error": "missing ip"}), "application/json")
                return
            script = INSTALL_ROOT / "lib" / "firewall-sentinel.sh"
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL_ROOT)
            env["NEXUS_STATE_DIR"] = str(STATE_DIR)
            safe_ip = ip.replace("'", "'\"'\"'")
            cmd = (
                f"source {INSTALL_ROOT}/lib/nexus-common.sh && nexus_load_config && "
                f"source {script} && "
                f"nexus_firewall_block_ip {direction} '{safe_ip}' 86400 '{reason}'"
            )
            proc = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=20, env=env)
            ok = proc.returncode == 0
            self._send(200 if ok else 500, json.dumps({"ok": ok, "ip": ip}), "application/json")
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
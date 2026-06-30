#!/usr/bin/env python3
"""Serve Grok16 speed comparison dashboard + live JSON API."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HTML = Path(__file__).resolve().parent / "speed-dashboard.html"
EXEC_MODE = os.environ.get("SPEED_DEMO_MODE", "").strip().lower() == "exec"
LIVE = (
    ROOT / "data" / "bench" / "exec-plane" / "field-exec-live.json"
    if EXEC_MODE
    else ROOT / "data" / "bench" / "speed-demo-live.json"
)
RESULT = (
    ROOT / "data" / "bench" / "exec-plane" / "field-exec-result.json"
    if EXEC_MODE
    else ROOT / "data" / "bench" / "speed-demo-result.json"
)
RUN_SCRIPT = (
    ROOT / "scripts" / "field-exec-compare.py"
    if EXEC_MODE
    else ROOT / "scripts" / "speed-demo-run.py"
)
PORT = int(os.environ.get("SPEED_DASHBOARD_PORT", "9416"))


class Handler(BaseHTTPRequestHandler):
    server_version = "Grok16SpeedDashboard/2.0"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send(200, HTML.read_bytes(), "text/html; charset=utf-8")
            return
        if path == "/api/live":
            if LIVE.is_file():
                self._send(200, LIVE.read_bytes(), "application/json")
            else:
                self._send(200, b'{"phase":"idle","cases":{}}', "application/json")
            return
        if path == "/api/result":
            if RESULT.is_file():
                self._send(200, RESULT.read_bytes(), "application/json")
            else:
                self._send(404, b'{"error":"no result"}', "application/json")
            return
        self._send(404, b"not found", "text/plain")

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/run":
            self._send(404, b"not found", "text/plain")
            return
        if getattr(self.server, "run_lock", False):
            self._send(409, b'{"error":"run in progress"}', "application/json")
            return
        self.server.run_lock = True

        def _run() -> None:
            try:
                env = {**os.environ, "GROK16_ROOT": str(ROOT), "G16_PREFIX": os.environ.get("G16_PREFIX", str(ROOT))}
                subprocess.run(
                    [sys.executable, str(RUN_SCRIPT)],
                    cwd=str(ROOT),
                    env=env,
                    check=False,
                )
            finally:
                self.server.run_lock = False

        threading.Thread(target=_run, daemon=True).start()
        self._send(202, b'{"ok":true,"message":"benchmark started"}', "application/json")


def main() -> int:
    os.chdir(ROOT)
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    httpd.run_lock = False
    print(f"Grok16 speed dashboard → http://127.0.0.1:{PORT}/")
    print(f"Live JSON → http://127.0.0.1:{PORT}/api/live")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
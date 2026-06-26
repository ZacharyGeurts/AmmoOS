#!/usr/bin/env pythong
"""F9 underlay hotkey — opens 2026 Tristate Installer (NEXUS-owned, not xbindkeys)."""
from __future__ import annotations

import glob
import json
import os
import select
import struct
import subprocess
import sys
import time
from pathlib import Path

EV_KEY = 0x01
KEY_F9 = 67  # F1=59 … F12=70 — F9 normally unused (F11=Queen FS, F8=RTX FS)
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
SWITCH_PY = INSTALL / "lib" / "field-underlay-switch.py"
DEBOUNCE_SEC = 1.2


def _open_installer() -> None:
    port = os.environ.get("NEXUS_THREAT_PANEL_PORT", "9477")
    url = f"http://127.0.0.1:{port}/field"
    if SWITCH_PY.is_file():
        subprocess.run(
            [sys.executable, str(SWITCH_PY), "hotkey"],
            env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL)},
            timeout=30,
            check=False,
        )
    for opener in ("xdg-open", "gio", "sensible-browser"):
        if subprocess.run(["which", opener], capture_output=True).returncode == 0:
            subprocess.Popen(
                [opener, url],
                env={**os.environ, "DISPLAY": os.environ.get("DISPLAY", ":0")},
            )
            return


def _keyboard_fds() -> dict[int, str]:
    fds: dict[int, str] = {}
    for path in sorted(glob.glob("/dev/input/event*")):
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
            fds[fd] = path
        except OSError:
            continue
    return fds


def listen_loop() -> None:
    last = 0.0
    while True:
        fds = _keyboard_fds()
        if not fds:
            time.sleep(5)
            continue
        try:
            readable, _, _ = select.select(list(fds.keys()), [], [], 2.0)
        except (ValueError, OSError):
            time.sleep(2)
            continue
        for fd in readable:
            try:
                data = os.read(fd, 24)
            except OSError:
                continue
            if len(data) < 24:
                continue
            _sec, _usec, ev_type, code, value = struct.unpack("llHHI", data)
            if ev_type == EV_KEY and code == KEY_F9 and value == 1:
                now = time.monotonic()
                if now - last < DEBOUNCE_SEC:
                    continue
                last = now
                _open_installer()


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        _open_installer()
        return 0
    if os.environ.get("NEXUS_UNDERLAY_HOTKEY") == "0":
        return 0
    try:
        listen_loop()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
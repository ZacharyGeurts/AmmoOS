#!/usr/bin/env pythong
"""Open Queen sovereign browser — self-contained shell, no OS wmctrl/xdotool hooks."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
SG = Path(os.environ.get("SG_ROOT", INSTALL.parent.parent))


def _resolve_queen_root() -> Path:
    env = os.environ.get("QUEEN_ROOT", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p.resolve()
    for candidate in (
        INSTALL / "Queen",
        SG / "Queen",
        SG / "NewLatest" / "Queen",
        Path("/home/default/Desktop/SG/NewLatest/Queen"),
    ):
        if candidate.is_dir() and (candidate / "world").is_dir():
            return candidate.resolve()
    return (INSTALL / "Queen").resolve()


def _load_panel_open() -> Any:
    py = INSTALL / "lib" / "queen-panel-open.py"
    spec = importlib.util.spec_from_file_location("queen_panel_open", py)
    if not spec or not spec.loader:
        raise ImportError("queen-panel-open.py missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def open_sovereign_browser(*, route: str = "", focus_url: str = "") -> dict[str, Any]:
    """F9 target — Queen world + Webbrowser shell; CHIPS/cores via web (no RTX comp shader)."""
    queen = _resolve_queen_root()
    port = int(os.environ.get("QUEEN_WORLD_PORT", "9481"))
    panel_port = int(os.environ.get("NEXUS_THREAT_PANEL_PORT", "9477"))
    c2_url = f"http://127.0.0.1:{panel_port}/field"
    c2_launch = os.environ.get("NEXUS_C2_DESKTOP_LAUNCH", "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )
    shell_url = os.environ.get("QUEEN_BROWSER_URL", "").strip() or (
        c2_url if c2_launch else f"http://127.0.0.1:{port}/world/browser.html"
    )
    env = {
        **os.environ,
        "NEXUS_INSTALL_ROOT": str(INSTALL),
        "NEXUS_STATE_DIR": str(STATE),
        "SG_ROOT": str(SG),
        "QUEEN_ROOT": str(queen),
        "QUEEN_SOVEREIGN": "1",
        "NEXUS_QUEEN_SOVEREIGN": "1",
        "QUEEN_INTERNAL_ONLY": "1",
        "QUEEN_INSTANT_BROWSER": "1",
        "QUEEN_WEB_SHELL": "1",
        "QUEEN_SKIP_RTX_BOOT": "1",
        "NEXUS_EMBED_PANEL_IN_ENGINE": "0",
        "NEXUS_FIELD_BROWSER_QUEEN": "1",
        "NEXUS_C2_DESKTOP_LAUNCH": os.environ.get("NEXUS_C2_DESKTOP_LAUNCH", "1"),
        "NEXUS_C2_KIOSK": os.environ.get("NEXUS_C2_KIOSK", "1"),
        "NEXUS_C2_LAUNCH_URL": os.environ.get("NEXUS_C2_LAUNCH_URL", c2_url),
        "QUEEN_BROWSER_URL": shell_url,
        "QUEEN_BROWSER_START": os.environ.get("QUEEN_BROWSER_START", c2_url),
        "QUEEN_BROWSER_HOME": os.environ.get("QUEEN_BROWSER_HOME", c2_url),
        "QUEEN_NO_OS_BROWSER": os.environ.get("QUEEN_NO_OS_BROWSER", "1"),
    }
    opener = _load_panel_open()
    world = opener.ensure_queen_world()
    if not world.get("ok"):
        start = queen / "scripts" / "start-world.sh"
        if start.is_file():
            subprocess.run(
                [str(start), "--daemon"],
                cwd=str(queen),
                env=env,
                capture_output=True,
                text=True,
                timeout=25,
                check=False,
            )
            world = opener.ensure_queen_world()
    panel_url = focus_url.strip()
    if not panel_url and route:
        panel_url = opener._panel_field_url(route)  # noqa: SLF001
    if not panel_url:
        panel_url = env.get("QUEEN_BROWSER_START", "").strip() or opener._panel_field_url()  # noqa: SLF001
    integrated_py = INSTALL / "lib" / "queen-integrated-browser.py"
    if integrated_py.is_file():
        try:
            proc = subprocess.run(
                [sys.executable, str(integrated_py), "open"],
                env=env,
                capture_output=True,
                text=True,
                timeout=50,
                check=False,
            )
            display = json.loads(proc.stdout or "{}") if (proc.stdout or "").strip().startswith("{") else {}
        except (subprocess.SubprocessError, json.JSONDecodeError):
            display = opener.launch_queen_display()
    else:
        display = opener.launch_queen_display()
    tab = opener.open_in_queen_tab(panel_url, new_tab=True) if panel_url else None
    return {
        "ok": bool(world.get("ok") or display.get("ok")),
        "engine": "queen-browser",
        "self_contained": True,
        "shell_url": shell_url,
        "world": world,
        "display": display,
        "tab": tab,
        "queen_root": str(queen),
    }


def f9_action() -> dict[str, Any]:
    drop_in_py = INSTALL / "lib" / "field-drop-in-orchestrator.py"
    ready = False
    if drop_in_py.is_file():
        try:
            proc = subprocess.run(
                [sys.executable, str(drop_in_py), "f9-ready"],
                capture_output=True,
                text=True,
                timeout=20,
                env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL), "NEXUS_STATE_DIR": str(STATE)},
            )
            doc = json.loads(proc.stdout or "{}")
            ready = bool(doc.get("ready"))
        except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
            pass
    lock = STATE / "field-underlay-lock.json"
    if lock.is_file():
        try:
            committed = json.loads(lock.read_text(encoding="utf-8")).get("committed")
            ready = ready or bool(committed)
        except (OSError, json.JSONDecodeError):
            pass
    if ready:
        out = open_sovereign_browser()
        out["action"] = "queen_sovereign_browser"
        return out
    switch = INSTALL / "lib" / "field-underlay-switch.py"
    if switch.is_file():
        subprocess.run(
            [sys.executable, str(switch), "hotkey"],
            env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL), "NEXUS_STATE_DIR": str(STATE)},
            timeout=30,
            check=False,
        )
    opener_py = INSTALL / "lib" / "queen-panel-open.py"
    if opener_py.is_file():
        subprocess.run(
            [sys.executable, str(opener_py), "nexus", "tristate-installer"],
            env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL)},
            timeout=25,
            check=False,
        )
    return {
        "ok": True,
        "action": "tristate_installer",
        "ready": False,
        "url": "/tristate-installer",
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "open").strip().lower()
    if cmd in ("f9", "hotkey"):
        out = f9_action()
    elif cmd == "open":
        route = sys.argv[2] if len(sys.argv) > 2 else ""
        out = open_sovereign_browser(route=route)
    else:
        print(json.dumps({"error": "usage: field-queen-browser-open.py [open [route]|f9|hotkey]"}))
        return 1
    print(json.dumps(out, ensure_ascii=False))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
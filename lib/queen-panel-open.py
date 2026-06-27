#!/usr/bin/env pythong
"""Open NEXUS / field URLs inside Queen browser tabs — no OS browser fallback."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))


def _resolve_queen_root() -> Path:
    env = os.environ.get("QUEEN_ROOT", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p.resolve()
    for candidate in (
        INSTALL / "Queen",
        INSTALL.parent / "Queen",
        Path(os.environ.get("SG_ROOT", str(INSTALL.parent))) / "Queen",
        Path(os.environ.get("SG_ROOT", str(INSTALL.parent))) / "NewLatest" / "Queen",
        Path("/home/default/Desktop/SG/Queen"),
        Path("/home/default/Desktop/SG/NewLatest/Queen"),
    ):
        if candidate.is_dir() and ((candidate / "world").is_dir() or (candidate / "lib").is_dir()):
            return candidate.resolve()
    return (INSTALL / "Queen").resolve()


QUEEN = _resolve_queen_root()
WORLD_PORT = int(os.environ.get("QUEEN_WORLD_PORT", "9481"))
PANEL_PORT = int(os.environ.get("NEXUS_THREAT_PANEL_PORT", "9477"))


def _world_base() -> str:
    return f"http://127.0.0.1:{WORLD_PORT}"


def _browser_shell_url() -> str:
    custom = os.environ.get("QUEEN_BROWSER_URL", "").strip()
    if custom:
        return custom
    return f"{_world_base()}/world/browser.html"


def _panel_field_url(route: str = "") -> str:
    base = f"http://127.0.0.1:{PANEL_PORT}/field"
    route = (route or "").strip().lstrip("#")
    return f"{base}#{route}" if route else base


def _http_json(method: str, url: str, body: dict[str, Any] | None = None, *, timeout: float = 8.0) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw.strip().startswith("{") else {"ok": True, "raw": raw[:200]}
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read().decode("utf-8", errors="replace")
            doc = json.loads(raw) if raw.strip().startswith("{") else {}
        except (OSError, json.JSONDecodeError):
            doc = {}
        doc.setdefault("ok", False)
        doc.setdefault("http_status", exc.code)
        return doc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return {"ok": False, "error": str(exc)}


def ensure_queen_world() -> dict[str, Any]:
    st = _http_json("GET", f"{_world_base()}/api/status?fast=1", timeout=2.0)
    if st.get("ok") is not False and (st.get("schema") or st.get("port") or st.get("queen_verdict")):
        return {"ok": True, "already": True, "world": _world_base()}
    script = QUEEN / "scripts" / "start-world.sh"
    if script.is_file():
        try:
            subprocess.run(
                [str(script), "--daemon"],
                cwd=str(QUEEN),
                env={**os.environ, "QUEEN_ROOT": str(QUEEN), "NEXUS_INSTALL_ROOT": str(INSTALL)},
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
    for _ in range(12):
        st = _http_json("GET", f"{_world_base()}/api/status?fast=1", timeout=2.0)
        if st.get("ok") is not False and (st.get("schema") or st.get("port") or st.get("queen_verdict")):
            return {"ok": True, "spawned": True, "world": _world_base()}
    return {"ok": False, "error": "queen_world_unavailable", "world": _world_base()}


def open_in_queen_tab(url: str, *, new_tab: bool = True, tab_id: str = "") -> dict[str, Any]:
    url = (url or "").strip()
    if not url:
        return {"ok": False, "error": "url_required"}
    world = ensure_queen_world()
    if not world.get("ok"):
        return world
    jump = _http_json(
        "POST",
        f"{_world_base()}/api/nexus-jump",
        {"action": "jump", "url": url, "tab_id": tab_id, "proc": "queen-browser"},
        timeout=12.0,
    )
    if jump.get("permit") is False or jump.get("ok") is False:
        return {**jump, "ok": False, "phase": "nexus_jump"}
    action = "new_tab" if new_tab else "navigate"
    nav = _http_json(
        "POST",
        f"{_world_base()}/api/queen-browser",
        {"action": action, "url": url, "tab_id": tab_id},
        timeout=12.0,
    )
    return {
        "ok": nav.get("ok") is not False,
        "engine": "queen-browser",
        "world": _world_base(),
        "url": url,
        "tab": nav.get("tab") or nav.get("tabs", [{}])[0] if isinstance(nav.get("tabs"), list) else nav.get("tab"),
        "jump_verdict": jump.get("verdict"),
        "nav": nav,
    }


def launch_queen_display(*, focus_url: str = "") -> dict[str, Any]:
    """RTX queen-browser opens NEXUS directly; web fallback is browser-only shell (not Queen OS world)."""
    panel_url = (focus_url or _panel_field_url()).strip()
    browser_shell = _browser_shell_url()
    candidates = [
        QUEEN / "build" / "rtx" / "bin" / "Linux" / "queen-browser",
        QUEEN / "build" / "queen-browser",
    ]
    env = {
        **os.environ,
        "QUEEN_ROOT": str(QUEEN),
        "NEXUS_INSTALL_ROOT": str(INSTALL),
        "NEXUS_EMBED_PANEL_IN_ENGINE": "0",
        "QUEEN_INSTANT_BROWSER": "1",
        "QUEEN_BROWSER_URL": browser_shell,
    }
    for binary in candidates:
        if not binary.is_file() or not os.access(binary, os.X_OK):
            continue
        try:
            subprocess.Popen(
                [
                    str(binary),
                    "--sovereign",
                    "--queen",
                    "--extended-field",
                    f"--url={panel_url}",
                ],
                env=env,
                cwd=str(QUEEN),
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return {
                "ok": True,
                "binary": str(binary),
                "url": panel_url,
                "shell_url": browser_shell,
                "display": "queen-browser-rtx",
            }
        except OSError as exc:
            return {"ok": False, "error": str(exc), "binary": str(binary)}
    return {
        "ok": True,
        "display": "queen_browser_shell",
        "url": browser_shell,
        "panel_url": panel_url,
        "hint": "Queen browser shell — NEXUS tab already queued (not Queen OS world)",
    }


def open_nexus_panel(*, route: str = "", new_tab: bool = True, launch_display: bool = True) -> dict[str, Any]:
    url = _panel_field_url(route)
    tab = open_in_queen_tab(url, new_tab=new_tab)
    out = {"ok": tab.get("ok"), "nexus_url": url, "tab": tab}
    if launch_display:
        out["display"] = launch_queen_display(focus_url=url)
    return out


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "nexus").strip().lower()
    if cmd in ("nexus", "field", "panel"):
        route = sys.argv[2] if len(sys.argv) > 2 else ""
        out = open_nexus_panel(route=route)
        print(json.dumps(out, ensure_ascii=False))
        return 0 if out.get("ok") else 1
    if cmd == "url" and len(sys.argv) > 2:
        out = open_in_queen_tab(" ".join(sys.argv[2:]))
        print(json.dumps(out, ensure_ascii=False))
        return 0 if out.get("ok") else 1
    if cmd == "ensure":
        print(json.dumps(ensure_queen_world(), ensure_ascii=False))
        return 0
    print(json.dumps({
        "error": "usage: queen-panel-open.py [nexus [route]|url URL|ensure]",
    }, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
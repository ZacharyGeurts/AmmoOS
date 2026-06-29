#!/usr/bin/env pythong
"""Queen classic desktop — first tab surface, SDF icons, wallpaper support, host mirror."""
from __future__ import annotations

import importlib.util
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

QUEEN = Path(__file__).resolve().parents[1]
SG = QUEEN.parent.parent
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", SG / "NewLatest"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", QUEEN / ".nexus-state"))
DESKTOP_STATE = STATE / "queen-desktop.json"

CLASSIC_PROGRAMS = [
    {"id": "kilroy", "name": "KILROY", "kind": "program", "url": "/world/?dock=kilroy", "category": "System"},
    {"id": "files", "name": "Files", "kind": "folder", "url": "/world/queen-files.html", "category": "System"},
    {"id": "browser", "name": "Queen Browser", "kind": "program", "url": "/world/browser.html", "category": "System"},
    {"id": "nexus-c2", "name": "AmmoOS C2", "kind": "program", "url": "/world/queen-nexus-c2.html", "category": "System", "panel_thumbnail": True, "icon": "ammoos-field"},
    {"id": "dashboard", "name": "AmmoOS C2", "kind": "program", "url": "/world/queen-nexus-c2.html", "category": "System", "panel_thumbnail": True, "legacy_id": "dashboard", "icon": "ammoos-field"},
    {"id": "ammoos-image", "name": "AmmoOS Image", "kind": "program", "url": "queen://field-gimp", "category": "AmmoOS"},
    {"id": "terminal", "name": "Terminal", "kind": "program", "url": "queen://terminal", "category": "System"},
    {"id": "code", "name": "Code", "kind": "program", "url": "/world/queen-code.html", "category": "Programs"},
    {"id": "chips", "name": "CHIPS", "kind": "program", "url": "queen://chips", "category": "Programs"},
    {"id": "cores", "name": "Cores", "kind": "program", "url": "queen://cores", "category": "Programs"},
    {"id": "gameroom", "name": "Game Room", "kind": "program", "url": "queen://gameroom", "category": "Programs"},
    {"id": "forge", "name": "Forge", "kind": "program", "url": "/gui/queen-build-deck.html", "category": "Programs"},
    {"id": "hostess", "name": "Hostess 7", "kind": "program", "url": "queen://hostess", "category": "Programs"},
    {"id": "eyeball", "name": "Final_Eye", "kind": "program", "url": "queen://eyeball", "category": "Programs"},
    {"id": "earball", "name": "Final Ear", "kind": "program", "url": "queen://earball", "category": "Programs"},

    {"id": "g16", "name": "Grok16", "kind": "program", "url": "queen://g16", "category": "Programs"},
    {"id": "gpy", "name": "GPY-16", "kind": "program", "url": "queen://grokpy", "category": "Programs"},
    {"id": "field", "name": "Field Tech", "kind": "folder", "url": "/world/?embed=1&dock=field", "category": "Programs"},
    {"id": "ammoos", "name": "AmmoOS", "kind": "program", "url": "queen://nexus", "category": "Field", "icon": "ammoos-field", "legacy_id": "nexus"},
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _save(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _world_base() -> str:
    port = os.environ.get("QUEEN_WORLD_PORT", "9481")
    return f"http://127.0.0.1:{port}"


def _boot_hook_mod() -> Any:
    script = QUEEN / "lib" / "queen-boot-hook.py"
    if not script.is_file():
        return None
    spec = importlib.util.spec_from_file_location("queen_boot_hook", script)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _panel_alive(port: int = 9477) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.4):
            return True
    except OSError:
        return False


def _fetch_host_desktop() -> dict[str, Any]:
    script = INSTALL / "lib" / "field-host-desktop.py"
    if script.is_file():
        try:
            proc = subprocess.run(
                [sys.executable, str(script), "json"],
                capture_output=True,
                text=True,
                timeout=45,
                cwd=str(INSTALL),
                env={
                    **os.environ,
                    "NEXUS_INSTALL_ROOT": str(INSTALL),
                    "NEXUS_STATE_DIR": str(STATE),
                },
            )
            return json.loads(proc.stdout or "{}")
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
            pass
    if _panel_alive():
        try:
            port = os.environ.get("NEXUS_THREAT_PANEL_PORT", "9477")
            import urllib.request

            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/field-host-desktop", timeout=5) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            pass
    return {}


def _normalize_url(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return _world_base() + "/world/browser.html"
    if u.startswith("/"):
        return _world_base() + u
    return u


def _default_pinned() -> set[str]:
    return {"kilroy", "files", "browser", "terminal", "code"}


def _pinned_ids() -> set[str]:
    doc = _load(DESKTOP_STATE, {})
    stored = doc.get("pinned_programs")
    if isinstance(stored, list) and stored:
        return {str(x) for x in stored}
    return _default_pinned()


def _classic_icons() -> list[dict[str, Any]]:
    pinned = _pinned_ids()
    out = []
    for p in CLASSIC_PROGRAMS:
        out.append({
            **p,
            "icon": f"prog-{p['id']}-48",
            "sdf_kind": p.get("kind") or "program",
            "pinned": p["id"] in pinned,
            "url": _normalize_url(p.get("url") or ""),
        })
    return out


def _desktop_icons_in_start(host_doc: dict[str, Any]) -> bool:
    policy = host_doc.get("policy") or {}
    if "desktop_icons_in_start" in policy:
        return bool(policy.get("desktop_icons_in_start"))
    return policy.get("show_desktop_icons") is False


def _host_programs(host_doc: dict[str, Any]) -> list[dict[str, Any]]:
    """Host OS mirror disabled — AmmoOS C2 desktop is the only program surface."""
    return []


def _host_programs_legacy(host_doc: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for app in host_doc.get("programs") or []:
        exec_line = app.get("exec") or app.get("url") or ""
        url = exec_line
        if exec_line.startswith("/"):
            port = os.environ.get("NEXUS_THREAT_PANEL_PORT", "9477")
            url = f"http://127.0.0.1:{port}{exec_line}"
        elif exec_line and not exec_line.startswith("http") and not exec_line.startswith("queen://"):
            url = f"queen://launch?exec={exec_line}"
        out.append({
            "id": app.get("id") or app.get("name", ""),
            "name": app.get("name") or "Program",
            "kind": "host",
            "url": url,
            "icon_url": app.get("icon_url"),
            "category": app.get("category") or "Host",
            "source": app.get("source") or "host",
            "exec": exec_line,
            "secured": True,
        })
    return out


def _desktop_prefs() -> dict[str, Any]:
    doc = _load(DESKTOP_STATE, {})
    return {
        "wallpaper": doc.get("wallpaper") or "",
        "wallpaper_fit": doc.get("wallpaper_fit") or "stretch",
        "icon_columns": int(doc.get("icon_columns") or 1),
        "theme": doc.get("theme") or "classic_win95",
    }


def desktop_posture() -> dict[str, Any]:
    hook = _boot_hook_mod()
    boot_hook = hook.posture() if hook else {}
    host_doc = _fetch_host_desktop()
    prefs = _desktop_prefs()
    boot_os = boot_hook.get("boot_os") if hook else False
    if hook and hasattr(hook, "is_boot_os"):
        boot_os = hook.is_boot_os()

    classic = _classic_icons()
    icons_in_start = _desktop_icons_in_start(host_doc)
    return {
        "schema": "queen-desktop/v1",
        "ts": _now(),
        "ok": True,
        "layout": "classic_win95",
        "boot_os": bool(boot_os),
        "start_button": "classic",
        "wallpaper": prefs["wallpaper"],
        "wallpaper_fit": prefs["wallpaper_fit"],
        "icon_columns": prefs["icon_columns"],
        "theme": prefs["theme"],
        "desktop_icons_in_start": icons_in_start,
        "classic_programs": [] if icons_in_start else classic,
        "start_programs": classic if icons_in_start else [],
        "host_programs": _host_programs(host_doc),
        "host_theme": host_doc.get("theme") or "gnome",
        "host_menu": host_doc.get("menu") or {},
        "host_os": host_doc.get("guest_os") or {},
        "network_metal": boot_hook.get("network_metal") or {},
        "boot_hook": {
            "boarded": boot_hook.get("boarded"),
            "front_hook": boot_hook.get("front_hook"),
        },
        "taskbar": {
            "position": "bottom",
            "height": 28,
            "show_clock": True,
            "show_tasks": True,
        },
        "posture": "Queen classic desktop — program icons live in Start folders; Queen Browser is the web engine",
    }


def dispatch(body: dict[str, Any]) -> dict[str, Any]:
    action = str(body.get("action") or "status").strip().lower().replace("-", "_")
    if action in ("status", "json", "posture"):
        return {"ok": True, **desktop_posture()}

    if action == "set_wallpaper":
        doc = _load(DESKTOP_STATE, {"schema": "queen-desktop-prefs/v1"})
        wp = str(body.get("wallpaper") or "").strip()
        if wp and not (wp.startswith("/") or wp.startswith("http") or wp.startswith("data:")):
            return {"ok": False, "error": "invalid_wallpaper"}
        doc["wallpaper"] = wp
        doc["wallpaper_fit"] = str(body.get("wallpaper_fit") or doc.get("wallpaper_fit") or "stretch")
        doc["updated"] = _now()
        _save(DESKTOP_STATE, doc)
        return {"ok": True, **desktop_posture()}

    if action in ("toggle_pin", "set_pin", "pin_program"):
        doc = _load(DESKTOP_STATE, {"schema": "queen-desktop-prefs/v1"})
        prog_id = str(body.get("program_id") or body.get("id") or "").strip()
        if not prog_id:
            return {"ok": False, "error": "program_id_required"}
        valid = {p["id"] for p in CLASSIC_PROGRAMS}
        if prog_id not in valid:
            return {"ok": False, "error": "unknown_program", "program_id": prog_id}
        pins = list(_pinned_ids())
        want = body.get("pinned")
        if want is None:
            want = prog_id not in pins
        if want:
            if prog_id not in pins:
                pins.append(prog_id)
        else:
            pins = [x for x in pins if x != prog_id]
        doc["pinned_programs"] = pins
        doc["updated"] = _now()
        _save(DESKTOP_STATE, doc)
        return {"ok": True, "program_id": prog_id, "pinned": bool(want), **desktop_posture()}

    return {"ok": False, "error": "unknown_action", "action": action}


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd == "json":
        print(json.dumps(desktop_posture(), ensure_ascii=False))
        return 0
    if cmd == "dispatch":
        raw = sys.stdin.read()
        body = json.loads(raw) if raw.strip() else {}
        print(json.dumps(dispatch(body), ensure_ascii=False))
        return 0
    print(json.dumps(dispatch({"action": cmd}), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
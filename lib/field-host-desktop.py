#!/usr/bin/env pythong
"""Host desktop — enumerate incumbent OS programs, mirror start menu, serve icons."""
from __future__ import annotations

import base64
import configparser
import json
import mimetypes
import os
import platform
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
DOCTRINE = INSTALL / "data" / "field-host-desktop-doctrine.json"
PANEL_FILE = STATE / "field-host-desktop.json"
STAMP = STATE / "field-host-desktop.stamp"
ICON_CACHE = STATE / "field-host-desktop-icons"

DESKTOP_SKIP = frozenset({"Hidden", "NoDisplay", "DBusActivatable"})
ICON_EXTS = (".png", ".svg", ".xpm", ".jpg", ".jpeg", ".webp")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _save_atomic(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _expand(path_text: str) -> Path:
    text = path_text.replace("HOME", str(Path.home()))
    return Path(text).expanduser()


def _guest_system() -> str:
    override = os.environ.get("NEXUS_GUEST_OS_THEME", "").strip().lower()
    if override in ("windows", "linux", "darwin", "macos"):
        return "darwin" if override == "macos" else override
    system = platform.system().lower()
    if "windows" in system:
        return "windows"
    if "darwin" in system:
        return "darwin"
    return "linux"


def _linux_de() -> str:
    for key in ("XDG_CURRENT_DESKTOP", "DESKTOP_SESSION", "XDG_SESSION_DESKTOP"):
        val = os.environ.get(key, "").lower()
        if "kde" in val or "plasma" in val:
            return "kde"
        if "gnome" in val:
            return "gnome"
        if "xfce" in val:
            return "xfce"
        if "cinnamon" in val or "mate" in val:
            return "cinnamon"
    return "gnome"


def _theme_id() -> str:
    doctrine = _load(DOCTRINE, {})
    themes = doctrine.get("themes") or {}
    guest = _guest_system()
    if guest == "windows":
        return os.environ.get("NEXUS_START_MENU_THEME", themes.get("windows", "windows11"))
    if guest == "darwin":
        return themes.get("darwin", "macos")
    de = _linux_de()
    if de == "kde":
        return "kde"
    return themes.get("linux", "gnome")


def _parse_desktop(path: Path) -> dict[str, Any] | None:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.optionxform = str  # type: ignore[method-assign]
    try:
        cfg.read_string(raw)
    except configparser.Error:
        return None
    if not cfg.has_section("Desktop Entry"):
        return None
    sec = cfg["Desktop Entry"]
    if sec.get("Type", "Application") != "Application":
        return None
    if sec.get("Hidden", "").lower() == "true":
        return None
    if sec.get("NoDisplay", "").lower() == "true":
        return None
    name = (sec.get("Name") or sec.get("GenericName") or path.stem).strip()
    if not name:
        return None
    exec_line = (sec.get("Exec") or "").strip()
    if not exec_line:
        return None
    exec_line = re.sub(r"%[fFuUdDnNickvm]", "", exec_line).strip()
    icon = (sec.get("Icon") or "").strip() or path.stem
    categories = [c.strip() for c in (sec.get("Categories") or "").split(";") if c.strip()]
    return {
        "id": f"desktop-{path.stem}",
        "name": name,
        "exec": exec_line,
        "icon": icon,
        "icon_key": f"{path.stem}:{icon}",
        "category": categories[0] if categories else "Other",
        "categories": categories,
        "source": "desktop_entry",
        "desktop_path": str(path),
        "terminal": sec.get("Terminal", "false").lower() == "true",
    }


def _icon_search_dirs() -> list[Path]:
    doctrine = _load(DOCTRINE, {})
    out: list[Path] = []
    for item in doctrine.get("icon_theme_dirs") or []:
        p = _expand(str(item))
        if p.is_dir() and p not in out:
            out.append(p)
    for extra in (
        Path("/usr/share/icons"),
        Path.home() / ".local/share/icons",
        Path("/usr/share/pixmaps"),
    ):
        if extra.is_dir() and extra not in out:
            out.append(extra)
    return out


def _resolve_icon_file(icon_name: str, desktop_path: str | None = None) -> Path | None:
    if not icon_name:
        return None
    icon_path = Path(icon_name)
    if icon_path.is_file():
        return icon_path.resolve()
    if desktop_path:
        sibling = Path(desktop_path).parent / icon_name
        for ext in ("", *ICON_EXTS):
            cand = sibling.with_suffix(ext) if ext else sibling
            if cand.is_file():
                return cand.resolve()
    name = icon_name
    if name.endswith(".png") or name.endswith(".svg"):
        name = Path(name).stem
    sizes = ("256x256", "128x128", "64x64", "48x48", "32x32", "24x24", "22x22", "16x16", "scalable")
    for base in _icon_search_dirs():
        for sz in sizes:
            for ext in ICON_EXTS:
                cand = base / sz / "apps" / f"{name}{ext}"
                if cand.is_file():
                    return cand.resolve()
        for ext in ICON_EXTS:
            cand = base / f"{name}{ext}"
            if cand.is_file():
                return cand.resolve()
    return None


def _safe_icon_path(token: str) -> Path | None:
    """Resolve cached icon token — no arbitrary filesystem reads."""
    if not token or ".." in token or "/" in token or "\\" in token:
        return None
    cand = ICON_CACHE / token
    if cand.is_file():
        return cand.resolve()
    return None


def _cache_icon(icon_key: str, src: Path) -> str | None:
    if not src.is_file():
        return None
    ICON_CACHE.mkdir(parents=True, exist_ok=True)
    ext = src.suffix.lower() if src.suffix.lower() in ICON_EXTS else ".png"
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", icon_key)[:120]
    dest = ICON_CACHE / f"{safe}{ext}"
    try:
        if not dest.is_file() or dest.stat().st_mtime < src.stat().st_mtime:
            dest.write_bytes(src.read_bytes())
        return dest.name
    except OSError:
        return None


def _scan_linux_apps() -> list[dict[str, Any]]:
    doctrine = _load(DOCTRINE, {})
    dirs: list[Path] = []
    for item in doctrine.get("linux_scan_dirs") or []:
        p = _expand(str(item))
        if p.is_dir():
            dirs.append(p)
    seen: set[str] = set()
    apps: list[dict[str, Any]] = []
    for base in dirs:
        for path in sorted(base.glob("*.desktop")):
            app = _parse_desktop(path)
            if not app:
                continue
            key = app["name"].lower()
            if key in seen:
                continue
            seen.add(key)
            resolved = _resolve_icon_file(app["icon"], app.get("desktop_path"))
            if resolved:
                token = _cache_icon(app["icon_key"], resolved)
                if token:
                    app["icon_url"] = f"/api/field-host-desktop/icon/{quote(token, safe='')}"
            apps.append(app)
    return sorted(apps, key=lambda x: x["name"].lower())


def _field_apps() -> list[dict[str, Any]]:
    doctrine = _load(DOCTRINE, {})
    out: list[dict[str, Any]] = []
    for row in doctrine.get("field_apps") or []:
        app = dict(row)
        app.setdefault("source", "field")
        app.setdefault("category", "Field")
        icon_name = app.get("icon") or "nexus-field"
        resolved = _resolve_icon_file(icon_name)
        if not resolved:
            for candidate in (
                INSTALL / "panel/assets/nexus-field.png",
                INSTALL / "panel/assets/nexus-field-48.png",
                INSTALL.parent / "Queen/world/icons/queen-browser.png",
            ):
                if candidate.is_file():
                    resolved = candidate
                    break
        if resolved:
            token = _cache_icon(app.get("id", icon_name), resolved)
            if token:
                app["icon_url"] = f"/api/field-host-desktop/icon/{quote(token, safe='')}"
        out.append(app)
    return out


def _running_programs() -> list[dict[str, Any]]:
    names = {
        "nexus-genius": "NEXUS Daemon",
        "threat-panel-http": "Field Panel",
        "queen-world": "Queen World",
        "firefox": "Firefox",
        "chromium": "Chromium",
        "google-chrome": "Chrome",
        "code": "VS Code",
        "obs": "OBS Studio",
    }
    running: list[dict[str, Any]] = []
    try:
        proc = subprocess.run(["ps", "-eo", "comm="], capture_output=True, text=True, timeout=5)
        lines = {ln.strip().lower() for ln in (proc.stdout or "").splitlines() if ln.strip()}
    except (OSError, subprocess.TimeoutExpired):
        lines = set()
    for comm, label in names.items():
        if comm in lines or any(comm in ln for ln in lines):
            running.append({"id": f"run-{comm}", "name": label, "comm": comm, "source": "process"})
    return running


def _power_actions() -> list[dict[str, Any]]:
    return [
        {"id": "underlay-drop", "label": "Drop under host desktop", "action": "underlay-drop"},
        {"id": "underlay-rise", "label": "Rise field OS", "action": "underlay-rise"},
        {"id": "freeze-soft", "label": "Soft freeze host", "action": "freeze-soft"},
        {"id": "sleep", "label": "Sleep", "action": "freeze-mem"},
        {"id": "underlay", "label": "Underlay F9", "exec": "/underlay-f9"},
        {"id": "command", "label": "NEXUS Command", "exec": "/command"},
    ]


def _menu_for_theme(theme: str, apps: list[dict[str, Any]]) -> dict[str, Any]:
    categories: dict[str, list[dict[str, Any]]] = {}
    for app in apps:
        cat = app.get("category") or "Other"
        categories.setdefault(cat, []).append(app)
    pinned = [a for a in apps if a.get("pinned")]
    alpha = sorted(apps, key=lambda x: x["name"].lower())
    if theme.startswith("windows"):
        return {
            "style": "windows",
            "layout": "two_column",
            "pinned": pinned[:12],
            "programs": alpha,
            "power": _power_actions(),
            "search": True,
        }
    if theme == "kde":
        return {
            "style": "kde",
            "layout": "sidebar_categories",
            "categories": {k: sorted(v, key=lambda x: x["name"].lower()) for k, v in sorted(categories.items())},
            "favorites": pinned,
            "power": _power_actions(),
            "search": True,
        }
    if theme == "macos":
        return {
            "style": "macos",
            "layout": "launchpad_grid",
            "programs": alpha,
            "dock_pinned": pinned,
            "power": _power_actions(),
            "search": True,
        }
    return {
        "style": "gnome",
        "layout": "grid_search",
        "frequent": pinned,
        "programs": alpha,
        "categories": list(sorted(categories.keys())),
        "power": _power_actions(),
        "search": True,
    }


def build_panel() -> dict[str, Any]:
    guest = _guest_system()
    theme = _theme_id()
    host_apps = _scan_linux_apps() if guest in ("linux", "windows") else []
    field_apps = _field_apps()
    merged: dict[str, dict[str, Any]] = {}
    for app in field_apps + host_apps:
        merged[app["name"].lower()] = app
    apps = sorted(merged.values(), key=lambda x: x["name"].lower())
    doc = {
        "schema": "field-host-desktop/v1",
        "ts": _now(),
        "ok": True,
        "guest_os": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "detected": guest,
        },
        "theme": theme,
        "linux_de": _linux_de() if guest == "linux" else None,
        "program_count": len(apps),
        "programs": apps,
        "field_apps": field_apps,
        "host_apps": host_apps,
        "running": _running_programs(),
        "menu": _menu_for_theme(theme, apps),
        "startbar": {
            "position": "bottom",
            "start_corner": "left",
            "show_clock": True,
            "show_running": True,
            "long_press_ms": int(_load(DOCTRINE, {}).get("policy", {}).get("touch_long_press_ms", 480)),
        },
        "routes": {
            "command": "/command",
            "underlay": "/underlay-f9",
            "tristate": "/tristate-installer",
        },
        "posture": "Host desktop mirrors incumbent OS — programs, icons, start menu, field startbar overlay",
    }
    _save_atomic(PANEL_FILE, doc)
    STAMP.write_text(_now() + "\n", encoding="utf-8")
    return doc


def posture() -> dict[str, Any]:
    if PANEL_FILE.is_file():
        try:
            cached = json.loads(PANEL_FILE.read_text(encoding="utf-8"))
            if cached.get("programs"):
                cached["ts"] = _now()
                cached["running"] = _running_programs()
                return cached
        except (OSError, json.JSONDecodeError):
            pass
    return build_panel()


def icon_bytes(token: str) -> tuple[bytes, str] | None:
    path = _safe_icon_path(token)
    if not path:
        return None
    data = path.read_bytes()
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return data, mime


def icon_data_url(token: str) -> str | None:
    got = icon_bytes(token)
    if not got:
        return None
    data, mime = got
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "status", "posture"):
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "build":
        print(json.dumps(build_panel(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "icon" and len(sys.argv) > 2:
        got = icon_bytes(sys.argv[2])
        if not got:
            print(json.dumps({"ok": False, "error": "icon_not_found"}))
            return 1
        data, mime = got
        print(json.dumps({"ok": True, "mime": mime, "data_url": icon_data_url(sys.argv[2])}, ensure_ascii=False))
        return 0
    print("usage: field-host-desktop.py [json|build|icon TOKEN]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
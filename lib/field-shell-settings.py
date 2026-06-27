#!/usr/bin/env pythong
"""Field OS shell settings — taskbar, display scale, theme, wallpaper."""
from __future__ import annotations

import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
SETTINGS = STATE / "field-shell-settings.json"
DOCTRINE = INSTALL / "data" / "field-host-desktop-doctrine.json"

DEFAULTS: dict[str, Any] = {
    "taskbar_auto_hide": False,
    "taskbar_peek": True,
    "desktop_icon_size": 40,
    "ui_scale": 100,
    "theme_override": "",
    "wallpaper": "default",
    "sort_desktop": "name",
    "show_desktop_icons": True,
    "fullscreen_programs": True,
    "fullscreen_desktop": True,
    "alt_tab_enabled": True,
    "queen_browser_only": True,
}


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


def _display_modes() -> list[dict[str, Any]]:
    script = INSTALL / "lib" / "field-display-open.py"
    if script.is_file():
        try:
            proc = subprocess.run(
                [os.environ.get("PYTHON", "pythong"), str(script), "json"],
                capture_output=True,
                text=True,
                timeout=12,
                env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL), "NEXUS_STATE_DIR": str(STATE)},
            )
            if proc.returncode == 0:
                doc = json.loads(proc.stdout or "{}")
                return doc.get("displays") or []
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
            pass
    return [{"id": "default", "name": "Default display", "backend": "unknown", "connected": True, "primary": True}]


def _hardware_summary() -> dict[str, Any]:
    script = INSTALL / "lib" / "field-hardware-probe.py"
    if not script.is_file():
        return {"ok": False, "error": "hardware_probe_missing"}
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "pythong"), str(script), "json"],
            capture_output=True,
            text=True,
            timeout=20,
            env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL), "NEXUS_STATE_DIR": str(STATE)},
        )
        if proc.returncode == 0:
            doc = json.loads(proc.stdout or "{}")
            doc["ok"] = True
            return doc
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return {"ok": False, "error": "hardware_probe_failed"}


def _version() -> str:
    common = INSTALL / "lib" / "nexus-common.sh"
    if common.is_file():
        try:
            proc = subprocess.run(
                ["bash", "-c", f'source "{common}" && echo -n "$NEXUS_VERSION"'],
                capture_output=True,
                text=True,
                timeout=5,
            )
            ver = (proc.stdout or "").strip()
            if ver:
                return ver
        except (OSError, subprocess.TimeoutExpired):
            pass
    return "0.9.0"


def posture() -> dict[str, Any]:
    saved = _load(SETTINGS, {})
    settings = {**DEFAULTS, **{k: v for k, v in saved.items() if k in DEFAULTS}}
    displays = _display_modes()
    hw = _hardware_summary()
    return {
        "schema": "field-shell-settings/v1",
        "ts": _now(),
        "ok": True,
        "settings": settings,
        "defaults": DEFAULTS,
        "displays": displays,
        "hardware": hw,
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "hostname": platform.node(),
        },
        "version": _version(),
        "control_panel": {
            "display": True,
            "theme": True,
            "hardware": bool(hw.get("ok", True)),
            "system": True,
            "personalization": True,
        },
    }


def apply_patch(patch: dict[str, Any]) -> dict[str, Any]:
    current = _load(SETTINGS, {})
    merged = {**DEFAULTS, **{k: v for k, v in current.items() if k in DEFAULTS}}
    for key, val in (patch or {}).items():
        if key not in DEFAULTS:
            continue
        if key == "ui_scale":
            merged[key] = max(75, min(200, int(val)))
        elif key == "desktop_icon_size":
            merged[key] = max(24, min(96, int(val)))
        elif key == "taskbar_auto_hide":
            merged[key] = bool(val)
        elif key == "taskbar_peek":
            merged[key] = bool(val)
        elif key == "show_desktop_icons":
            merged[key] = bool(val)
        elif key == "fullscreen_programs":
            merged[key] = bool(val)
        elif key == "alt_tab_enabled":
            merged[key] = bool(val)
        elif key in ("theme_override", "wallpaper", "sort_desktop"):
            merged[key] = str(val or "")
    doc = {"schema": "field-shell-settings/v1", "ts": _now(), **merged}
    _save_atomic(SETTINGS, doc)
    out = posture()
    out["applied"] = list(patch.keys()) if patch else []
    return out


def set_resolution(display_id: str, resolution: str) -> dict[str, Any]:
    display_id = (display_id or "").strip()
    resolution = (resolution or "").strip()
    if not resolution or "x" not in resolution:
        return {"ok": False, "error": "invalid_resolution"}
    if not display_id:
        displays = _display_modes()
        primary = next((d for d in displays if d.get("primary")), displays[0] if displays else None)
        display_id = str((primary or {}).get("id") or "default")
    if display_id in ("default", "wayland-primary"):
        return {
            "ok": True,
            "display_id": display_id,
            "resolution": resolution,
            "applied": False,
            "message": "Resolution change recorded — apply via host display settings on Wayland.",
        }
    try:
        proc = subprocess.run(
            ["xrandr", "--output", display_id, "--mode", resolution.split("@", 1)[0]],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        ok = proc.returncode == 0
        return {
            "ok": ok,
            "display_id": display_id,
            "resolution": resolution,
            "applied": ok,
            "stderr": (proc.stderr or "").strip()[:400] if not ok else "",
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc)}


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "status", "posture"):
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "apply":
        raw = sys.stdin.read() if not sys.stdin.isatty() else (sys.argv[2] if len(sys.argv) > 2 else "{}")
        try:
            patch = json.loads(raw or "{}")
        except json.JSONDecodeError:
            print(json.dumps({"ok": False, "error": "invalid_json"}))
            return 1
        print(json.dumps(apply_patch(patch), ensure_ascii=False, indent=2))
        return 0
    if cmd == "resolution" and len(sys.argv) > 3:
        print(json.dumps(set_resolution(sys.argv[2], sys.argv[3]), ensure_ascii=False, indent=2))
        return 0
    print("usage: field-shell-settings.py [json|apply|resolution DISPLAY MODE]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
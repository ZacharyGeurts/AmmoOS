#!/usr/bin/env python3
"""NEXUS panel system tray — pick a tab and open in browser."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("AyatanaAppIndicator3", "0.1")
from gi.repository import AyatanaAppIndicator3, GLib, Gtk  # noqa: E402

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", Path(__file__).resolve().parent.parent))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
PORT = os.environ.get("NEXUS_THREAT_PANEL_PORT", "9477")
TLS = os.environ.get("NEXUS_PANEL_TLS", "1") == "1"
APP_ID = "nexus-shield-panel"
LAST_TAB_FILE = STATE / "panel-tray-last-tab.json"

TAB_CHOICES: list[tuple[str, str]] = [
    ("Command", "command"),
    ("US field", "us"),
    ("Packets · Live", "packets/monitor"),
    ("Packets · DPI", "packets/inspect"),
    ("Threats · Home", "threats/home-protector"),
    ("Threats · Map", "threats/host-attack"),
    ("Threats · Kill orders", "threats/human-dossier"),
    ("Intel · Honor", "intel/honor"),
    ("Intel · Field RF", "intel/field-rf"),
    ("Intel · Research", "intel/research"),
    ("Signals", "signals"),
    ("DNS", "dns"),
    ("Outside", "outside"),
    ("Library · Books", "library"),
    ("System · Settings", "system/settings"),
    ("System · Logs", "system/logs"),
]


def _panel_base() -> str:
    scheme = "https" if TLS else "http"
    return f"{scheme}://127.0.0.1:{PORT}/field"


def _ensure_tray_icon() -> Path:
    icon = STATE / "nexus-tray.png"
    if icon.is_file() and icon.stat().st_size > 0:
        return icon
    src = INSTALL / "panel" / "assets" / "nexus-shield.png"
    if not src.is_file():
        src = INSTALL / "assets" / "nexus-shield.png"
    icon.parent.mkdir(parents=True, exist_ok=True)
    if src.is_file():
        try:
            from PIL import Image

            img = Image.open(src).convert("RGBA")
            img = img.resize((24, 24), Image.Resampling.LANCZOS)
            img.save(icon, format="PNG")
            return icon
        except Exception:
            pass
    # Minimal shield fallback
    try:
        from PIL import Image, ImageDraw

        img = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.polygon([(12, 2), (22, 8), (18, 22), (6, 22), (2, 8)], fill=(201, 162, 39, 255))
        draw.rectangle([(7, 7), (16, 11)], fill=(59, 130, 246, 255))
        img.save(icon, format="PNG")
    except Exception:
        icon.write_bytes(b"")
    return icon


def _save_last_tab(route: str) -> None:
    try:
        LAST_TAB_FILE.parent.mkdir(parents=True, exist_ok=True)
        LAST_TAB_FILE.write_text(
            json.dumps({"route": route, "url": f"{_panel_base()}#{route}"}, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass


def _load_last_tab() -> str:
    try:
        doc = json.loads(LAST_TAB_FILE.read_text(encoding="utf-8"))
        return str(doc.get("route") or "command")
    except (OSError, json.JSONDecodeError, TypeError):
        return "command"


def _detect_browser() -> list[str]:
    for name in (
        "xdg-open",
        "google-chrome-stable",
        "google-chrome",
        "chromium-browser",
        "chromium",
        "firefox",
        "brave-browser",
        "microsoft-edge",
    ):
        try:
            proc = subprocess.run(["which", name], capture_output=True, text=True, timeout=3)
            if proc.returncode == 0 and (proc.stdout or "").strip():
                yield name
        except (OSError, subprocess.TimeoutExpired):
            continue


def open_tab(route: str = "command") -> None:
    route = (route or "command").strip().lstrip("#")
    url = f"{_panel_base()}#{route}"
    _save_last_tab(route)
    env = os.environ.copy()
    env.setdefault("DISPLAY", ":0")
    for browser in _detect_browser():
        try:
            if browser == "xdg-open":
                subprocess.Popen(["xdg-open", url], env=env, start_new_session=True)
            elif browser in ("google-chrome-stable", "google-chrome", "chromium-browser", "chromium"):
                subprocess.Popen(
                    [browser, "--ignore-certificate-errors", f"--app={url}", "--new-window"],
                    env=env,
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.Popen(
                    [browser, "--new-window", url],
                    env=env,
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return
        except OSError:
            continue


class NexusTray:
    def __init__(self) -> None:
        icon_path = str(_ensure_tray_icon())
        self.indicator = AyatanaAppIndicator3.Indicator.new(
            APP_ID,
            icon_path if Path(icon_path).is_file() and Path(icon_path).stat().st_size else "security-high",
            AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        self.indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_title("NEXUS-Shield — right-click to pick a tab")
        self.indicator.set_menu(self._build_menu())

    def _build_menu(self) -> Gtk.Menu:
        menu = Gtk.Menu()

        header = Gtk.MenuItem(label="Go to tab")
        header.set_sensitive(False)
        menu.append(header)

        for label, route in TAB_CHOICES:
            item = Gtk.MenuItem(label=label)
            item.connect("activate", self._on_tab, route)
            menu.append(item)

        menu.append(Gtk.SeparatorMenuItem())

        last = Gtk.MenuItem(label=f"Last tab ({_load_last_tab()})")
        last.connect("activate", self._on_last)
        menu.append(last)

        panel = Gtk.MenuItem(label="Open panel home")
        panel.connect("activate", self._on_home)
        menu.append(panel)

        menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit tray icon")
        quit_item.connect("activate", self._on_quit)
        menu.append(quit_item)

        menu.show_all()
        return menu

    def _on_tab(self, _item, route: str) -> None:  # noqa: ANN001
        open_tab(route)

    def _on_last(self, _item) -> None:  # noqa: ANN001
        open_tab(_load_last_tab())

    def _on_home(self, _item) -> None:  # noqa: ANN001
        open_tab("command")

    def _on_quit(self, _item) -> None:  # noqa: ANN001
        Gtk.main_quit()


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "open":
        open_tab(sys.argv[2] if len(sys.argv) > 2 else _load_last_tab())
        return 0
    Gtk.init(sys.argv)
    NexusTray()
    Gtk.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
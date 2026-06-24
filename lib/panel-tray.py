#!/usr/bin/env python3
"""NEXUS panel system tray — left or right click opens tab picker."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # noqa: E402

try:
    gi.require_version("AyatanaAppIndicator3", "0.1")
    from gi.repository import AyatanaAppIndicator3  # noqa: E402

    HAS_APPINDICATOR = True
except (ImportError, ValueError):
    HAS_APPINDICATOR = False

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


def _tray_icon_source() -> Path:
    for rel in (
        "panel/assets/nexus-tray-amouranth-24.png",
        "panel/assets/nexus-tray-amouranth.png",
        "panel/assets/amouranth-twitch-avatar.png",
        "panel/assets/nexus-shield.png",
        "assets/nexus-shield.png",
    ):
        p = INSTALL / rel
        if p.is_file() and p.stat().st_size > 0:
            return p
    return INSTALL / "panel" / "assets" / "nexus-shield.png"


def _icon_stamp(src: Path) -> str:
    try:
        st = src.stat()
        return f"{src}:{st.st_mtime_ns}:{st.st_size}"
    except OSError:
        return ""


def _ensure_tray_icon(*, force: bool = False) -> Path:
    icon = STATE / "nexus-tray.png"
    stamp_file = STATE / "nexus-tray-icon.stamp"
    src = _tray_icon_source()
    icon.parent.mkdir(parents=True, exist_ok=True)
    stamp = _icon_stamp(src)
    if src.is_file():
        try:
            if (
                not force
                and icon.is_file()
                and icon.stat().st_size > 0
                and stamp_file.is_file()
                and stamp_file.read_text(encoding="utf-8", errors="replace").strip() == stamp
            ):
                return icon
            from PIL import Image

            img = Image.open(src).convert("RGBA")
            img = img.resize((24, 24), Image.Resampling.LANCZOS)
            img.save(icon, format="PNG")
            if stamp:
                stamp_file.write_text(stamp + "\n", encoding="utf-8")
            return icon
        except Exception:
            if icon.is_file() and icon.stat().st_size > 0:
                return icon
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


class TabPickerPopup(Gtk.Window):
    """Fast-track tab list — single click opens browser tab; no quit/cancel chrome."""

    def __init__(self) -> None:
        super().__init__(title="NEXUS-Shield — Tab")
        self.set_default_size(360, 420)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_type_hint(Gtk.WindowTypeHint.UTILITY)
        self.connect("delete-event", lambda *_: False)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        outer.set_margin_top(12)
        outer.set_margin_bottom(12)
        outer.set_margin_start(12)
        outer.set_margin_end(12)

        hint = Gtk.Label(label="Click a tab — opens immediately in your browser")
        hint.set_xalign(0)
        hint.set_line_wrap(True)
        outer.pack_start(hint, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(300)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.set_activate_on_single_click(True)
        for label, route in TAB_CHOICES:
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            box.set_margin_top(6)
            box.set_margin_bottom(6)
            box.set_margin_start(8)
            box.set_margin_end(8)
            title = Gtk.Label(label=label)
            title.set_xalign(0)
            title.get_style_context().add_class("title")
            route_lbl = Gtk.Label(label=route)
            route_lbl.set_xalign(0)
            route_lbl.get_style_context().add_class("dim-label")
            box.pack_start(title, False, False, 0)
            box.pack_start(route_lbl, False, False, 0)
            row.add(box)
            row.route = route  # type: ignore[attr-defined]
            self.listbox.add(row)
        self.listbox.connect("row-activated", self._on_row_activated)
        scroll.add(self.listbox)
        outer.pack_start(scroll, True, True, 0)

        last_row = next(
            (row for row in self.listbox.get_children() if getattr(row, "route", None) == _load_last_tab()),
            None,
        )
        if last_row:
            self.listbox.select_row(last_row)
        self.add(outer)

    def _on_row_activated(self, _listbox, row) -> None:  # noqa: ANN001
        open_tab(str(getattr(row, "route", "command")))
        self.destroy()


_dialog_open = False


def show_tab_picker() -> None:
    global _dialog_open
    if _dialog_open:
        return
    _dialog_open = True

    def _on_destroy(_widget) -> None:  # noqa: ANN001
        global _dialog_open
        _dialog_open = False

    popup = TabPickerPopup()
    popup.connect("destroy", _on_destroy)
    popup.show_all()
    popup.present()


class NexusTray:
    def __init__(self) -> None:
        force_icon = os.environ.get("NEXUS_TRAY_ICON_REFRESH", "0") == "1"
        icon_path = str(_ensure_tray_icon(force=force_icon))
        self._status_icon = None
        self._indicator = None

        if self._try_status_icon(icon_path):
            return
        if HAS_APPINDICATOR:
            self._try_app_indicator(icon_path)

    def _try_status_icon(self, icon_path: str) -> bool:
        try:
            icon = Gtk.StatusIcon()
            if Path(icon_path).is_file() and Path(icon_path).stat().st_size:
                icon.set_from_file(icon_path)
            else:
                icon.set_from_icon_name("security-high")
            icon.set_tooltip_text("NEXUS-Shield · Amouranth — click to pick a panel tab")
            icon.set_visible(True)
            icon.connect("activate", lambda *_: show_tab_picker())
            icon.connect("popup-menu", lambda *_: show_tab_picker())
            self._status_icon = icon
            return True
        except Exception:
            return False

    def _try_app_indicator(self, icon_path: str) -> None:
        self._indicator = AyatanaAppIndicator3.Indicator.new(
            APP_ID,
            icon_path if Path(icon_path).is_file() and Path(icon_path).stat().st_size else "security-high",
            AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        self._indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)
        self._indicator.set_title("NEXUS-Shield · Amouranth — click to pick a panel tab")
        # Ayatana opens this menu on left or right click — show the tab picker instead.
        menu = Gtk.Menu()
        menu.connect("show", self._on_indicator_menu_show)
        self._indicator.set_menu(menu)

    def _on_indicator_menu_show(self, menu: Gtk.Menu) -> None:
        menu.hide()
        GLib.idle_add(show_tab_picker)


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
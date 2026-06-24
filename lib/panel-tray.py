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
from gi.repository import Gtk  # noqa: E402

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


def _install_xdg_tray_icon(icon: Path) -> str:
    """Install 22/24/32 px tray icons so AppIndicator picks max taskbar resolution."""
    try:
        import importlib.util

        mod_path = INSTALL / "lib" / "panel-tray-icon.py"
        spec = importlib.util.spec_from_file_location("panel_tray_icon", mod_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.install_xdg_tray_icons(INSTALL)
            return "nexus-shield-panel"
    except Exception:
        pass
    home = Path(os.environ.get("HOME", "/home/default"))
    theme_icon = home / ".local/share/icons/hicolor/32x32/apps/nexus-shield-panel.png"
    try:
        theme_icon.parent.mkdir(parents=True, exist_ok=True)
        if icon.is_file() and icon.stat().st_size > 0:
            theme_icon.write_bytes(icon.read_bytes())
            subprocess.run(
                ["gtk-update-icon-cache", str(theme_icon.parent.parent)],
                capture_output=True,
                timeout=8,
            )
            return "nexus-shield-panel"
    except (OSError, subprocess.TimeoutExpired):
        pass
    return str(icon)


def _ensure_tray_icon(*, force: bool = False) -> Path:
    icon = STATE / "nexus-tray.png"
    icon.parent.mkdir(parents=True, exist_ok=True)
    try:
        import importlib.util

        mod_path = INSTALL / "lib" / "panel-tray-icon.py"
        spec = importlib.util.spec_from_file_location("panel_tray_icon", mod_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.build_tray_icons(INSTALL, STATE, force=force)
    except Exception:
        pass
    src = _tray_icon_source()
    stamp_file = STATE / "nexus-tray-icon.stamp"
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

            img = Image.open(src).convert("RGBA").resize((24, 24), Image.Resampling.LANCZOS)
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
        try:
            utility = getattr(Gtk, "WindowTypeHint", None)
            if utility is not None:
                self.set_type_hint(utility.UTILITY)
        except (AttributeError, TypeError):
            pass
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


def _populate_tray_flyout(menu: Gtk.Menu) -> None:
    """Fill tray menu with tab rows — dbus/AppIndicator needs each item shown individually."""
    for child in list(menu.get_children()):
        menu.remove(child)
        child.destroy()
    last = _load_last_tab()
    for label, route in TAB_CHOICES:
        title = f"★ {label}" if route == last else label
        item = Gtk.MenuItem.new_with_label(title)
        item.connect("activate", lambda _w, r=route: open_tab(r))
        item.show()
        menu.append(item)


def build_tray_flyout_menu() -> Gtk.Menu:
    """Native tray flyout — menu anchored to the taskbar icon, not a popup window."""
    menu = Gtk.Menu()
    _populate_tray_flyout(menu)
    menu.show()
    return menu


def show_tab_picker(status_icon=None, button: int = 0, activate_time: int = 0) -> None:
    """Show the tray flyout menu (StatusIcon fallback path)."""
    menu = build_tray_flyout_menu()
    if status_icon is not None:
        menu.popup(None, None, status_icon.position_popup, status_icon, button, activate_time)
    else:
        menu.popup(None, None, None, None, button, activate_time)


class NexusTray:
    def __init__(self) -> None:
        force_icon = os.environ.get("NEXUS_TRAY_ICON_REFRESH", "0") == "1"
        icon_file = _ensure_tray_icon(force=force_icon)
        icon_ref = _install_xdg_tray_icon(icon_file)
        self._status_icon = None
        self._indicator = None
        self._flyout_menu = Gtk.Menu()
        self._flyout_menu.connect("show", self._refresh_flyout_menu)

        if HAS_APPINDICATOR and self._try_app_indicator(icon_ref):
            return
        self._try_status_icon(str(icon_file))

    def _refresh_flyout_menu(self, *_args) -> None:
        _populate_tray_flyout(self._flyout_menu)

    def _try_status_icon(self, icon_path: str) -> bool:
        try:
            icon = Gtk.StatusIcon()
            if Path(icon_path).is_file() and Path(icon_path).stat().st_size:
                icon.set_from_file(icon_path)
            else:
                icon.set_from_icon_name("security-high")
            icon.set_tooltip_text("NEXUS-Shield · Amouranth — click to pick a panel tab")
            icon.set_visible(True)
            icon.connect("activate", lambda ic, *_: show_tab_picker(ic, 1, Gtk.get_current_event_time()))
            icon.connect("popup-menu", lambda ic, btn, t: show_tab_picker(ic, btn, t))
            self._status_icon = icon
            return True
        except Exception:
            return False

    def _try_app_indicator(self, icon_ref: str) -> bool:
        try:
            icon_name = icon_ref
            if Path(icon_ref).is_file():
                if not Path(icon_ref).stat().st_size:
                    icon_name = "security-high"
            self._indicator = AyatanaAppIndicator3.Indicator.new(
                APP_ID,
                icon_name,
                AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS,
            )
            self._indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)
            self._indicator.set_title("NEXUS-Shield · Amouranth — click to pick a panel tab")
            _populate_tray_flyout(self._flyout_menu)
            self._indicator.set_menu(self._flyout_menu)
            return True
        except Exception:
            return False


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
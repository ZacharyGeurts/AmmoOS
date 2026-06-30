#!/usr/bin/env pythong
"""Queen Browser profile branding — full rebrand; reports Queen Browser, not Firefox."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

QUEEN = Path(__file__).resolve().parents[1]
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", str(QUEEN.parent)))
PANEL_PORT = int(os.environ.get("NEXUS_THREAT_PANEL_PORT", "9477") or "9477")
WORLD_PORT = int(os.environ.get("QUEEN_WORLD_PORT", "9481") or "9481")

QUEEN_UA = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) "
    "QueenBrowser/2026 AmmoOS/1.0 Gecko/20100101 QueenFieldEngine/128.0"
)


def _ammoos_url() -> str:
    env = os.environ.get("AMMOOS_DESKTOP_URL", "").strip()
    if env:
        return env
    return f"http://127.0.0.1:{PANEL_PORT}/field"


def _queen_shell_url() -> str:
    return f"http://127.0.0.1:{WORLD_PORT}/world/browser.html"


def user_js_lines(*, homepage: str | None = None) -> list[str]:
    home = homepage or _ammoos_url()
    return [
        "// Queen Browser — AmmoOS field profile (auto-generated; not Firefox)",
        'user_pref("general.useragent.override", "' + QUEEN_UA + '");',
        'user_pref("general.useragent.vendor", "AmmoOS Field");',
        'user_pref("general.useragent.vendorSub", "Queen Browser");',
        'user_pref("general.useragent.product", "QueenBrowser");',
        'user_pref("general.useragent.productSub", "2026");',
        'user_pref("general.useragent.locale", "en-US");',
        'user_pref("browser.startup.homepage", "' + home + '");',
        'user_pref("browser.startup.page", 1);',
        'user_pref("browser.startup.homepage_override.mstone", "ignore");',
        'user_pref("browser.shell.checkDefaultBrowser", false);',
        'user_pref("browser.aboutwelcome.enabled", false);',
        'user_pref("browser.aboutConfig.showWarning", false);',
        'user_pref("browser.rights.3.shown", true);',
        'user_pref("browser.rights.override.uri", "");',
        'user_pref("identity.fxaccount.enabled", false);',
        'user_pref("identity.fxaccounts.enabled", false);',
        'user_pref("toolkit.telemetry.enabled", false);',
        'user_pref("toolkit.telemetry.unified", false);',
        'user_pref("datareporting.healthreport.uploadEnabled", false);',
        'user_pref("datareporting.policy.dataSubmissionEnabled", false);',
        'user_pref("app.update.enabled", false);',
        'user_pref("app.update.auto", false);',
        'user_pref("browser.newtabpage.enabled", false);',
        'user_pref("browser.newtabpage.activity-stream.feeds.section.topstories", false);',
        'user_pref("browser.newtabpage.activity-stream.feeds.topsites", false);',
        'user_pref("browser.newtabpage.activity-stream.showSponsored", false);',
        'user_pref("browser.newtabpage.activity-stream.discoverystream.enabled", false);',
        'user_pref("browser.tabs.firefox-view", false);',
        'user_pref("extensions.pocket.enabled", false);',
        'user_pref("browser.pocket.enabled", false);',
        'user_pref("browser.search.defaultenginename", "DuckDuckGo");',
        'user_pref("browser.urlbar.placeholderName", "Queen Browser");',
        'user_pref("browser.fullscreen.autohide", true);',
        'user_pref("full-screen-api.ignore-widgets", true);',
        'user_pref("browser.tabs.inTitlebar", 0);',
        'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);',
        'user_pref("browser.tabs.unloadOnLowMemory", true);',
        'user_pref("dom.ipc.processCount", 8);',
        'user_pref("gfx.webrender.all", true);',
    ]


def user_chrome_css() -> str:
    return """/* Queen Browser — chrome rebrand */
#navigator-toolbox {
  border-top: 2px solid #1a4d32 !important;
}
.titlebar-text {
  font-size: 0 !important;
}
.titlebar-text::after {
  content: "Queen Browser";
  font-size: 11px;
  color: #3ecf8e;
  letter-spacing: 0.08em;
}
"""


def write_profile(
    profile_dir: Path,
    *,
    homepage: str | None = None,
) -> dict[str, Any]:
    profile_dir = profile_dir.expanduser().resolve()
    profile_dir.mkdir(parents=True, exist_ok=True)
    chrome = profile_dir / "chrome"
    chrome.mkdir(parents=True, exist_ok=True)
    user_js = profile_dir / "user.js"
    user_js.write_text("\n".join(user_js_lines(homepage=homepage)) + "\n", encoding="utf-8")
    (chrome / "userChrome.css").write_text(user_chrome_css(), encoding="utf-8")
    compat = profile_dir / "compatibility.ini"
    if not compat.is_file():
        compat.write_text(
            "[Compatibility]\nLastVersion=128.0\nLastOSABI=Linux_x86_64-gcc3\n",
            encoding="utf-8",
        )
    return {
        "ok": True,
        "profile": str(profile_dir),
        "user_js": str(user_js),
        "homepage": homepage or _ammoos_url(),
        "user_agent": QUEEN_UA,
        "product": "Queen Browser",
        "not_firefox": True,
    }


def default_profiles() -> list[Path]:
    roots = [
        QUEEN / "field-gecko" / "profile",
        INSTALL / "panel" / "profile-ammoos-desktop",
        INSTALL / "Queen" / "field-gecko" / "profile",
    ]
    seen: set[str] = set()
    out: list[Path] = []
    for p in roots:
        key = str(p.resolve()) if p.exists() or True else str(p)
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def seed_all(*, homepage: str | None = None) -> dict[str, Any]:
    profiles = []
    for p in default_profiles():
        profiles.append(write_profile(p, homepage=homepage))
    return {"ok": True, "seeded": profiles, "product": "Queen Browser"}


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "seed").strip().lower()
    if cmd in ("seed", "write", "all"):
        out = seed_all()
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    if cmd == "json":
        print(
            json.dumps(
                {
                    "product": "Queen Browser",
                    "user_agent": QUEEN_UA,
                    "ammoos_home": _ammoos_url(),
                    "queen_shell": _queen_shell_url(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    profile = sys.argv[2] if len(sys.argv) > 2 else str(QUEEN / "field-gecko" / "profile")
    out = write_profile(Path(profile))
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
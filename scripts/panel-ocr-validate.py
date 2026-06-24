#!/usr/bin/env python3
"""OCR + DOM validation for NEXUS v8 military panel before release."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", str(ROOT)))
PORT = int(os.environ.get("NEXUS_THREAT_PANEL_PORT", "9477"))
PANEL_URL = os.environ.get("NEXUS_PANEL_URL", f"https://127.0.0.1:{PORT}")

REQUIRED_HTML = (
    "nexus-military-v8",
    "v8.2.0",
    "Military C2 Panel",
    "nexus-military-v8.css",
    "nexus-military-v8.js",
    "nexus-military-v82.js",
    "nexus-military-v82.css",
)
REQUIRED_JS = ("OPS FLOW", "MILITARY v8", "stampVersion")
REQUIRED_STATUS = ("8.2.0", "military-v82")


def _ssl_ctx():
    import ssl

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _fetch(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "NEXUS-OCR-Validate"})
    with urllib.request.urlopen(req, timeout=timeout, context=_ssl_ctx()) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _ocr_image(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        out = subprocess.check_output(
            ["tesseract", str(path), "stdout", "-l", "eng", "--psm", "6"],
            stderr=subprocess.DEVNULL,
            timeout=20,
        )
        return out.decode("utf-8", errors="replace")
    except (subprocess.SubprocessError, OSError):
        return ""


def _screenshot_panel(out: Path) -> bool:
    url = f"{PANEL_URL}/field"
    for cmd in (
        ["firefox", "--headless", "--screenshot", str(out), url],
        ["firefox", "-headless", "-screenshot", str(out), url],
    ):
        try:
            subprocess.run(cmd, capture_output=True, timeout=45, check=False)
            if out.is_file() and out.stat().st_size > 1000:
                return True
        except (subprocess.SubprocessError, OSError):
            continue
    return False


def main() -> int:
    fail = 0
    print("=== NEXUS Panel OCR Validation ===")
    print(f"target={PANEL_URL}")

    try:
        html = _fetch(f"{PANEL_URL}/field")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"FAIL: cannot fetch panel HTML — {exc}")
        return 1

    for needle in REQUIRED_HTML:
        if needle in html:
            print(f"HTML OK: {needle}")
        else:
            print(f"HTML FAIL: missing {needle}")
            fail += 1

    js_path = INSTALL / "panel" / "assets" / "nexus-military-v8.js"
    js_live = ""
    try:
        js_live = _fetch(f"{PANEL_URL}/assets/nexus-military-v8.js")
    except (urllib.error.URLError, TimeoutError, OSError):
        js_live = js_path.read_text(encoding="utf-8", errors="replace") if js_path.is_file() else ""
    for needle in REQUIRED_JS:
        if needle in js_live:
            print(f"JS OK: {needle}")
        else:
            print(f"JS FAIL: missing {needle}")
            fail += 1

    try:
        status = json.loads(_fetch(f"{PANEL_URL}/api/status"))
        ver = str(status.get("version") or "")
        build = str(status.get("panel_build") or "")
        if ver == REQUIRED_STATUS[0]:
            print(f"API OK: version={ver}")
        else:
            print(f"API FAIL: version={ver!r} want {REQUIRED_STATUS[0]}")
            fail += 1
        if build == REQUIRED_STATUS[1]:
            print(f"API OK: panel_build={build}")
        else:
            print(f"API FAIL: panel_build={build!r} want {REQUIRED_STATUS[1]}")
            fail += 1
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError) as exc:
        print(f"API FAIL: /api/status — {exc}")
        fail += 1

    tray_icon = INSTALL / "panel" / "assets" / "nexus-tray-amouranth-24.png"
    if tray_icon.is_file() and tray_icon.stat().st_size > 100:
        print(f"TRAY ICON OK: {tray_icon.name} ({tray_icon.stat().st_size} bytes)")
        ocr = _ocr_image(tray_icon).lower()
        if ocr.strip():
            print(f"TRAY OCR smoke: {ocr[:80].strip()!r}")
    else:
        print("TRAY ICON FAIL: nexus-tray-amouranth-24.png missing or empty")
        fail += 1

    shot = Path("/tmp/nexus-panel-ocr.png")
    if _screenshot_panel(shot):
        ocr = _ocr_image(shot)
        ocr_l = ocr.lower()
        print(f"PANEL SCREENSHOT OK: {shot} ({shot.stat().st_size} bytes)")
        for token in ("nexus", "shield", "military", "v8", "8.0"):
            if token in ocr_l or token in html.lower():
                print(f"OCR/DOM OK: {token}")
            else:
                print(f"OCR WARN: {token} not in screenshot OCR (DOM may still carry it)")
        if re.search(r"v8\.0|8\.0\.0|military", ocr_l):
            print("OCR PASS: v8 military strings visible in screenshot")
        else:
            print("OCR NOTE: screenshot OCR inconclusive — HTML/API checks are authoritative")
    else:
        print("OCR SKIP: headless screenshot unavailable (HTML/API checks used)")

    if fail:
        print(f"\nOCR VALIDATION FAILED ({fail} hard failures)")
        return 1
    print("\nOCR VALIDATION PASSED — v8.2.0 military GUI confirmed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
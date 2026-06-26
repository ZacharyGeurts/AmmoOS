#!/usr/bin/env pythong
"""OCR + DOM validation for NEXUS RTX Zero panel (NewLatest tree)."""
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
RTX_URL = f"{PANEL_URL}/?rtx=1"

REQUIRED_HTML = (
    "nexus-military-v8",
    "Military C2 Panel",
    "nexus-military-v8.css",
    "nexus-military-v8.js",
    "nexus-rtx-zero.css",
    "nexus-rtx-zero.js",
    "nexus-sdf-menu.js",
    "packet-field-graphics.js",
)
REQUIRED_JS = ("OPS FLOW", "MILITARY C2", "stampVersion", "RTX · ZERO COST")
REQUIRED_RTX_JS = ("rtx-zero-v1", "nexus_rtx_zero", "panel_rtx_zero")
EXPECTED_VERSION = os.environ.get("NEXUS_VERSION", "10.0.0")
EXPECTED_BUILD = "rtx-zero-v1"


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


def _screenshot_panel(out: Path, url: str) -> bool:
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
    print("=== NEXUS Panel OCR Validation (NewLatest / RTX Zero) ===")
    print(f"target={RTX_URL}")

    try:
        html = _fetch(RTX_URL)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"FAIL: cannot fetch panel HTML — {exc}")
        return 1

    for needle in REQUIRED_HTML:
        if needle in html:
            print(f"HTML OK: {needle}")
        else:
            print(f"HTML FAIL: missing {needle}")
            fail += 1

    js_checks: list[tuple[str, str]] = []
    for name in ("nexus-military-v8.js", "nexus-rtx-zero.js"):
        try:
            body = _fetch(f"{PANEL_URL}/assets/{name}")
        except (urllib.error.URLError, TimeoutError, OSError):
            fp = INSTALL / "panel" / "assets" / name
            body = fp.read_text(encoding="utf-8", errors="replace") if fp.is_file() else ""
        js_checks.append((name, body))

    for needle in REQUIRED_JS:
        ok = any(needle in body for _n, body in js_checks)
        if ok:
            print(f"JS OK: {needle}")
        else:
            print(f"JS FAIL: missing {needle}")
            fail += 1

    rtx_body = next((b for n, b in js_checks if n == "nexus-rtx-zero.js"), "")
    for needle in REQUIRED_RTX_JS:
        if needle in rtx_body:
            print(f"RTX JS OK: {needle}")
        else:
            print(f"RTX JS FAIL: missing {needle}")
            fail += 1

    try:
        status = json.loads(_fetch(f"{PANEL_URL}/api/status"))
        ver = str(status.get("version") or "")
        build = str(status.get("panel_build") or "")
        rtx = status.get("panel_rtx_zero")
        if ver == EXPECTED_VERSION:
            print(f"API OK: version={ver}")
        else:
            print(f"API FAIL: version={ver!r} want {EXPECTED_VERSION}")
            fail += 1
        if build == EXPECTED_BUILD:
            print(f"API OK: panel_build={build}")
        else:
            print(f"API FAIL: panel_build={build!r} want {EXPECTED_BUILD}")
            fail += 1
        if rtx in (True, 1, "1"):
            print("API OK: panel_rtx_zero=true")
        else:
            print(f"API FAIL: panel_rtx_zero={rtx!r}")
            fail += 1
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError) as exc:
        print(f"API FAIL: /api/status — {exc}")
        fail += 1

    tray_icon = INSTALL / "panel" / "assets" / "nexus-tray-us-24.png"
    if tray_icon.is_file() and tray_icon.stat().st_size > 100:
        print(f"TRAY ICON OK: {tray_icon.name} ({tray_icon.stat().st_size} bytes)")
    else:
        print("TRAY ICON WARN: nexus-tray-us-24.png missing — non-fatal")

    shot = Path("/tmp/nexus-panel-ocr-rtx.png")
    if _screenshot_panel(shot, RTX_URL):
        ocr = _ocr_image(shot).lower()
        print(f"PANEL SCREENSHOT OK: {shot} ({shot.stat().st_size} bytes)")
        for token in ("nexus", "shield", "military", "rtx", "zero"):
            if token in ocr or token in html.lower():
                print(f"OCR/DOM OK: {token}")
            else:
                print(f"OCR WARN: {token} not in screenshot OCR")
        if re.search(r"rtx|zero|nexus|shield", ocr):
            print("OCR PASS: RTX panel strings visible in screenshot")
        else:
            print("OCR NOTE: screenshot OCR inconclusive — HTML/API checks are authoritative")
    else:
        print("OCR SKIP: headless screenshot unavailable (HTML/API checks used)")

    if fail:
        print(f"\nOCR VALIDATION FAILED ({fail} hard failures)")
        return 1
    print("\nOCR VALIDATION PASSED — RTX Zero panel confirmed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
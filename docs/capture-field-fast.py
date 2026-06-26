#!/usr/bin/env pythong
"""Benchmark /field first paint and OCR-verify header + connections."""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
URL = os.environ.get("NEXUS_PANEL_URL", "https://127.0.0.1:9477/field")


def _ensure_playwright():
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ImportError:
        venv = Path("/tmp/nexus-cap-venv")
        if not (venv / "bin" / "python").is_file():
            subprocess.check_call([sys.executable, "-m", "venv", str(venv)])
        subprocess.check_call([str(venv / "bin" / "pip"), "install", "playwright", "-q"])
        subprocess.check_call([str(venv / "bin" / "playwright"), "install", "chromium"])
        sys.path.insert(0, str(venv / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"))
        from playwright.sync_api import sync_playwright
        return sync_playwright


def _ocr(img_path: Path) -> str:
    tess = None
    for candidate in ("tesseract", "/usr/bin/tesseract"):
        try:
            proc = subprocess.run([candidate, "--version"], capture_output=True, timeout=5)
            if proc.returncode == 0:
                tess = candidate
                break
        except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
            continue
    if not tess:
        return ""
    for extra in (["-l", "eng", "--psm", "6"], []):
        try:
            proc = subprocess.run([tess, str(img_path), "stdout", *extra], capture_output=True, text=True, timeout=30)
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout
        except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
            continue
    return ""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sync_playwright = _ensure_playwright()
    timings = {}
    ocr_text = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True)
        page = ctx.new_page()

        t0 = time.perf_counter()
        page.goto(URL, wait_until="commit", timeout=30000)
        timings["commit_ms"] = round((time.perf_counter() - t0) * 1000, 1)

        page.wait_for_selector("#mode", timeout=10000)
        timings["mode_el_ms"] = round((time.perf_counter() - t0) * 1000, 1)

        try:
            page.wait_for_function(
                "() => document.getElementById('mode')?.textContent !== '—'",
                timeout=5000,
            )
            timings["mode_paint_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        except Exception:
            timings["mode_paint_ms"] = None

        try:
            page.wait_for_function(
                "() => { const el = document.getElementById('connections'); "
                "return el && !el.textContent.includes('Loading connections'); }",
                timeout=8000,
            )
            timings["connections_paint_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        except Exception:
            timings["connections_paint_ms"] = None

        bootstrap = page.evaluate(
            "() => !!(window.NEXUS_FIELD && document.getElementById('nexus-field-bootstrap'))"
        )
        live = page.evaluate(
            "() => ({ mode: document.getElementById('mode')?.textContent, "
            "live: document.getElementById('field-live')?.textContent, "
            "updated: document.getElementById('updated')?.textContent, "
            "egress: document.getElementById('egress')?.textContent, "
            "connRows: document.querySelectorAll('#connections .intent-row').length })"
        )

        shot = OUT / "field-fast.png"
        page.screenshot(path=str(shot), full_page=False)
        ocr_text = _ocr(shot)

        page.click('nav.menu button[data-view="host-attack"]')
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / "field-host-attack.png"), full_page=False)

        browser.close()

    report = {
        "url": URL,
        "timings_ms": timings,
        "inline_bootstrap": bootstrap,
        "dom_snapshot": live,
        "ocr_snippet": ocr_text[:1200],
        "ocr_has_nexus": bool(re.search(r"NEXUS", ocr_text, re.I)),
        "ocr_has_connections": bool(re.search(r"Live connections|Outgoing|ESTAB|tcp", ocr_text, re.I)),
    }
    report_path = OUT / "field-fast-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"wrote {shot}")
    print(f"wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
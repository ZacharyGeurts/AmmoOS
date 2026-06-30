#!/usr/bin/env python3
"""Build PDF textbook volumes from docs/chapters/ via headless Chromium."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CHAPTERS = DOCS / "chapters"
PRINT = DOCS / "print"
OUT = ROOT / "pdf"
MANIFEST = DOCS / "data/image-manifest.json"
VENV_PY = ROOT / ".venv-pdf/bin/python"

# Logical volumes — each PDF stays under GitHub-friendly size (~15–40 MB).
VOLUMES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "01-foundations-ch01-04.pdf",
        "Volume 01 — Foundations (Chapters 1–4)",
        ("01-preface", "02-fields-pixels-packets", "03-thermodynamics", "04-entropy"),
    ),
    (
        "02-engine-ch05-08.pdf",
        "Volume 02 — Engine (Chapters 5–8)",
        ("05-packet-field", "06-rf-signals", "07-gpu-engine", "08-field-die"),
    ),
    (
        "03-operator-ch09-12.pdf",
        "Volume 03 — Operator (Chapters 9–12)",
        ("09-fcc-tesla", "10-spiderweb", "11-observability", "12-reality-theory"),
    ),
    (
        "04-creditors-ch13-15.pdf",
        "Volume 04 — Creditor Deep Dives (Chapters 13–15)",
        ("13-landauer-deep", "14-shannon-oracle", "15-maxwell-gpu"),
    ),
    (
        "05-sacred-ch16-18.pdf",
        "Volume 05 — Sacred Track (Chapters 16–18)",
        ("16-love-coupling", "17-god-boundary", "18-operator-covenant"),
    ),
    (
        "06-perimeter-ch19-22.pdf",
        "Volume 06 — 2026 Perimeter & Reference (Chapters 19–22)",
        ("19-sovereign-time", "20-public-services", "21-field-browser-queen", "22-glossary"),
    ),
)

PORT = 18765
BASE = f"http://127.0.0.1:{PORT}"


def chapter_keys(manifest: dict) -> list[str]:
    return sorted(manifest["chapters"].keys(), key=lambda x: int(x))


def slug_for_key(manifest: dict, key: str) -> str:
    return manifest["chapters"][key]["slug"]


def extract_main(html: str) -> str:
    m = re.search(r"<main[^>]*class=\"chapter-main[^\"]*\"[^>]*>(.*)</main>", html, re.DOTALL)
    if not m:
        return "<p>Chapter body missing.</p>"
    body = m.group(1)
    body = re.sub(r"<nav class=\"chapter-nav.*?</nav>", "", body, flags=re.DOTALL)
    return body.strip()


def chapter_heading(manifest: dict, slug: str) -> tuple[str, str]:
    for key in chapter_keys(manifest):
        ch = manifest["chapters"][key]
        if ch["slug"] == slug:
            num = int(key)
            title = ch["title"]
            return f"Chapter {num}", title
    return slug, slug


def build_volume_html(manifest: dict, volume_title: str, slugs: tuple[str, ...]) -> str:
    parts = [
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\" />",
        f"<title>{volume_title}</title>",
        '<link rel="stylesheet" href="../css/field-primer.css" />',
        '<link rel="stylesheet" href="../css/chapters.css" />',
        '<link rel="stylesheet" href="../css/print.css" />',
        '<style>body.print-volume{background:#fff;color:#1a1a1a;}</style>',
        "</head><body class=\"print-volume chapter-page\">",
        '<div class="volume-title-page">',
        "<p style=\"letter-spacing:0.12em;text-transform:uppercase;color:#8b6914\">Field Technology v5</p>",
        f"<h1>{volume_title}</h1>",
        "<p>Zachary Robert Geurts · Field Primer PDF edition</p>",
        "</div>",
    ]
    for slug in slugs:
        path = CHAPTERS / f"{slug}.html"
        html = path.read_text(encoding="utf-8")
        num, title = chapter_heading(manifest, slug)
        parts.append('<div class="chapter-break">')
        parts.append(f'<p class="chapter-num">{num}</p>')
        parts.append(f"<h1>{title}</h1>")
        parts.append(extract_main(html))
        parts.append("</div>")
    parts.append("</body></html>")
    return "\n".join(parts)


def start_server() -> ThreadingHTTPServer:
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(DOCS), **kwargs)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    import threading

    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(0.4)
    return server


def render_pdf(playwright, url: str, out_path: Path) -> None:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until="networkidle", timeout=120_000)
    page.emulate_media(media="print")
    page.pdf(
        path=str(out_path),
        format="Letter",
        print_background=True,
        margin={"top": "0.85in", "bottom": "1in", "left": "0.9in", "right": "0.9in"},
        display_header_footer=True,
        header_template="<span></span>",
        footer_template=(
            '<div style="width:100%;font-size:8px;color:#666;text-align:center;'
            'padding:0 0.5in;font-family:Georgia,serif">'
            "Field Technology v5 · Field Primer"
            "</div>"
        ),
    )
    browser.close()


def main() -> None:
    if not VENV_PY.is_file():
        print("Run: python3 -m venv .venv-pdf && .venv-pdf/bin/pip install playwright pypdf", file=sys.stderr)
        print("Then: .venv-pdf/bin/playwright install chromium", file=sys.stderr)
        sys.exit(1)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    PRINT.mkdir(parents=True, exist_ok=True)

    # Stitch volume HTML files for reliable single-pass PDF per volume.
    volume_urls: list[tuple[str, str]] = []
    for filename, title, slugs in VOLUMES:
        stem = filename.replace(".pdf", "")
        html_path = PRINT / f"{stem}.html"
        html_path.write_text(build_volume_html(manifest, title, slugs), encoding="utf-8")
        volume_urls.append((filename, f"{BASE}/print/{stem}.html"))
        print(f"stitched {html_path.name} ({len(slugs)} chapters)")

    server = start_server()

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        front_url = f"{BASE}/print/front-matter.html"
        front_out = OUT / "00-front-matter.pdf"
        print(f"rendering {front_out.name}...")
        render_pdf(p, front_url, front_out)

        for filename, url in volume_urls:
            out_path = OUT / filename
            print(f"rendering {out_path.name}...")
            render_pdf(p, url, out_path)

    server.shutdown()

    # Manifest for README
    lines = ["# Field Technology v5 — PDF Textbook\n"]
    lines.append("Generated from the web edition. Download volumes in order.\n")
    lines.append("| File | Chapters | Size |")
    lines.append("|------|----------|------|")
    total = 0
    for path in sorted(OUT.glob("*.pdf")):
        size = path.stat().st_size
        total += size
        mb = size / (1024 * 1024)
        ch = ""
        for fn, _title, slugs in VOLUMES:
            if fn == path.name:
                nums = [
                    int(k)
                    for k in chapter_keys(manifest)
                    if manifest["chapters"][k]["slug"] in slugs
                ]
                ch = f"{min(nums)}–{max(nums)}" if nums else "—"
                break
        if path.name == "00-front-matter.pdf":
            ch = "Front matter"
        lines.append(f"| [{path.name}]({path.name}) | {ch} | {mb:.1f} MB |")
    lines.append(f"\n**Total:** {total / (1024 * 1024):.1f} MB across {len(list(OUT.glob('*.pdf')))} files.\n")
    lines.append("Regenerate: `bash scripts/build-pdfs.sh`\n")
    lines.append("Web reader (vanilla paper): [Field Primer](https://zacharygeurts.github.io/Field_Primer/)\n")
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"done — {len(list(OUT.glob('*.pdf')))} PDFs in pdf/")


if __name__ == "__main__":
    main()
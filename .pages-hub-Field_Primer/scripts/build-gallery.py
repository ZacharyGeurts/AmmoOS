#!/usr/bin/env python3
"""Build docs/gallery.html from image-manifest — v5 long book figures."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/data/image-manifest.json"
OUT = ROOT / "docs/gallery.html"

GENERATED_CHAPTER_IMAGES: tuple[tuple[str, str, str], ...] = (
    ("chapters/ch01-illustration-theory.jpg", "Illustration theory", "Leonardo → Mayer density"),
    ("chapters/ch01-dual-channel.jpg", "Dual channel", "Paivio / Mayer alignment"),
    ("chapters/ch03-coupled-fabric.jpg", "Coupled fabric", "Phi · Thermo · Flow"),
    ("chapters/ch04-entropy-layers.jpg", "Entropy layers", "Three plates — never summed"),
    ("chapters/ch05-packet-perimeter.jpg", "Packet perimeter", "Defensive jsonl"),
    ("chapters/ch08-die-bus.jpg", "Die data bus", "Telemetry spine"),
    ("chapters/ch09-fcc-bus.jpg", "FCC bus slots", "Stability under load"),
    ("chapters/ch13-landauer-plate.jpg", "Landauer plate", "Thermodynamic floor"),
    ("chapters/ch14-shannon-storm.jpg", "Shannon storm", "Byte surprise gauge"),
    ("chapters/ch18-covenant-ladder.jpg", "Covenant ladder", "Operator ethics"),
    ("chapters/ch19-sovereign-time.jpg", "Sovereign time", "Seal forward · verify"),
    ("chapters/ch20-public-services.jpg", "Public services", "DNS · DHCP · NTP"),
    ("chapters/ch21-queen-browser.jpg", "Queen browser", "Hold all gates"),
    ("chapters/ch22-glossary-map.jpg", "Glossary map", "Disambiguation"),
)


def pic_card(href: str, img: str, title: str, caption: str = "") -> str:
    cap = f"<p>{html.escape(caption)}</p>" if caption else ""
    return (
        f'<a class="pic-card" href="{html.escape(href)}">'
        f'<img src="assets/images/{html.escape(img)}" alt="{html.escape(title)}" loading="lazy" />'
        f'<div class="pic-body"><h4>{html.escape(title)}</h4>{cap}</div></a>'
    )


def chapter_pic(key: str, ch: dict) -> str:
    slug = ch["slug"]
    title = f"Ch {int(key):02d}"
    cap = ch["title"].split(" — ", 1)[-1] if " — " in ch["title"] else ch["title"]
    return pic_card(f"chapters/{slug}.html", ch["image"], title, cap)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    chapters = manifest["chapters"]
    keys = sorted(chapters.keys(), key=lambda x: int(x))

    ch_cards = "\n        ".join(chapter_pic(k, chapters[k]) for k in keys)
    gen_cards = "\n        ".join(
        pic_card("chapters/01-preface.html" if "ch01" in img else "index.html", img, title, cap)
        for img, title, cap in GENERATED_CHAPTER_IMAGES
    )

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>Gallery · Field Technology v6</title>
  <meta name="description" content="22 chapters · generated mechanism figures · Queen robot brain · creditor portraits." />
  <link rel="canonical" href="https://zacharygeurts.github.io/Field_Primer/gallery.html" />
  <link rel="stylesheet" href="css/field-primer.css" />
  <link rel="stylesheet" href="css/chapters.css" />
  <link rel="stylesheet" href="css/reader.css" />
</head>
<body>
  <nav class="top"><div class="inner">
    <a class="logo" href="index.html">FIELD TECHNOLOGY <span class="v6-badge">v6</span></a>
    <ul>
      <li><a href="index.html">Home</a></li>
      <li><a href="creditors/index.html">Creditors</a></li>
      <li><a href="chapters/01-preface.html">Preface</a></li>
      <li><a href="index.html#chapters">22 Chapters</a></li>
    </ul>
  </div></nav>

  <main style="max-width:1100px;margin:0 auto;padding:3rem 2rem 4rem">
    <p class="eyebrow">Textbook of 2026 · v5 long book</p>
    <h1 style="margin-bottom:0.5rem">Gallery</h1>
    <p class="muted" style="margin-bottom:2rem">Mechanism figures, chapter heroes, creditor portraits — signaled art per Mayer density, not wallpaper.</p>

    <section>
      <h2>22 chapters — read the long book</h2>
      <div class="gallery-grid">
        {ch_cards}
      </div>
    </section>

    <section style="margin-top:3rem">
      <h2>Generated mechanism figures</h2>
      <div class="gallery-grid">
        {gen_cards}
      </div>
    </section>

    <section style="margin-top:3rem">
      <h2>Creditor portraits</h2>
      <div class="gallery-grid">
        {pic_card("creditors/maxwell.html", "v4/creditors/maxwell.jpg", "Maxwell")}
        {pic_card("creditors/landauer.html", "v4/creditors/landauer.jpg", "Landauer")}
        {pic_card("creditors/shannon.html", "v4/creditors/shannon.jpg", "Shannon")}
        {pic_card("creditors/turing.html", "v4/creditors/turing.jpg", "Turing")}
        {pic_card("creditors/tesla.html", "v4/creditors/tesla.jpg", "Tesla")}
        {pic_card("creditors/zachary-geurts.html", "v4/creditors/zachary-geurts.jpg", "Zachary Geurts")}
        {pic_card("creditors/grok.html", "v4/creditors/grok.jpg", "Grok")}
        {pic_card("creditors/love-and-god.html", "v4/creditors/love-and-god.jpg", "Love &amp; God")}
        {pic_card("creditors/index.html", "v3/science/fabric-schematic.jpg", "All tributes", "+5 more →")}
      </div>
    </section>

    <p class="muted" style="margin-top:2.5rem"><code>bash scripts/build-site.sh</code></p>
  </main>
  <footer><p>Field Technology v6 · Serious book · With love</p></footer>
  <script src="js/reader.js" defer></script>
</body>
</html>
"""
    OUT.write_text(html_out, encoding="utf-8")
    print(f"gallery.html built — {len(keys)} chapters + {len(GENERATED_CHAPTER_IMAGES)} mechanism figures")


if __name__ == "__main__":
    main()
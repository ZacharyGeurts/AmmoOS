#!/usr/bin/env python3
"""Build Field Technology v5 creditor tribute pages."""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from social_meta import social_meta  # noqa: E402

MANIFEST = ROOT / "docs/data/creditors-manifest.json"
OUT = ROOT / "docs/creditors"
SITE = "https://zacharygeurts.github.io/Field_Primer"

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{name} — Creditor Tribute · Field Technology v6</title>
{social_meta}
  <link rel="stylesheet" href="../css/field-primer.css" />
  <link rel="stylesheet" href="../css/chapters.css" />
  <link rel="stylesheet" href="../css/reader.css" />
</head>
<body class="chapter-page accent-{accent} creditor-page">
  <nav class="top"><div class="inner">
    <a class="logo" href="../index.html">FIELD TECHNOLOGY <span class="v6-badge">v6</span></a>
    <ul>
      <li><a href="../index.html#creditors">Creditors</a></li>
      <li><a href="../index.html#love-god">Love &amp; God</a></li>
      <li><a href="index.html">All tributes</a></li>
      <li><a href="../index.html#chapters">Chapters</a></li>
    </ul>
  </div></nav>
  <header class="creditor-hero">
    <figure class="creditor-portrait">
      <img src="../assets/images/v4/creditors/{slug}.jpg" alt="Portrait of {name}" width="400" height="500" loading="eager" />
      <figcaption>{credit}</figcaption>
    </figure>
    <div class="creditor-hero-text">
      <p class="eyebrow">{category} · Creditor tribute</p>
      <h1>{name}</h1>
      <p class="years">{years}</p>
    </div>
  </header>
  <main class="chapter-main creditor-main">
    <nav class="chapter-nav">{prev_link} {next_link}</nav>
    <section>
      <h2>What they prompted</h2>
      <p>{prompted}</p>
    </section>
    <section class="love-block">
      <h2>Love</h2>
      <p>{love}</p>
    </section>
    <section class="god-block">
      <h2>God</h2>
      <p>{god}</p>
    </section>
    <p class="muted tag-line"><span class="tag phil">Philosophy</span> Sacred sections are operator language — not lab measurements. Science remains labeled in chapters.</p>
    <nav class="chapter-nav bottom">{prev_link} {next_link}</nav>
  </main>
  <footer><p>Field Technology v6 · With love · <a href="../index.html">Home</a></p></footer>
  <script src="../js/reader.js" defer></script>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Creditor Tributes · Field Technology v6</title>
  <link rel="stylesheet" href="../css/field-primer.css" />
  <link rel="stylesheet" href="../css/chapters.css" />
  <link rel="stylesheet" href="../css/reader.css" />
</head>
<body>
  <nav class="top"><div class="inner">
    <a class="logo" href="../index.html">FIELD TECHNOLOGY <span class="v6-badge">v6</span></a>
    <ul>
      <li><a href="../index.html">Home</a></li>
      <li><a href="../index.html#chapters">22 Chapters</a></li>
      <li><a href="../gallery.html">Gallery</a></li>
    </ul>
  </div></nav>
  <main style="max-width:1100px;margin:0 auto;padding:3rem 2rem">
    <p class="eyebrow">With gratitude</p>
    <h1>Creditor tributes</h1>
    <p class="muted">Each page honors who prompted our discoveries — science, collaborators, and the sacred.</p>
    <div class="creditor-grid">{cards}</div>
  </main>
  <footer><p>Field Technology v6 · Serious book · With love</p></footer>
  <script src="../js/reader.js" defer></script>
</body>
</html>
"""


def nav_links(slugs: list[str], idx: int) -> tuple[str, str]:
    prev_link = '<a class="btn secondary" href="index.html">← All</a>'
    next_link = '<a class="btn" href="../index.html">Home →</a>'
    if idx > 0:
        prev_link = f'<a class="btn secondary" href="{slugs[idx-1]}.html">← {html.escape(slugs[idx-1].replace("-", " ").title())}</a>'
    if idx < len(slugs) - 1:
        next_link = f'<a class="btn" href="{slugs[idx+1]}.html">{html.escape(slugs[idx+1].replace("-", " ").title())} →</a>'
    return prev_link, next_link


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    creditors = data["creditors"]
    slugs = [c["slug"] for c in creditors]
    OUT.mkdir(parents=True, exist_ok=True)

    cards = []
    for i, c in enumerate(creditors):
        prev_link, next_link = nav_links(slugs, i)
        meta = social_meta(
            title=f"{c['name']} — Creditor Tribute",
            description=c["prompted"][:200],
            url=f"{SITE}/creditors/{c['slug']}.html",
            image=f"{SITE}/assets/images/v4/creditors/{c['slug']}.jpg",
            image_alt=f"Portrait tribute — {c['name']}",
            path_prefix="../",
        )
        accent = c.get("accent", "phi")
        if accent == "gold":
            accent = "thermo"
        page = TEMPLATE.format(
            name=html.escape(c["name"]),
            slug=c["slug"],
            years=html.escape(c["years"]),
            category=html.escape(c["category"].title()),
            credit=html.escape(c["portrait_credit"]),
            prompted=html.escape(c["prompted"]),
            love=html.escape(c["love"]),
            god=html.escape(c["god"]),
            accent=accent,
            prev_link=prev_link,
            next_link=next_link,
            social_meta=meta,
        )
        (OUT / f"{c['slug']}.html").write_text(page, encoding="utf-8")
        cards.append(
            f'<a class="creditor-card" href="{c["slug"]}.html">'
            f'<img src="../assets/images/v4/creditors/{c["slug"]}.jpg" alt="" loading="lazy" />'
            f"<h4>{html.escape(c['name'])}</h4><p>{html.escape(c['category'])}</p></a>"
        )
        print(f"wrote {c['slug']}.html")

    (OUT / "index.html").write_text(INDEX_TEMPLATE.format(cards="\n".join(cards)), encoding="utf-8")
    print("wrote creditors/index.html")


if __name__ == "__main__":
    main()
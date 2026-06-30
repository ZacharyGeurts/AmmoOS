#!/usr/bin/env python3
"""Build Field Technology v5 chapter HTML."""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
CONTENT = Path(__file__).resolve().parents[1] / "content" / "chapters"
from chapter_bookends import inject_bookends  # noqa: E402
from chapter_signposting import inject_signposting  # noqa: E402
from editorial_front_matter import inject_editorial_front_matter, replace_reading_spine  # noqa: E402
from illustration_theory_section import inject_illustration_theory  # noqa: E402
from inject_figures import inject_figures  # noqa: E402
from master_rocks_table import inject_master_rocks  # noqa: E402
from technical_anchors import inject_technical_anchors  # noqa: E402
from tighten_sacred import tighten_sacred  # noqa: E402
from social_meta import chapter_meta  # noqa: E402

MANIFEST = ROOT / "docs/data/image-manifest.json"
OUT = ROOT / "docs/chapters"

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>{num} — {title} · Field Technology v6</title>
{social_meta}
  <link rel="stylesheet" href="../css/field-primer.css" />
  <link rel="stylesheet" href="../css/chapters.css" />
  <link rel="stylesheet" href="../css/reader.css" />
</head>
<body class="chapter-page accent-{accent}">
  <nav class="top"><div class="inner">
    <a class="logo" href="../index.html">FIELD TECHNOLOGY <span class="v6-badge">v6</span></a>
    <ul>
      <li><a href="../creditors/index.html">Creditors</a></li>
      <li><a href="../index.html#love-god">Love &amp; God</a></li>
      <li><a href="../index.html#chapters">Chapters</a></li>
      <li><a href="https://github.com/ZacharyGeurts/Field_Primer/wiki/{wiki}">Wiki</a></li>
    </ul>
  </div></nav>
  <header class="chapter-hero" style="background-image:url('../assets/images/{image}')">
    <div class="chapter-hero-overlay"></div>
    <div class="chapter-hero-content">
      <p class="eyebrow">Chapter {num} · Field Technology v6</p>
      <h1>{title}</h1>
      {subtitle}
    </div>
  </header>
  <main class="chapter-main{preface_class}">
    <nav class="chapter-nav">{prev_link} {next_link}</nav>
    {body}
    <nav class="chapter-nav bottom">{prev_link} {next_link}</nav>
  </main>
  <footer><p>Field Technology v6 · Serious book · We do not hide the rocks.</p></footer>
  <script src="../js/reader.js" defer></script>
</body>
</html>
"""


def chapter_keys(manifest: dict) -> list[str]:
    return sorted(manifest["chapters"].keys(), key=lambda x: int(x))


def nav_link(num: int, keys: list[str], manifest: dict, direction: str) -> str:
    key = str(num).zfill(2)
    idx = keys.index(key)
    if direction == "prev":
        if idx <= 0:
            return '<a class="btn secondary" href="../index.html">← Home</a>'
        prev_key = keys[idx - 1]
        ch = manifest["chapters"][prev_key]
        return f'<a class="btn secondary" href="{ch["slug"]}.html">← Ch {int(prev_key)}</a>'
    if idx >= len(keys) - 1:
        return '<a class="btn" href="../creditors/love-and-god.html">Love &amp; God →</a>'
    nxt_key = keys[idx + 1]
    ch = manifest["chapters"][nxt_key]
    return f'<a class="btn" href="{ch["slug"]}.html">Ch {int(nxt_key)} →</a>'


def load_body(key: str, slug: str) -> str:
    for name in (f"{key}.html", f"{key}-{slug}.html", f"{slug}.html"):
        path = CONTENT / name
        if path.is_file():
            return path.read_text(encoding="utf-8")
    return "<p>Chapter body missing — write content/chapters/" + key + ".html</p>"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    keys = chapter_keys(manifest)
    OUT.mkdir(parents=True, exist_ok=True)
    for key in keys:
        ch = manifest["chapters"][key]
        num = int(key)
        body = load_body(key, ch["slug"])
        body = inject_editorial_front_matter(body, key)
        body = replace_reading_spine(body, key)
        body = tighten_sacred(body, key)
        body = inject_illustration_theory(body, key)
        body = inject_bookends(body, key, ch["image"], ch.get("alt", ch["title"]))
        body = inject_signposting(body, key)
        body = inject_figures(body, key)
        body = inject_master_rocks(body, key)
        body = inject_technical_anchors(body, key)
        prev_link = nav_link(num, keys, manifest, "prev")
        next_link = nav_link(num, keys, manifest, "next")
        meta = chapter_meta(
            num,
            ch["title"],
            ch["slug"],
            ch["image"],
            ch.get("alt", ch["title"]),
        )
        subtitle = ""
        if ch.get("subtitle"):
            subtitle = f'<p class="lead" style="margin-top:0.75rem">{html.escape(ch["subtitle"])}</p>'
        preface_class = " preface-full" if num == 1 else ""
        html_out = TEMPLATE.format(
            num=num,
            title=html.escape(ch["title"]),
            accent=ch["accent"],
            wiki=ch["wiki"],
            image=ch["image"],
            body=body,
            prev_link=prev_link,
            next_link=next_link,
            social_meta=meta,
            subtitle=subtitle,
            preface_class=preface_class,
        )
        (OUT / f"{ch['slug']}.html").write_text(html_out, encoding="utf-8")
        print(f"wrote {ch['slug']}.html")
    print("done")


if __name__ == "__main__":
    main()
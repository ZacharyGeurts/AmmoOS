#!/usr/bin/env pythong
"""Patch all manual HTML: v7 assets, search, layout, Concepts nav."""
from __future__ import annotations
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
ASSETS = """  <script src="manual-theme.js?v=7"></script>
  <script src="manual-search.js?v=7"></script>
  <script src="manual-layout.js?v=7"></script>
  <link rel="stylesheet" href="manual.css?v=7" />"""

OLD_ASSETS = re.compile(
    r"  <script src=\"manual-theme\.js\?v=\d+\"></script>\s*"
    r"(?:  <script src=\"manual-search\.js\?v=\d+\"></script>\s*)?"
    r"(?:  <script src=\"manual-layout\.js\?v=\d+\"></script>\s*)?"
    r"  <link rel=\"stylesheet\" href=\"manual\.css\?v=\d+\" />"
)

CONCEPTS_LINK = '      <a href="concepts.html">Concepts</a>\n'

for path in sorted(ROOT.glob("*.html")):
    text = path.read_text(encoding="utf-8")
    text = OLD_ASSETS.sub(ASSETS, text, count=1)
    if 'href="concepts.html"' not in text:
        text = text.replace(
            '      <a href="index.html">Index</a>\n',
            '      <a href="index.html">Index</a>\n' + CONCEPTS_LINK,
            1,
        )
    path.write_text(text, encoding="utf-8")
    print("patched", path.name)
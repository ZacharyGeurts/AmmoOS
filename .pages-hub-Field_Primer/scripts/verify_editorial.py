#!/usr/bin/env python3
"""Verify editorial pass completeness on built chapters."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "docs/chapters"

BOILERPLATE = re.compile(
    r"Pedagogy for «|Synthesis question for «|Workshop exercise \d+:",
)


def main() -> None:
    files = sorted(CHAPTERS.glob("*.html"))
    if len(files) != 22:
        raise SystemExit(f"expected 22 chapters, found {len(files)}")
    missing_toc: list[str] = []
    missing_anchor: list[str] = []
    boilerplate_hits: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if 'class="chapter-toc"' not in text:
            missing_toc.append(path.name)
        if 'class="evidence-anchor"' not in text:
            missing_anchor.append(path.name)
        if BOILERPLATE.search(text):
            boilerplate_hits.append(path.name)
    if missing_toc:
        raise SystemExit(f"missing chapter-toc: {', '.join(missing_toc)}")
    if missing_anchor:
        raise SystemExit(f"missing evidence-anchor: {', '.join(missing_anchor)}")
    if boilerplate_hits:
        raise SystemExit(f"boilerplate remains: {', '.join(boilerplate_hits)}")
    print("editorial verify ok — 22 chapters, TOC + anchors, no boilerplate")


if __name__ == "__main__":
    main()
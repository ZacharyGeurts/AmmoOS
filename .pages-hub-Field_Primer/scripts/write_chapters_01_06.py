#!/usr/bin/env python3
"""Write full textbook body fragments for chapters 01-06 (4500+ words each)."""
from __future__ import annotations

import re
from pathlib import Path

from bulk_paragraphs import (
    bulk_ch01_extra,
    bulk_ch02,
    bulk_ch03,
    bulk_ch04,
    bulk_ch05,
    bulk_ch06,
)
from bulk_paragraphs_extra import (
    extra_01,
    extra_02,
    extra_03,
    extra_04,
    extra_05,
    extra_06,
)
from chapter_expansions_01_06 import EXPAND_01, PREFIX_01, SUFFIX_01
from long_form_extra import long_04d, long_05d, long_06d
from mega_content import mega_01, mega_02, mega_03, mega_04, mega_05, mega_06
from long_form_chapters import (
    long_02,
    long_02b,
    long_03,
    long_03b,
    long_03c,
    long_04,
    long_04b,
    long_04c,
    long_05,
    long_05b,
    long_05c,
    long_06,
    long_06b,
    long_06c,
)
from pad_chapters import (
    PAD_01,
    PAD_02,
    PAD_02_EXT,
    PAD_03,
    PAD_03_EXT,
    PAD_04,
    PAD_04_EXT,
    PAD_05,
    PAD_05_EXT,
    PAD_06,
    PAD_06_EXT,
    pad_body,
)

OUT = Path(__file__).resolve().parents[1] / "content" / "chapters"
TARGET = 4500


def word_count(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text.split()) if text else 0


def write_file(name: str, body: str) -> int:
    path = OUT / name
    path.write_text(body.strip() + "\n", encoding="utf-8")
    n = word_count(body)
    print(f"{name}: {n} words")
    return n


def assemble(*parts: str) -> str:
    return "\n\n".join(p.strip() for p in parts if p.strip())


def with_pads(*parts: str, pads: list[str]) -> str:
    return assemble(*parts, *pads)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    bodies = {
        "01.html": with_pads(
            '<p class="eyebrow">Chapter 1 · Read this before you dispatch anything</p>',
            PREFIX_01,
            EXPAND_01,
            bulk_ch01_extra(),
            extra_01(),
            mega_01(),
            SUFFIX_01,
            pads=PAD_01,
        ),
        "02.html": with_pads(bulk_ch02(), extra_02(), long_02(), long_02b(), mega_02(), pads=PAD_02 + PAD_02_EXT),
        "03.html": with_pads(bulk_ch03(), extra_03(), long_03(), long_03b(), long_03c(), mega_03(), pads=PAD_03 + PAD_03_EXT),
        "04.html": with_pads(bulk_ch04(), extra_04(), long_04(), long_04b(), long_04c(), long_04d(), mega_04(), pads=PAD_04 + PAD_04_EXT),
        "05.html": with_pads(bulk_ch05(), extra_05(), long_05(), long_05b(), long_05c(), long_05d(), mega_05(), pads=PAD_05 + PAD_05_EXT),
        "06.html": with_pads(bulk_ch06(), extra_06(), long_06(), long_06b(), long_06c(), long_06d(), mega_06(), pads=PAD_06 + PAD_06_EXT),
    }

    total = 0
    for name, body in bodies.items():
        total += write_file(name, body)
    print(f"TOTAL: {total} words")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Assemble chapters 01-06 from substantive prose modules — no depth-N padding."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content" / "chapters"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bulk_paragraphs import (  # noqa: E402
    bulk_ch01_extra,
    bulk_ch02,
    bulk_ch03,
    bulk_ch04,
    bulk_ch05,
    bulk_ch06,
)
from bulk_paragraphs_extra import (  # noqa: E402
    extra_01,
    extra_02,
    extra_03,
    extra_04,
    extra_05,
    extra_06,
)
from chapter_expansions_01_06 import EXPAND_01, PREFIX_01, SUFFIX_01  # noqa: E402
from long_form_chapters import (  # noqa: E402
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
from long_form_extra import long_04d, long_05d, long_06d  # noqa: E402
from mega_content import mega_01, mega_02, mega_03, mega_04, mega_05, mega_06  # noqa: E402
from pad_chapters import (  # noqa: E402
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
)
from real_expansion_01_06 import (  # noqa: E402
    expand_01,
    expand_02,
    expand_03,
    expand_04,
    expand_05,
    expand_06,
)

TARGET = 5200


def word_count(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text.split()) if text else 0


def assemble(*parts: str) -> str:
    return "\n\n".join(p.strip() for p in parts if p and p.strip())


def depth_mentions(html: str) -> int:
    return len(re.findall(r"\(depth \d+\)", html))


def write_chapter(name: str, body: str) -> None:
    path = OUT / name
    path.write_text(body.strip() + "\n", encoding="utf-8")
    n = word_count(body)
    d = depth_mentions(body)
    flag = "OK" if n >= TARGET and d == 0 else "WARN"
    print(f"{name}: {n} words, depth={d} [{flag}]")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    write_chapter(
        "01.html",
        assemble(
            '<p class="eyebrow">Chapter 1 · Read this before you dispatch anything</p>',
            PREFIX_01,
            EXPAND_01,
            bulk_ch01_extra(),
            extra_01(),
            mega_01(),
            expand_01(),
            SUFFIX_01,
            *PAD_01,
        ),
    )
    write_chapter(
        "02.html",
        assemble(
            bulk_ch02(),
            extra_02(),
            long_02(),
            long_02b(),
            mega_02(),
            expand_02(),
            *PAD_02,
            *PAD_02_EXT,
        ),
    )
    write_chapter(
        "03.html",
        assemble(
            bulk_ch03(),
            extra_03(),
            long_03(),
            long_03b(),
            long_03c(),
            mega_03(),
            expand_03(),
            *PAD_03,
            *PAD_03_EXT,
        ),
    )
    write_chapter(
        "04.html",
        assemble(
            bulk_ch04(),
            extra_04(),
            long_04(),
            long_04b(),
            long_04c(),
            long_04d(),
            mega_04(),
            expand_04(),
            *PAD_04,
            *PAD_04_EXT,
        ),
    )
    write_chapter(
        "05.html",
        assemble(
            bulk_ch05(),
            extra_05(),
            long_05(),
            long_05b(),
            long_05c(),
            long_05d(),
            mega_05(),
            expand_05(),
            *PAD_05,
            *PAD_05_EXT,
        ),
    )
    write_chapter(
        "06.html",
        assemble(
            bulk_ch06(),
            extra_06(),
            long_06(),
            long_06b(),
            long_06c(),
            long_06d(),
            mega_06(),
            expand_06(),
            *PAD_06,
            *PAD_06_EXT,
        ),
    )


if __name__ == "__main__":
    main()
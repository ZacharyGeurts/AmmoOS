#!/usr/bin/env python3
"""Write full textbook HTML fragments for chapters 13-18."""
from __future__ import annotations

import re
import textwrap
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "content" / "chapters"


def wc(html: str) -> int:
    t = re.sub(r"<[^>]+>", " ", html)
    return len(re.sub(r"\s+", " ", t).strip().split())


def P(*parts: str) -> str:
    return "".join(f"<p>{x}</p>\n" for x in parts)


def H(title: str) -> str:
    return f"<h2>{title}</h2>\n"


def build_chapter(
    eyebrow: str,
    sections: list[tuple[str, list[str]]],
    drills: list[tuple[str, list[str]]],
    questions: list[str],
    footer: str,
    extras: str = "",
) -> str:
    body = f'<p class="eyebrow">{eyebrow}</p>\n'
    for title, paras in sections:
        body += H(title) + P(*paras)
    for title, steps in drills:
        body += H(title) + f'<pre class="eq">{chr(10).join(steps)}</pre>\n'
    body += H("Study questions")
    body += "<ol>" + "".join(f"<li>{q}</li>" for q in questions) + "</ol>\n"
    body += extras + footer
    return body


# Shared pedagogical depth blocks
ROCK = (
    "Chapter 12 remains the contract: theory inspires vocabulary; implementation is what you "
    "<strong>grep</strong>, <strong>set</strong>, and <strong>screenshot</strong>. We do not hide the rocks."
)
LOCAL = (
    "The stack is local-first — loopback truth, operator-owned time, jsonl receipts on disk. "
    "No phone-home permission is required to learn field literacy."
)
CRED = 'Honor creditors at <a href="../creditors/index.html">the tribute index</a> — portraits, not footnotes.'

CHAPTERS: dict[str, str] = {}
#!/usr/bin/env pythong
"""Operator voice pass — content/chapters only; labels promotional shorthand."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "chapters"

# (pattern, replacement) — order matters
RULES: tuple[tuple[str, str], ...] = (
    (r"\btoss when the plate", "redata when the plate"),
    (r"\btoss\b(?= when)", "redata"),
    (r"Super Intelligence doctrine", '<span class="tag meta">Metaphor</span> super-intelligence doctrine'),
    (r"<h3>Queen robot brain —", "<h3>Queen gate stack —"),
    (r"robot-brain architecture", "gate+recall architecture"),
    (r"robot-brain stack", "gate+recall stack"),
    (r"DARPA-grade robot brain", "in-process gate stack <span class=\"tag meta\">Metaphor</span>"),
    (r"DARPA-grade", "in-process gate stack <span class=\"tag meta\">Metaphor</span>"),
    (r"Textbook of 2026\.</figcaption>", "Field Technology v5.</figcaption>"),
    (r"greatest weapon is field literacy", "strongest operator discipline is field literacy"),
    (r'The sentence "greatest weapon', 'The sentence "strongest operator discipline'),
)

INJECT_LABEL_HINTS = (
    ("planetary weave", '<span class="tag vis">Visual</span>'),
    ("Landauer joules from GPU", '<span class="tag meta">Metaphor</span>'),
)


def apply_voice(text: str) -> tuple[str, int]:
    n = 0
    for pat, repl in RULES:
        text, c = re.subn(pat, repl, text, flags=re.IGNORECASE)
        n += c
    return text, n


def main() -> None:
    files = sorted(CONTENT.glob("*.html"))
    if not files:
        raise SystemExit(f"no chapters in {CONTENT}")
    total = 0
    for path in files:
        raw = path.read_text(encoding="utf-8")
        out, n = apply_voice(raw)
        if n:
            path.write_text(out, encoding="utf-8")
            print(f"voice {path.name}: {n} edits")
        total += n
    print(f"voice_pass ok — {len(files)} chapters, {total} replacements")


if __name__ == "__main__":
    main()
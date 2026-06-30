"""Inject Mayer segment wrappers and labels into chapter bodies."""

from __future__ import annotations

import re

from mayer_segment_toolkit import wrap_segment, word_count

# Chapters with hand-authored mayer-segment markup in content/
HAND_AUTHORED = frozenset({f"{i:02d}" for i in range(1, 23)})

SKIP_H2 = frozenset({
    "learning objectives",
    "study questions",
    "chapter summary",
    "on the way",
    "reading companion",
    "operator journal",
    "chapter closing",
})


def _should_skip_h2(title: str) -> bool:
    t = title.lower().strip()
    return any(s in t for s in SKIP_H2)


def auto_segment_body(body: str, key: str) -> str:
    """Group h2 blocks into ~1000–1200 word Mayer segments (fallback chapters)."""
    if 'class="mayer-segment"' in body:
        return body
    chunks = re.split(r"(?=<h2)", body, flags=re.I)
    preamble = chunks[0] if chunks and not chunks[0].lstrip().startswith("<h2") else ""
    h2_blocks = [c for c in chunks if c.lstrip().startswith("<h2")]
    if not h2_blocks:
        return body

    segments: list[str] = []
    buf: list[str] = []
    buf_words = 0
    seg_n = 0

    def flush() -> None:
        nonlocal seg_n, buf, buf_words
        if not buf:
            return
        seg_n += 1
        inner = "".join(buf)
        first_h2 = re.search(r"<h2[^>]*>(.*?)</h2>", inner, re.I | re.S)
        sid = re.sub(r"[^a-z0-9]+", "-", (first_h2.group(1) if first_h2 else f"seg-{seg_n}").lower())[:48].strip("-")
        segments.append(wrap_segment(key, seg_n, sid or f"seg-{seg_n}", inner))
        buf = []
        buf_words = 0

    for block in h2_blocks:
        m = re.match(r"<h2[^>]*>(.*?)</h2>", block, re.I | re.S)
        title = re.sub(r"<[^>]+>", "", m.group(1)) if m else ""
        if _should_skip_h2(title):
            flush()
            segments.append(block)
            continue
        w = word_count(block)
        if buf_words + w > 1250 and buf:
            flush()
        buf.append(block)
        buf_words += w
    flush()
    return preamble + "\n".join(segments)


def inject_mayer_segments(body: str, key: str) -> str:
    if key in HAND_AUTHORED or 'class="mayer-segment"' in body:
        return body
    return auto_segment_body(body, key)
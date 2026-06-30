"""Mayer segment toolkit — Field Technology v5 textbook standard.

Each teaching beat: 900–1200 words + one signaled figure (Leonardo → Mayer, Ch 1).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

WORDS_MIN = 900
WORDS_TARGET = (1000, 1200)
WORDS_MAX = 1350
FIGURE_RE = re.compile(r'<figure\s+class="figure"', re.I)
GROK_RE = re.compile(r'class="professor-grok"', re.I)
CITATIONS_RE = re.compile(r'class="segment-citations"', re.I)
H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class SegmentReport:
    chapter: str
    index: int
    words: int
    has_figure: bool
    has_grok: bool
    has_citations: bool
    title: str
    ok: bool
    notes: list[str]


def strip_html(html: str) -> str:
    text = TAG_RE.sub(" ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def word_count(html: str) -> int:
    return len(strip_html(html).split()) if strip_html(html) else 0


def extract_mayer_segments(body: str) -> list[tuple[str, str]]:
    """Return (title, inner_html) for each <section class=\"mayer-segment\">."""
    parts: list[tuple[str, str]] = []
    pattern = re.compile(
        r'<section\s+class="mayer-segment"[^>]*data-segment="([^"]*)"[^>]*>'
        r"(.*?)</section>",
        re.I | re.S,
    )
    for m in pattern.finditer(body):
        inner = m.group(2)
        title_m = H2_RE.search(inner)
        title = strip_html(title_m.group(1)) if title_m else m.group(1)
        parts.append((title, inner))
    return parts


def segment_header(ch: str, n: int, words: int, title: str) -> str:
    return (
        f'<p class="mayer-segment-label">Segment {ch}.{n} · ~{words:,} words · '
        f"Textbook beat · 1 figure</p>"
    )


def validate_chapter(body: str, chapter_key: str) -> list[SegmentReport]:
    segments = extract_mayer_segments(body)
    reports: list[SegmentReport] = []
    if not segments:
        return [
            SegmentReport(
                chapter_key, 0, word_count(body), bool(FIGURE_RE.search(body)),
                False, False, "(whole chapter)", False, ["no mayer-segment sections"],
            )
        ]
    for i, (title, inner) in enumerate(segments, start=1):
        wc = word_count(inner)
        fig = bool(FIGURE_RE.search(inner))
        grok = bool(GROK_RE.search(inner))
        cites = bool(CITATIONS_RE.search(inner))
        notes: list[str] = []
        if wc < WORDS_MIN:
            notes.append(f"under {WORDS_MIN} words ({wc})")
        if wc > WORDS_MAX:
            notes.append(f"over {WORDS_MAX} words ({wc}) — split segment")
        if not fig:
            notes.append("missing signaled figure")
        if not grok:
            notes.append("missing Professor Grok summary")
        if not cites:
            notes.append("missing segment citations")
        ok = WORDS_MIN <= wc <= WORDS_MAX and fig and grok and cites
        reports.append(
            SegmentReport(chapter_key, i, wc, fig, grok, cites, title, ok, notes)
        )
    return reports


def wrap_segment(ch: str, n: int, segment_id: str, inner: str) -> str:
    wc = word_count(inner)
    label = segment_header(ch, n, wc, segment_id)
    if 'class="mayer-segment-label"' not in inner:
        inner = label + "\n" + inner
    return (
        f'<section class="mayer-segment" data-segment="{segment_id}" '
        f'data-words="{wc}" id="seg-{ch}-{n}">\n{inner}\n</section>'
    )
"""Inject scannable In-this-chapter TOC from h2 headings."""

from __future__ import annotations

import html
import re

_STRIP = re.compile(r"<[^>]+>")


def _plain(h: str) -> str:
    return html.escape(_STRIP.sub("", h).strip())


def inject_signposting(body: str, chapter_key: str) -> str:
    if 'class="chapter-toc"' in body:
        return body
    headings = re.findall(r"<h2[^>]*>(.*?)</h2>", body, flags=re.DOTALL | re.IGNORECASE)
    skip = {
        "learning objectives",
        "on the way — what you will learn",
        "in this chapter",
        "evidence anchor — grep and sources",
        "chapter summary — before you turn the page",
    }
    items: list[str] = []
    for raw in headings:
        text = _plain(raw).lower()
        if not text or text in skip:
            continue
        anchor = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48]
        label = _plain(raw)
        items.append(f'<li><a href="#toc-{chapter_key}-{anchor}">{label}</a></li>')
        if len(items) >= 14:
            break
    if len(items) < 4:
        return body

    # Add id anchors to first matching h2s
    out = body
    for raw in headings:
        label = _plain(raw)
        if not label:
            continue
        anchor = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")[:48]
        aid = f'id="toc-{chapter_key}-{anchor}"'
        if aid in out:
            continue
        old = f"<h2>{raw}</h2>"
        new = f'<h2 {aid}>{raw}</h2>'
        if old in out:
            out = out.replace(old, new, 1)

    toc = (
        '<nav class="chapter-toc" aria-label="In this chapter">'
        "<h2>In this chapter</h2><ol>"
        + "".join(items)
        + "</ol></nav>"
    )

    for needle in ('</div>\n\n<div class="on-the-way">', 'class="on-the-way">'):
        idx = out.find(needle)
        if idx != -1:
            close = out.find("</div>", idx)
            if close != -1:
                insert = close + len("</div>")
                return out[:insert] + "\n" + toc + out[insert:]

    obj = out.find('class="objectives"')
    if obj != -1:
        close = out.find("</div>", obj)
        if close != -1:
            insert = close + len("</div>")
            return out[:insert] + "\n" + toc + out[insert:]

    eyebrow = out.find("</p>")
    if eyebrow != -1:
        return out[: eyebrow + 4] + "\n" + toc + out[eyebrow + 4 :]
    return toc + out
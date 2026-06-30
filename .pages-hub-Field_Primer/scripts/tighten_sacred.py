"""Remove per-section boilerplate from chapters 13–18; one workshop block each."""

from __future__ import annotations

import re

BOILERPLATE = re.compile(
    r"<p>(?:Pedagogy for «[^»]+»:|Workshop exercise \d+:|Synthesis question for «[^»]+»:|"
    r"Field note \d+ on [^:<]+:|Lab pairing for «[^»]+»:|Citation drill:)[^<]*</p>\s*",
    re.DOTALL,
)

SACRED_WORKSHOP = """
<div class="sacred-workshop">
<h2>Sacred track workshop — complete once</h2>
<p><span class="tag phil">Philosophy track.</span> These exercises apply to Chapters 16–18 collectively — not once per section above.</p>
<ol>
<li><strong>Memo:</strong> Two pages — one <a href="../creditors/index.html">creditor tribute</a> cited, one <code>grep</code> command proving an <span class="tag impl">Implemented</span> claim from this chapter.</li>
<li><strong>Pair drill:</strong> Matched 90-second sessions; diff THERMO or jsonl; resolve disputes with headers, not vibes.</li>
<li><strong>Status email:</strong> Three sentences to management — one Implemented, one Metaphor, one Philosophy (Chapter 12 labels).</li>
<li><strong>Journal entry:</strong> Date, git hash, three log lines, one surprise, one honesty label. Bring to Chapter 18 audit.</li>
</ol>
</div>
"""

CREDITOR_WORKSHOP = """
<div class="creditor-workshop">
<h2>Creditor deep-dive workshop — complete once</h2>
<p>Chapters 13–15 share one drill set — complete after reading all three creditor chapters.</p>
<ol>
<li><strong>Primary source:</strong> Footnote one Landauer, Shannon, or Maxwell paper (not Wikipedia alone).</li>
<li><strong>Grep proof:</strong> One <code>grep</code> command tying this chapter's equation to an <span class="tag impl">Implemented</span> or <span class="tag meta">Metaphor</span> label from Chapter 12.</li>
<li><strong>Layer separation:</strong> Write three sentences — GPU proxy, file oracle, theory — never summed into one entropy number.</li>
<li><strong>Comparative run:</strong> Two matched sessions; plot <code>entropyThisFrame</code> or file H trend — comparative only, no joule billing.</li>
</ol>
</div>
"""

COVENANT_WORKSHOP = """
<div class="covenant-workshop">
<h2>Operator covenant workshop — complete once</h2>
<ol>
<li><strong>Clause audit:</strong> Recite six covenant clauses from memory; map each to one grep habit.</li>
<li><strong>Rock recitation:</strong> Five rows from Chapter 12 honesty table without looking.</li>
<li><strong>Monday grep:</strong> Before any Friday demo, run week-zero drill from Chapter 1 — archive run.log.</li>
<li><strong>Sign in spirit:</strong> One paragraph operator journal — which clause you broke last month and how you fixed it.</li>
</ol>
</div>
"""

TIGHTEN_KEYS: dict[str, str] = {
    "13": "creditor",
    "14": "creditor",
    "15": "creditor",
    "16": "sacred",
    "17": "sacred",
    "18": "covenant",
}

WORKSHOPS = {
    "creditor": CREDITOR_WORKSHOP,
    "sacred": SACRED_WORKSHOP,
    "covenant": COVENANT_WORKSHOP,
}


def _insert_workshop(cleaned: str, workshop: str) -> str:
    if "creditor-workshop" in cleaned or "sacred-workshop" in cleaned or "covenant-workshop" in cleaned:
        return cleaned
    for marker in (
        "<h2>Operator journal",
        "<h2>Chapter closing",
        "<h2>Chapter summary",
        '<div class="chapter-summary-box">',
    ):
        if marker in cleaned:
            return cleaned.replace(marker, workshop + "\n" + marker, 1)
    return cleaned + workshop


def tighten_sacred(body: str, chapter_key: str) -> str:
    kind = TIGHTEN_KEYS.get(chapter_key)
    if not kind:
        return body
    cleaned = BOILERPLATE.sub("", body)
    return _insert_workshop(cleaned, WORKSHOPS[kind])
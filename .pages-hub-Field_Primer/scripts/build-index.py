#!/usr/bin/env python3
"""Sync docs/index.html chapter grid and copy with image-manifest + long book."""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from master_rocks_table import master_rocks_index_rows  # noqa: E402
from social_meta import social_meta  # noqa: E402

INDEX = ROOT / "docs/index.html"
MANIFEST = ROOT / "docs/data/image-manifest.json"
MARKER_START = "  <!-- social-meta -->"
MARKER_END = "  <!-- /social-meta -->"
GRID_START = "      <!-- chapter-grid -->"
GRID_END = "      <!-- /chapter-grid -->"

CHAPTER_BLURBS: dict[str, str] = {
    "01": "Start here · illustration theory",
    "19": "SQUIDGIE · terror-threat posture",
    "20": "DNS · DHCP · NTP",
    "21": "Queen gates · Hostess 7 doctrine",
    "22": "Glossary · master rocks table",
}


def chapter_keys(manifest: dict) -> list[str]:
    return sorted(manifest["chapters"].keys(), key=lambda x: int(x))


def chapter_card(key: str, ch: dict) -> str:
    num = int(key)
    slug = ch["slug"]
    title = html.escape(ch["title"])
    img = html.escape(ch["image"])
    alt = html.escape(ch.get("alt", ""))
    blurb = CHAPTER_BLURBS.get(key, "")
    short = title.split(" — ", 1)[-1] if " — " in title else title
    if len(short) > 42:
        short = short[:39] + "…"
    p = f'<p>{html.escape(blurb)}</p>' if blurb else ""
    return (
        f'<a class="chapter-card" href="chapters/{slug}.html?reader=1">'
        f'<img class="thumb" src="assets/images/{img}" alt="{alt}" loading="lazy" />'
        f'<span class="num">{num:02d}</span><h4>{short}</h4>{p}</a>'
    )


def build_chapter_grid(manifest: dict) -> str:
    lines = [GRID_START]
    for key in chapter_keys(manifest):
        lines.append("        " + chapter_card(key, manifest["chapters"][key]))
    lines.append("      " + GRID_END)
    return "\n".join(lines)


READER_CSS = '  <link rel="stylesheet" href="css/reader.css" />'
READER_JS = '  <script src="js/reader.js" defer></script>'


def patch_reader_assets(text: str) -> str:
    if 'href="css/reader.css"' not in text:
        text = text.replace(
            '  <link rel="stylesheet" href="css/chapters.css" />',
            '  <link rel="stylesheet" href="css/chapters.css" />\n' + READER_CSS,
            1,
        )
    if 'src="js/reader.js"' not in text:
        text = text.replace("</body>", READER_JS + "\n</body>", 1)
    return text


def patch_reader_cta(text: str) -> str:
    pairs = (
        ('href="chapters/01-preface.html">Start Chapter 1', 'href="chapters/01-preface.html?reader=1">Start Chapter 1'),
        ('href="chapters/01-preface.html" class="btn">Read Chapter 1', 'href="chapters/01-preface.html?reader=1" class="btn">Read Chapter 1'),
    )
    for old, new in pairs:
        if old in text and new not in text:
            text = text.replace(old, new)
    return text


def patch_about_copy(text: str) -> str:
    """Index about section — honest operator-textbook positioning."""
    about_block = """          <p>
            v6 is a <strong>manuscript-grade operator textbook</strong> — full sentences, drills, honesty labels —
            updated for the 2026 stack: NEXUS host desktop, Grok16 2.0 single fabric, Ironclad depth fields sealed and destroyed,
            DNS egress integrity, and Queen browser gates. Chapter 1 locks thesis and the operator map;
            Chapter 12 and the <a href="chapters/22-glossary.html#master-rocks">master rocks table</a> label every claim
            <span class="tag impl">Implemented</span>, <span class="tag meta">Metaphor</span>, <span class="tag phil">Philosophy</span>, or <span class="tag vis">Visual</span>.
            The engineering spine (Chapters 2–12, 19–21) stands alone; Love, God, and creditor tributes (16–18) are a
            <em>bracketed philosophical track</em> — optional, labeled, never smuggled into thermodynamic proofs.
          </p>
          <p>
            You will learn how AMOURANTHRTX treats GPU texels as addressable state, how NEXUS turns sockets into
            readable perimeter with gatekeeper IFF, how <strong>Grok16 <code>belt_2_0</code></strong> dispatches single-fabric knowing,
            how Queen holds browser gates when <code>QUEEN_READY</code> without amputating the web,
            and how KILROY seals Field Die discipline at the kernel boundary. Creditor pages honor Maxwell, Landauer, Shannon,
            Bennett, Khronos, Hostess 7, and the builders who got us here. Illustration follows Mayer density (~1 figure / 1,000 words).
            You will also learn what we <em>cannot</em> measure — proxy entropy is not joules; SDF plates are not fMRI — and we say so in place.
          </p>
          <p>
            Read Chapter 1 for thesis, operator map, and validation table. Read Chapter 12 before you treat a shader as a spectrum analyzer.
            Read Chapters 19–21 for sovereign time, public services, and Queen. Skip 16–18 if you want engineering only.
          </p>"""
    text = re.sub(
        r'<section id="about".*?</section>',
        f'<section id="about" class="v3-launch">\n      <div class="v3-launch-inner">\n        <div class="v3-copy">\n          <p class="eyebrow">What v6 is</p>\n          <h2>An operator textbook you can actually read</h2>\n{about_block}\n        </div>\n        <figure class="v3-covers">\n          <img src="assets/images/fabric-triple.jpg" alt="Phi Thermo Flow" loading="lazy" />\n          <img src="assets/images/field-die.jpg" alt="Field Die" loading="lazy" />\n        </figure>\n      </div>\n    </section>',
        text,
        count=1,
        flags=re.DOTALL,
    )
    return text


def patch_hero_lead(text: str) -> str:
    lead = (
        "<strong>Twenty-two chapters of operator prose</strong> — v6 stack update, honesty-labeled, grep-first. "
        "Engineering core on Phi, Thermo, Flow, Field Die, packet field, Grok16 2.0 single fabric, "
        "NEXUS host desktop, Queen, and sovereign time. "
        "Sacred chapters (16–18) and expanded creditor tributes sit beside the math — bracketed, not mixed into proofs. "
        "The rocks stay visible."
    )
    text = re.sub(
        r'<p class="lead">\s*.*?\s*</p>',
        f'<p class="lead">\n        {lead}\n      </p>',
        text,
        count=1,
        flags=re.DOTALL,
    )
    return text


READER_ROOM_START = "  <!-- reader-room -->"
READER_ROOM_END = "  <!-- /reader-room -->"

READER_ROOM_HTML = """  <!-- reader-room -->
  <section id="reader-room" class="reader-room" aria-labelledby="reader-room-heading">
    <div class="reader-room-inner">
      <div class="reader-room-copy">
        <p class="eyebrow">Schools · home · any device</p>
        <h2 id="reader-room-heading">Reading room — fullscreen textbook</h2>
        <p>
          Every chapter opens in <strong>full-screen reader mode</strong>: warm cream paper, brown ink, soft grain —
          like a bound textbook you can pinch, scroll, and zoom. Tap <strong>Read</strong> on any chapter, or start below.
          Customize paper, ink, accent, muted text, code blocks, typeface, and column width. Settings sync across chapters on this device.
        </p>
        <ul class="reader-room-features">
          <li><strong>Pinch zoom</strong> on phone and tablet · <strong>Ctrl+wheel</strong> (or trackpad pinch) on desktop</li>
          <li><strong>Double-tap</strong> or <strong>long-press</strong> anywhere on the page to close reader</li>
          <li>Toolbar <kbd>+</kbd>/<kbd>−</kbd> zoom · <kbd>Shift</kbd>+<kbd>+</kbd>/<kbd>−</kbd> font size · <kbd>Esc</kbd> exit</li>
          <li><strong>Classroom</strong> preset: high-contrast cream paper for projectors and bright rooms</li>
        </ul>
        <div class="reader-room-cta">
          <a class="btn btn-reader-vanilla" href="chapters/01-preface.html?reader=1">Open Chapter 1 in reader</a>
          <a class="btn secondary" href="#chapters">Browse all 22 chapters</a>
          <a class="btn secondary" href="https://github.com/ZacharyGeurts/Field_Primer/tree/main/pdf">PDF textbook (7 volumes)</a>
        </div>
      </div>
      <div class="reader-preview-wrap" aria-hidden="true">
        <span class="reader-preview-label">Your paper</span>
        <div id="reader-room-preview">
          <p class="reader-preview-title">Field Technology v6</p>
          <p class="reader-preview-body">Reality is 3D. Time is linear. Energy can be moved.</p>
          <span class="reader-preview-muted">Caption and muted text</span>
          <code class="reader-preview-code">grep THERMO run.log</code>
        </div>
      </div>
    </div>
  </section>
  <!-- /reader-room -->"""


def patch_reader_room(text: str) -> str:
    if READER_ROOM_START in text:
        return re.sub(
            rf"{re.escape(READER_ROOM_START)}.*?{re.escape(READER_ROOM_END)}",
            READER_ROOM_HTML.strip(),
            text,
            count=1,
            flags=re.DOTALL,
        )
    return text.replace(
        "  </header>\n\n  <main>",
        "  </header>\n\n" + READER_ROOM_HTML + "\n\n  <main>",
        1,
    )


FEATURED_CREDITORS = (
    "maxwell",
    "landauer",
    "shannon",
    "bennett",
    "khronos",
    "hostess7",
    "zachary-geurts",
    "grok",
    "love-and-god",
)

CREDITOR_GRID_START = "      <div class=\"creditor-grid\">"
CREDITOR_GRID_END = "      </div>"


def creditor_card(slug: str, name: str) -> str:
    esc_name = html.escape(name)
    return (
        f'        <a class="creditor-card" href="creditors/{slug}.html">'
        f'<img src="assets/images/v4/creditors/{slug}.jpg" alt="" loading="lazy" />'
        f"<h4>{esc_name}</h4></a>"
    )


def build_creditor_grid(manifest: dict) -> str:
    by_slug = {c["slug"]: c for c in manifest["creditors"]}
    lines = [CREDITOR_GRID_START]
    for slug in FEATURED_CREDITORS:
        c = by_slug.get(slug)
        if c:
            lines.append(creditor_card(slug, c["name"]))
    lines.append("      " + CREDITOR_GRID_END.strip())
    return "\n".join(lines)


def patch_creditor_grid(text: str, manifest: dict) -> str:
    inner = "\n".join(build_creditor_grid(manifest).splitlines()[1:-1])
    pattern = re.compile(
        r'(<section id="creditors">.*?<div class="creditor-grid">)\s*.*?\s*(</div>\s*<p style="margin-top:1\.5rem">)',
        re.DOTALL,
    )

    def _repl(m: re.Match[str]) -> str:
        return f"{m.group(1)}\n{inner}\n      {m.group(2)}"

    return pattern.sub(_repl, text, count=1)


def patch_v6_badge(text: str) -> str:
    text = text.replace('<span class="v6-badge">v5</span>', '<span class="v6-badge">v6</span>')
    text = text.replace('<span class="v5-badge">v5</span>', '<span class="v6-badge">v6</span>')
    return text


def patch_chapters_heading(text: str) -> str:
    return re.sub(
        r'(<section id="chapters">\s*<h2>).*?(</h2>)',
        r"\g<1>22 chapters — hand-written in v6\g<2>",
        text,
        count=1,
        flags=re.DOTALL,
    )


def patch_rocks_table(text: str) -> str:
    rows = master_rocks_index_rows().strip()
    return re.sub(
        r'(<section id="rocks">.*?<tbody>)\s*.*?\s*(</tbody>)',
        rf"\1\n{rows}\n        \2",
        text,
        count=1,
        flags=re.DOTALL,
    )


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    text = INDEX.read_text(encoding="utf-8")

    meta = social_meta(
        title="Field Technology v6 — Serious Book · Textbook of 2026",
        description=(
            "22-chapter operator textbook · fullscreen reader · pinch zoom · Grok16 2.0 single fabric · "
            "NEXUS host desktop · Queen gates · master rocks table. Reality is 3D. Time is linear. Energy can be moved."
        ),
        url="https://zacharygeurts.github.io/Field_Primer/",
        image_alt="Field Technology v6 — Serious Book cover and axioms",
        path_prefix="",
    )
    block = f"{MARKER_START}\n{meta}\n{MARKER_END}"
    if MARKER_START not in text:
        raise SystemExit("index.html missing social-meta markers")
    text = re.sub(
        rf"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}",
        block,
        text,
        count=1,
        flags=re.DOTALL,
    )

    if GRID_START not in text:
        raise SystemExit("index.html missing chapter-grid markers")
    grid = build_chapter_grid(manifest)
    text = re.sub(
        rf"{re.escape(GRID_START)}.*?{re.escape(GRID_END)}",
        grid,
        text,
        count=1,
        flags=re.DOTALL,
    )

    creditors_manifest = json.loads((ROOT / "docs/data/creditors-manifest.json").read_text(encoding="utf-8"))

    text = patch_about_copy(text)
    text = patch_hero_lead(text)
    text = patch_reader_room(text)
    text = patch_rocks_table(text)
    text = patch_creditor_grid(text, creditors_manifest)
    text = patch_chapters_heading(text)
    text = patch_v6_badge(text)
    text = patch_reader_assets(text)
    text = patch_reader_cta(text)
    INDEX.write_text(text, encoding="utf-8")
    print(f"index.html updated — {len(chapter_keys(manifest))} chapter cards from manifest")


if __name__ == "__main__":
    main()
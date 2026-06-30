#!/usr/bin/env pythong
"""Build mandatory one-page reader filter — axioms, honesty, rocks gate."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sign_off_table import collect_status, html_table  # noqa: E402
from social_meta import social_meta  # noqa: E402

OUT = ROOT / "docs" / "read-first.html"

BODY = """
  <main class="chapter-main read-first-gate">
    <p class="eyebrow">Mandatory reader filter · ~3 minutes</p>
    <h1>Read this before Chapter 1</h1>
    <p class="lead">Publisher-ready gate: three axioms, honesty labels, and the rocks table. If you skip this page, you will misread metaphor as measurement.</p>

    <section id="axioms" class="gate-section">
      <h2>Core axioms</h2>
      <p>Every technical sentence in Field Technology must respect these constraints. They are not cosmology marketing — they are operator discipline.</p>
      <table>
        <thead><tr><th>Axiom</th><th>Operational meaning</th><th>Example</th><th>Label</th></tr></thead>
        <tbody>
          <tr><td><strong>Reality is 3D</strong></td><td>State lives at addressable coordinates — texels, guest offsets, socket tuples</td><td><code>data_bus[24]</code>, Field Die <code>guest[0xB8000]</code></td><td><span class="tag impl">Implemented</span></td></tr>
          <tr><td><strong>Time is linear</strong></td><td>Dispatch advances; entropy receipts do not run backward without explicit reset</td><td><code>TotalTime::seal()</code>, sovereign pulse verify</td><td><span class="tag impl">Implemented</span></td></tr>
          <tr><td><strong>Energy can be moved</strong></td><td>Coupling transfers work between channels; thermo proxy records maintenance cost</td><td><code>grep THERMO</code>, <code>entropyThisFrame</code></td><td><span class="tag meta">Metaphor</span> proxy</td></tr>
        </tbody>
      </table>
    </section>

    <section id="honesty" class="gate-section">
      <h2>Honesty system — four labels</h2>
      <p>Every major claim carries exactly one primary label. Mixed labels mean the paragraph needs editing.</p>
      <table>
        <thead><tr><th>Label</th><th>Use when</th><th>Do not use when</th></tr></thead>
        <tbody>
          <tr><td><span class="tag impl">Implemented</span></td><td>Grep, binding, or jsonl proves it on your machine today</td><td>Theory slide without host/shader match</td></tr>
          <tr><td><span class="tag meta">Metaphor</span></td><td>Intuition, proxy, or visual stack — explicitly not instrumentation</td><td>You can bill joules or claim spectrum analysis</td></tr>
          <tr><td><span class="tag phil">Philosophy</span></td><td>Operator discipline, sacred track, edition ambition</td><td>Substituting for stderr in a status email</td></tr>
          <tr><td><span class="tag vis">Visual</span></td><td>Beautiful ink that does not measure</td><td>Planetary weave cited as RF lab data</td></tr>
        </tbody>
      </table>
      <p><strong>Edition name:</strong> <em>Textbook of 2026</em> = teaching ambition <span class="tag phil">Philosophy</span> — not third-party accreditation.</p>
      <p><strong>Architecture shorthand:</strong> Queen “robot brain” / DARPA-grade = in-process gate+recall metaphor <span class="tag meta">Metaphor</span> — not a government deliverable.</p>
    </section>

    <section id="rocks-gate" class="gate-section">
      <h2>Rocks table — mandatory filter</h2>
      <p>If marketing copy disagrees with this table, the table wins. Full list: <a href="chapters/22-glossary.html#master-rocks">Chapter 22 master rocks</a>.</p>
      <table>
        <thead><tr><th>Claim</th><th>Operator reality</th><th>Label</th></tr></thead>
        <tbody>
          <tr><td>Certified textbook</td><td>Manuscript-grade operator course</td><td><span class="tag phil">Philosophy</span></td></tr>
          <tr><td>Landauer joules from GPU</td><td>Proxy integral only — not wattmeter</td><td><span class="tag meta">Metaphor</span></td></tr>
          <tr><td>Packet field sees everything</td><td>Local sockets on your machine</td><td><span class="tag impl">Implemented</span> local</td></tr>
          <tr><td>SDF brain imaging</td><td>Procedural plates — not fMRI</td><td><span class="tag meta">Metaphor</span></td></tr>
          <tr><td>Love / God prove physics</td><td>Sacred track Ch 16–18 — optional</td><td><span class="tag phil">Philosophy</span></td></tr>
          <tr><td>Queen all gates</td><td>When <code>QUEEN_READY</code> after build</td><td><span class="tag impl">Implemented</span> when built</td></tr>
        </tbody>
      </table>
    </section>

    <section id="mayer-segment" class="gate-section">
      <h2>Textbook segment standard — Mayer beats</h2>
      <p>Field Primer is the <strong>definitive textbook</strong> on Field Technology — collegiate / masters-level physics and engineering, with <strong>lead-in prose</strong> before formal equations so lay readers can climb into the math. Dense, thorough, clear, clarifying; only as many pages per chapter as the information requires. One book should teach the whole stack.</p>
      <p>Each teaching beat is a <strong>Mayer segment</strong>: approximately <strong>900–1,200 words</strong> of full prose plus <strong>one signaled figure</strong>, a <strong>Professor Grok</strong> plain-summary box, and <strong>local citations</strong> (chapter, wiki, creditor links) at the bottom of the segment.</p>
      <table>
        <thead><tr><th>Metric</th><th>Target</th><th>Why</th></tr></thead>
        <tbody>
          <tr><td>Words per segment</td><td>900–1,200</td><td>One conceptual beat; Mayer segmenting</td></tr>
          <tr><td>Figures per segment</td><td>1 mechanism figure</td><td>Dual coding — visual + verbal same claim</td></tr>
          <tr><td>Lead-in block</td><td>Before heavy math</td><td>Layman staircase into equations</td></tr>
          <tr><td>Professor Grok box</td><td>1 per segment</td><td>Plain summary beside dense prose</td></tr>
          <tr><td>Segment citations</td><td>Per page / segment</td><td>Go-deeper links without leaving the book</td></tr>
          <tr><td>Exemplar chapters</td><td><a href="chapters/02-fields-pixels-packets.html?reader=1">Ch 2</a> · <a href="chapters/03-thermodynamics.html?reader=1">Ch 3</a></td><td>Coordinates + full thermodynamics on fabric</td></tr>
        </tbody>
      </table>
      <p>Illustration theory (Leonardo → Mayer) is Chapter 1. Hostess7 ingests each segment losslessly for SDF recall. When prose sounds like marketing, grep Chapter 12 before you teach from it.</p>
    </section>

    <section id="spine-gate" class="gate-section">
      <h2>Book spine — 14 core + appendices</h2>
      <p>Twenty-two files on disk; fourteen chapters form the technical manual. Sacred, creditor, and horizon material is appendix — bracketed, not interleaved in proofs.</p>
      <table>
        <thead><tr><th>Part</th><th>Core chapters</th><th>Appendix</th></tr></thead>
        <tbody>
          <tr><td><strong>I Foundations</strong></td><td>02–06 fields, thermo, entropy, packet, RF</td><td>—</td></tr>
          <tr><td><strong>II Implementation</strong></td><td>07–11 engine, die, FCC, spiderweb, observability</td><td>—</td></tr>
          <tr><td><strong>III Defense</strong></td><td>12 honesty capstone; 19–20 time &amp; services</td><td>—</td></tr>
          <tr><td><strong>IV Operator</strong></td><td>21 Queen browser</td><td>18 covenant</td></tr>
          <tr><td><strong>Reference</strong></td><td>01 preface (onboarding)</td><td>13–17 creditors + sacred; 22 glossary; <a href="chapters/22-glossary.html#horizon">Horizon</a></td></tr>
        </tbody>
      </table>
    </section>

    <section id="repro-gate" class="gate-section">
      <h2>Reproducibility — build today vs proposed</h2>
      <table>
        <thead><tr><th>Build today</th><th>Proposed / horizon</th></tr></thead>
        <tbody>
          <tr><td><code>./linux.sh run</code> + <code>grep THERMO</code></td><td>Calibrated GPU joules vs proxy</td></tr>
          <tr><td>NEXUS panel <code>:9477</code>, gatekeeper jsonl</td><td>Full DNSSEC wire validation</td></tr>
          <tr><td><code>QUEEN_BROWSER_BUILD</code> → <code>QUEEN_READY</code></td><td>Parity across all gate classes</td></tr>
          <tr><td>Hostess7 SDF segment workflow</td><td>Cross-host sovereign time under adversarial NTP</td></tr>
        </tbody>
      </table>
    </section>

    {sign_off}

    <div class="cta-row gate-cta">
      <a class="btn" href="chapters/01-preface.html?reader=1">Continue to Chapter 1 — Preface</a>
      <a class="btn secondary" href="index.html">Home</a>
      <a class="btn secondary" href="chapters/22-glossary.html#master-rocks">Full rocks table</a>
    </div>
  </main>
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>Read First — Field Technology v5</title>
{social_meta}
  <link rel="stylesheet" href="css/field-primer.css" />
  <link rel="stylesheet" href="css/chapters.css" />
  <link rel="stylesheet" href="css/reader.css" />
</head>
<body class="chapter-page accent-phi read-first-page">
  <nav class="top"><div class="inner">
    <a class="logo" href="index.html">FIELD TECHNOLOGY <span class="v5-badge">v5</span></a>
    <ul>
      <li><a href="creditors/index.html">Creditors</a></li>
      <li><a href="index.html#chapters">Chapters</a></li>
      <li><a href="wiki/Home.md">Wiki</a></li>
    </ul>
  </div></nav>
{body}
  <footer><p>Field Technology v5 · Read first · We do not hide the rocks.</p></footer>
  <script src="js/reader.js" defer></script>
</body>
</html>
"""


def main() -> None:
    doc = collect_status()
    sign_off = html_table(doc)
    json_out = ROOT / "docs" / "data" / "sign-off.json"
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    meta = social_meta(
        title="Read First — Field Technology v5",
        description="Mandatory reader filter: three axioms, honesty labels, rocks table, 14-chapter spine, reproducibility scope.",
        url="https://zacharygeurts.github.io/Field_Primer/read-first.html",
        image_alt="Field Technology v5 reader gate",
        path_prefix="",
    )
    OUT.write_text(
        TEMPLATE.format(social_meta=meta, body=BODY.format(sign_off=sign_off)),
        encoding="utf-8",
    )
    print(f"wrote {OUT.relative_to(ROOT)} (sign-off stamped {doc['stamped']})")


if __name__ == "__main__":
    main()
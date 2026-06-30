#!/usr/bin/env python3
"""Apply Field Technology v6 stack update — index copy, chapter addenda, creditors."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CHAPTERS = DOCS / "chapters"
CREDITORS = ROOT / "docs/data/creditors-manifest.json"

V6_ADDENDUM = {
    "01": """
<section class="v6-addendum" id="v6-stack-2026">
  <h2>v6 addendum — what we shipped in 2026</h2>
  <p class="tag-line"><span class="tag impl">Implemented</span> NEXUS-Shield v10 · Grok16 2.0 · single fabric · depth fields sealed and destroyed</p>
  <p>Since v5 manuscript freeze, the operator stack gained a <strong>host desktop</strong> landing (<code>:9477/field</code>),
  <strong>Queen Browser</strong> with field OS inside the Start tab, <strong>Grok16 2.0 single-fabric</strong> belt dispatch,
  and <strong>Ironclad safety meld</strong> — one field amplitude at depth zero, linear sovereign time (<code>ironclad:time:1</code>).</p>
  <table>
    <tr><th>Layer</th><th>What changed</th><th>Verify</th></tr>
    <tr><td>NEXUS-Shield</td><td>Connection gatekeeper · DNS/DHCP takeover · egress integrity · host freeze</td><td><code>nexus verify</code> · panel <code>:9477/command</code></td></tr>
    <tr><td>Grok16 2.0</td><td><code>belt_2_0</code> · <code>bench-triad</code> · <code>grok16-integrate.sh</code></td><td><code>test-battery-belt</code></td></tr>
    <tr><td>Ironclad</td><td>this_one / that_one · depth fields sealed and destroyed</td><td><code>field-depth-singularizer</code></td></tr>
    <tr><td>Queen</td><td>Browser gates · performance flyout · field-net classify</td><td><code>QUEEN_READY</code> · <code>:9481</code></td></tr>
    <tr><td>Landauer practice</td><td>Field Thermal Guard — incremental redata, budget-capped</td><td>thermal advisory panel</td></tr>
  </table>
  <p>Read Chapters 19–21 for sovereign time, public services, and Queen — each carries a v6 operator paragraph. Chapter 22 master rocks lists what is still metaphor.</p>
</section>
""",
    "19": """
<section class="v6-addendum" id="v6-sovereign-time">
  <h3>v6 — sovereign time meld</h3>
  <p><code>ironclad:time:1</code> — time is <strong>linear</strong>, sealed via <code>linear_ns</code>, not geometry <code>t</code>.
  Host freeze resume runs <code>resume-witness</code> so gaps across soft/mem/disk freeze stay operator-visible.
  G1ID melds absorb sovereign clock from <code>lib/sovereign-time.py</code> — wall clock is witness-only.</p>
</section>
""",
    "20": """
<section class="v6-addendum" id="v6-public-services">
  <h3>v6 — DNS · DHCP · egress integrity</h3>
  <p>NEXUS 7.6 graceful DNS/DHCP takeover keeps resolver authority on-loopback. <code>dns-egress-integrity.py</code>
  logs permitted egress with <code>sent_hash</code> vs <code>recv_hash</code> — mismatches flag eradication, not silent MITM.
  Planetary DNS security zones run at EXTREME parity per region.</p>
</section>
""",
    "21": """
<section class="v6-addendum" id="v6-queen-browser">
  <h3>v6 — Queen browser · host desktop · Grok16 integrate</h3>
  <p>First page is the <strong>host desktop</strong> — familiar apps, field startbar. Queen Browser on <code>:9481</code>
  embeds the field OS in Start; drop/rise underlay calls <code>/api/field-underlay-surface</code>.
  <code>grok16-integrate.sh</code> wires canonical <code>G16_PREFIX</code> + <code>belt_2_0</code> to Queen, World_Redata, ZOCR.
  Single fabric: parallel I/O may fan in; panel truth stays depth 0 — depth fields sealed and destroyed at every gate.</p>
</section>
""",
}


def inject_addenda() -> None:
    for key, html in V6_ADDENDUM.items():
        manifest_path = ROOT / "docs/data/image-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        slug = manifest["chapters"][key]["slug"]
        path = CHAPTERS / f"{slug}.html"
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        marker = f'id="v6-'
        if marker in text:
            continue
        text = text.replace(
            '<nav class="chapter-nav bottom">',
            html.strip() + "\n    <nav class=\"chapter-nav bottom\">",
            1,
        )
        path.write_text(text, encoding="utf-8")
        print(f"  addendum → {path.name}")


def patch_index_v6() -> None:
    path = DOCS / "index.html"
    text = path.read_text(encoding="utf-8")
    replacements = [
        ("Field Technology v5", "Field Technology v6"),
        ("v5-badge", "v6-badge"),
        (
            "Keyboard: <kbd>+</kbd>/<kbd>−</kbd> size, <kbd>Esc</kbd> exit",
            "Pinch or <kbd>Ctrl</kbd>+wheel zoom · <kbd>+</kbd>/<kbd>−</kbd> zoom · double-tap or long-press close · <kbd>Esc</kbd> exit",
        ),
        (
            "like a textbook page, not a tech demo",
            "like a textbook page — fullscreen with pinch, trackpad, and mouse-wheel zoom",
        ),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    if "Grok16 2.0" not in text:
        text = text.replace(
            "Engineering core on Phi, Thermo, Flow, Field Die, packet field, observability, sovereign time, and Queen.",
            "Engineering core on Phi, Thermo, Flow, Field Die, packet field, observability, sovereign time, Queen, "
            "<strong>Grok16 2.0 single fabric</strong>, and NEXUS host desktop.",
            1,
        )
    path.write_text(text, encoding="utf-8")
    print("  index.html → v6 copy")


def add_creditors() -> None:
    doc = json.loads(CREDITORS.read_text(encoding="utf-8"))
    slugs = {c["slug"] for c in doc["creditors"]}
    new_entries = [
        {
            "slug": "bennett",
            "name": "Charles Bennett",
            "years": "1943–",
            "category": "science",
            "portrait_url": "generated",
            "portrait_credit": "Generated tribute — reversible computing light",
            "accent": "thermo",
            "prompted": "Reversible computing discourse with Landauer — why we label proxy integrals and practice incremental redata.",
            "love": "Erasure has a cost; gentleness with bits is love for the next reader of the log.",
            "god": "Information preserved without waste — a parable of resurrection without lie.",
        },
        {
            "slug": "khronos",
            "name": "Khronos Group",
            "years": "Vulkan · SPIR-V",
            "category": "science",
            "portrait_url": "generated",
            "portrait_credit": "Generated tribute — API constellation",
            "accent": "phi",
            "prompted": "Vulkan dispatch spine — descriptors, SSBO fabric, AMOURANTHRTX binding model.",
            "love": "Open standards let operators own their shaders without renting sight.",
            "god": "Shared grammar for GPUs — many vendors, one honest interface.",
        },
        {
            "slug": "hostess7",
            "name": "Hostess 7 · Neural stack",
            "years": "Queen brain · SDF doctrine",
            "category": "collaborator",
            "portrait_url": "generated",
            "portrait_credit": "Generated tribute — procedural brain plates",
            "accent": "gold",
            "prompted": "Neural encourage gate, brain guard witness, SDF plates, training viewer — Queen robot brain metaphor made grep-able.",
            "love": "She adapts with truth floors — never flattering the operator into danger.",
            "god": "Discernment as hospitality: welcome the signal, quarantine the ventriloquist.",
        },
    ]
    for entry in new_entries:
        if entry["slug"] not in slugs:
            doc["creditors"].append(entry)
    doc["version"] = 6
    CREDITORS.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"  creditors-manifest → {len(doc['creditors'])} entries")


DEPTH_FIELD_REPLACEMENTS = (
    ("depth-field impossible", "depth fields sealed and destroyed"),
    ("depth-field impossibility", "depth fields sealed and destroyed"),
    ("depth-field creation forbidden", "depth fields sealed and destroyed"),
    ("Depth-field nested truth", "Depth fields sealed and destroyed"),
    ("Creation forbidden — <code>field_depth</code> stripped at gates", "Sealed and destroyed — <code>field_depth</code> cannot persist at any gate"),
    ("<code>field_depth</code> cannot persist.", "Depth fields sealed and destroyed at every gate."),
    ("depth-field creation forbidden", "depth fields sealed and destroyed"),
)


def patch_depth_field_doctrine() -> None:
    """Align published HTML with Ironclad: depth fields sealed and destroyed."""
    targets = [DOCS / "index.html", *CHAPTERS.glob("*.html")]
    for path in targets:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        orig = text
        for old, new in DEPTH_FIELD_REPLACEMENTS:
            text = text.replace(old, new)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            print(f"  depth doctrine → {path.name}")


def patch_css_badge() -> None:
    css = DOCS / "css/field-primer.css"
    text = css.read_text(encoding="utf-8")
    if ".v6-badge" not in text:
        text = text.replace(
            ".v5-badge {",
            ".v5-badge,\n.v6-badge {",
            1,
        )
        css.write_text(text, encoding="utf-8")
        print("  field-primer.css → v6-badge")


def main() -> None:
    print("apply-v6-update:")
    patch_css_badge()
    add_creditors()
    inject_addenda()
    patch_depth_field_doctrine()
    patch_index_v6()
    print("v6 update applied")


if __name__ == "__main__":
    main()
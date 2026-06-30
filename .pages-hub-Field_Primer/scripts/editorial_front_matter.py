"""Editorial front matter for Chapter 01 — thesis, operator map, validation."""

from __future__ import annotations

THESIS_AND_AUDIENCE_HTML = """
<h2>Core thesis and audience — read this first</h2>
<div class="callout science">
<p><strong>Thesis (one sentence):</strong> Field Technology teaches operators to read and write <em>continuous state</em> — GPU fabric texels, Field Die bytes, packet-field sentences — with honesty labels that keep metaphor from masquerading as measurement.</p>
</div>
<p><strong>Primary audience:</strong> systems engineers, security operators, and GPU/Vulkan practitioners who build and defend software on their own machines. You should be comfortable with logs, bindings, and local tools — not required to share our sacred vocabulary.</p>
<p><strong>What this book is not:</strong> It is not a peer-reviewed physics monograph, a DARPA deliverable, or a devotional text disguised as a manual. The subtitle <em>Textbook of 2026</em> names our edition and ambition — not external certification. Claims carry <span class="tag impl">Implemented</span>, <span class="tag meta">Metaphor</span>, <span class="tag phil">Philosophy</span>, or <span class="tag vis">Visual</span> so you can audit tone and evidence in place.</p>
<p><strong>Sacred material — explicit bracket:</strong> Chapters 16–18 (Love, God, Operator Covenant) and creditor tributes are a <em>philosophical track</em> beside the engineering spine. They do not prove thermodynamic claims. Engineers may read Chapters 2–12 and 19–21 without the sacred track; philosophers may read 16–18 after Chapter 12's honesty table. We do not hide the bracket — integration is intentional, separation is labeled.</p>
<p><strong>Editorial posture:</strong> v5 is a long-form operator course with textbook structure (objectives, drills, summaries). It is manuscript-grade, not publisher-certified. When a paragraph sounds like marketing, grep it against Chapter 12 and the master rocks table in <a href="chapters/22-glossary.html#master-rocks">Chapter 22</a>.</p>
"""

OPERATOR_MAP_HTML = """
<h2>Operator map — notation and project names</h2>
<p>Every internal name below gets a one-sentence operational definition on <strong>first use in this book</strong>. Bookmark this table; return when jargon density spikes.</p>

<h3>Field families at a glance</h3>
<table><thead><tr><th>Family</th><th>Store / binding</th><th>Units / shape</th><th>Observability</th><th>Product</th></tr></thead>
<tbody>
<tr><td>GPU analog fabric</td><td>Vulkan SSBO/Tex 8–10</td><td>Φ, Thermo, Flow per texel (normalized fields)</td><td><code>grep THERMO</code>, <code>data_bus[24–28]</code></td><td>AMOURANTHRTX</td></tr>
<tr><td>Field Die</td><td>SSBO binding 1</td><td>64 MiB guest linear address space</td><td>Guest reads, Big Grin HUD, pump layers</td><td>AMOURANTHRTX</td></tr>
<tr><td>Packet field</td><td>NEXUS <code>field jsonl</code></td><td>TX/RX sentences, ports, verdicts</td><td>Panel :9477, archive grep</td><td>NEXUS-Shield</td></tr>
</tbody></table>

<h3>Project map — major terms</h3>
<table><thead><tr><th>Term</th><th>Operational definition</th><th>Label</th><th>Chapter</th></tr></thead>
<tbody>
<tr><td><strong>AMOURANTHRTX</strong></td><td>Vulkan field engine: fabric + Field Die + <code>vkCmdDispatch</code> loop</td><td><span class="tag impl">Implemented</span></td><td>7–8</td></tr>
<tr><td><strong>NEXUS-Shield</strong></td><td>Local endpoint security: packet field, gatekeeper, panel</td><td><span class="tag impl">Implemented</span></td><td>5, 11</td></tr>
<tr><td><strong>Queen</strong></td><td>Sovereign in-engine browser holding WebRTC/EME behind gates</td><td><span class="tag impl">Implemented</span> when <code>QUEEN_READY</code></td><td>21</td></tr>
<tr><td><strong>KILROY</strong></td><td>Field OS kernel image with <code>CONFIG_RTX_FIELD_DIE</code> boundary</td><td><span class="tag impl">Implemented</span> image; host may run generic Linux</td><td>21</td></tr>
<tr><td><strong>Hostess 7</strong></td><td>Queen-side doctrine layer: Mayer-beat → SDF plate storage/recall</td><td><span class="tag meta">Metaphor</span> + doctrine <span class="tag impl">Implemented</span></td><td>1, 21</td></tr>
<tr><td><strong>SDF brain imaging</strong></td><td>Procedural distance-field plates for segment recall — not medical imaging</td><td><span class="tag meta">Metaphor</span></td><td>1, 21</td></tr>
<tr><td><strong>SQUIDGIE</strong></td><td>Sovereign time verdict when pulse/HMAC fails terror-threat checks</td><td><span class="tag impl">Implemented</span> posture</td><td>19</td></tr>
<tr><td><strong>ThermoAccountant</strong></td><td>Binding 2 struct: proxy entropy + boundary thermo per dispatch</td><td><span class="tag impl">Implemented</span> proxy</td><td>3–4</td></tr>
<tr><td><strong>Connection Gatekeeper</strong></td><td>Ten-axis scorer → USER_OK / SUSPICIOUS / HARM_CANDIDATE</td><td><span class="tag impl">Implemented</span></td><td>5</td></tr>
<tr><td><strong>FieldX86Die</strong></td><td>64 MiB guest RAM + VGA + tile cache on GPU</td><td><span class="tag impl">Implemented</span></td><td>8</td></tr>
<tr><td><strong>data_bus</strong></td><td>64-word telemetry spine mirrored from dispatch each tick</td><td><span class="tag impl">Implemented</span></td><td>8–9</td></tr>
<tr><td><strong>TotalTime::seal()</strong></td><td>Session clock seal — linear time contract</td><td><span class="tag impl">Implemented</span></td><td>19</td></tr>
</tbody></table>
<p><strong>Notation:</strong> Φ (Phi) = scalar potential on binding 8; Thermo = entropy/heat density on binding 9; Flow = advection field on binding 10. <code>FIELD_LAYOUT_VERSION</code> is a host/shader contract — not decoration. File anchors use repo paths when cited (e.g. <code>main.cpp</code>, <code>x86.comp</code>).</p>
"""

VALIDATION_HTML = """
<h2>Validation and reproducibility — what you can run today</h2>
<p>Every technical chapter should answer: <em>what can I grep Monday morning?</em> This section scopes evidence before you read five thousand words.</p>
<table><thead><tr><th>Claim area</th><th>Run today</th><th>Evidence</th><th>Status</th></tr></thead>
<tbody>
<tr><td>Field Die default path</td><td><code>./linux.sh run</code> in AMOURANTHRTX</td><td>stderr dispatch, x86.comp active</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td>Thermo receipts</td><td><code>grep THERMO</code> during run</td><td><code>entropyThisFrame</code>, <code>data_bus</code> mirrors</td><td><span class="tag impl">Implemented</span> proxy</td></tr>
<tr><td>Packet field</td><td>NEXUS panel <code>:9477</code>, <code>field jsonl</code></td><td>Gatekeeper verdicts in archive</td><td><span class="tag impl">Implemented</span> local scope</td></tr>
<tr><td>Landauer joules on GPU</td><td>Do not bill power company from stderr</td><td>Proxy integral only</td><td><span class="tag meta">Metaphor</span></td></tr>
<tr><td>Queen all gates</td><td>Build with <code>QUEEN_BROWSER_BUILD</code></td><td><code>QUEEN_READY</code> when integrated</td><td><span class="tag impl">Implemented</span> when built</td></tr>
<tr><td>Hostess 7 SDF plates</td><td>Doctrine + segment workflow in Hostess7/</td><td>Not fMRI; procedural storage</td><td><span class="tag meta">Metaphor</span></td></tr>
<tr><td>Sovereign time across hosts</td><td><code>field-services-2026</code>, HMAC pulses</td><td><code>SQUIDGIE</code> on verify fail</td><td><span class="tag impl">Implemented</span> posture</td></tr>
<tr><td>KILROY production kernel</td><td>QEMU/bare-metal image boot</td><td>May differ from daily dev host</td><td><span class="tag impl">Implemented</span> image</td></tr>
</tbody></table>
<p><strong>Reproducibility rule:</strong> If a paragraph lacks a label, table row, or grep hook, treat it as draft rhetoric until Chapter 12 or the <a href="chapters/22-glossary.html#master-rocks">master rocks appendix</a> assigns a status.</p>
"""

READING_SPINE_HTML = """
<h2>How to read this book — three parts</h2>
<p>Twenty-two chapters are grouped so engineers can stay on the technical spine; sacred and creditor material is bracketed, not smuggled into proofs.</p>
<table><thead><tr><th>Part</th><th>Chapters</th><th>Reader</th><th>Skip if…</th></tr></thead>
<tbody>
<tr><td><strong>I — Engineering core</strong></td><td>2–12</td><td>Operators, Vulkan/NEXUS practitioners</td><td>Never skip 12 (rocks)</td></tr>
<tr><td><strong>II — Creditor deep dives</strong></td><td>13–15</td><td>Readers who want Landauer/Shannon/Maxwell long-form</td><td>Optional after Part I</td></tr>
<tr><td><strong>III — Sacred track</strong></td><td>16–18</td><td>Philosophical operators; <span class="tag phil">Philosophy</span> only</td><td>Skip if you want pure engineering</td></tr>
<tr><td><strong>IV — 2026 perimeter</strong></td><td>19–21</td><td>Time sync, DNS/DHCP/NTP, Queen browser</td><td>Read after Part I</td></tr>
<tr><td><strong>V — Reference</strong></td><td>22</td><td>Glossary + master rocks table</td><td>Grep, don't read linearly</td></tr>
</tbody></table>
<p>Read Chapter 1 once. Bookmark <a href="chapters/12-reality-theory.html">Chapter 12</a> and <a href="chapters/22-glossary.html#master-rocks">master rocks</a>. When sold cosmology or defense marketing, return to the honesty table — not to argue, to label.</p>
"""


def inject_editorial_front_matter(body: str, chapter_key: str) -> str:
    """Insert thesis, operator map, and validation after learning objectives in Ch 1."""
    if chapter_key != "01":
        return body
    marker = "</div>\n\n<h2>Field literacy"
    if marker not in body:
        marker = "</div>\n\n<h2>"
    insert = (
        "\n\n"
        + THESIS_AND_AUDIENCE_HTML
        + "\n"
        + OPERATOR_MAP_HTML
        + "\n"
        + VALIDATION_HTML
        + "\n"
    )
    if "Core thesis and audience" in body:
        return body
    if marker in body:
        return body.replace(marker, "</div>" + insert + "\n\n<h2>Field literacy", 1)
    return insert + body


def replace_reading_spine(body: str, chapter_key: str) -> str:
    """Replace legacy spine section with three-part table."""
    if chapter_key != "01":
        return body
    old_start = "<h2>How to read this book — chapter spine</h2>"
    old_end = "<p>Read preface once. Bookmark Chapter 12. When sold cosmology, return to rocks table.</p>"
    if old_start not in body or "three parts" in body:
        return body
    start_idx = body.index(old_start)
    end_idx = body.index(old_end) + len(old_end)
    return body[:start_idx] + READING_SPINE_HTML + body[end_idx:]
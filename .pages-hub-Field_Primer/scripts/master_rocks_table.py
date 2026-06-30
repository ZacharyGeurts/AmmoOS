"""Master rocks & open questions table — appendix for Ch 22 and site index."""

from __future__ import annotations

MASTER_ROCKS_ID = "master-rocks"

MASTER_ROCKS_HTML = f"""
<h2 id="{MASTER_ROCKS_ID}">Master rocks and open questions</h2>
<p>Consolidated honesty table — every major claim that marketing might exaggerate, with current evidence level. Supersedes scattered rocks in Chapter 12 and the site index. Update this table when implementation catches aspiration.</p>
<table><thead><tr><th>Claim</th><th>Operator reality</th><th>Label</th><th>Evidence / gap</th></tr></thead>
<tbody>
<tr><td>This is a certified textbook</td><td>Long-form operator course; manuscript not publisher-certified</td><td><span class="tag phil">Philosophy</span></td><td>Edition subtitle, not external validation</td></tr>
<tr><td>Textbook of 2026</td><td>Edition name and teaching ambition</td><td><span class="tag phil">Philosophy</span></td><td>Not third-party curriculum approval</td></tr>
<tr><td>Field literacy as greatest weapon</td><td>Read/write continuous state locally; distrust single dashboards</td><td><span class="tag phil">Philosophy</span></td><td>Operator discipline, not ordnance</td></tr>
<tr><td>Living thermodynamic computer</td><td>ThermoAccountant in stderr each dispatch</td><td><span class="tag impl">Implemented</span></td><td><code>grep THERMO</code></td></tr>
<tr><td>Landauer joules from GPU</td><td>Proxy integral <code>entropyThisFrame</code></td><td><span class="tag meta">Metaphor</span></td><td>Not package wattmeter</td></tr>
<tr><td>Packet field sees everything</td><td>Local sockets + heuristics on your machine</td><td><span class="tag impl">Implemented</span></td><td>Not internet omniscience</td></tr>
<tr><td>RF planetary shell</td><td><code>planetary_weave.comp</code> visual stack</td><td><span class="tag vis">Visual</span></td><td>Not spectrum analyzer</td></tr>
<tr><td>Queen holds all gates</td><td>WebRTC/EME through gatekeeper when built</td><td><span class="tag impl">Implemented</span></td><td><code>QUEEN_READY</code> required</td></tr>
<tr><td>DARPA-grade / robot brain</td><td>In-process Queen architecture metaphor for gate+recall stack</td><td><span class="tag meta">Metaphor</span></td><td>Not a government program deliverable</td></tr>
<tr><td>Hostess 7 SDF brain imaging</td><td>Procedural SDF plates + segment doctrine</td><td><span class="tag meta">Metaphor</span></td><td>Not fMRI; Hostess7/ workflow</td></tr>
<tr><td>KILROY on daily driver host</td><td>Kernel image exists; dev may use generic Linux</td><td><span class="tag impl">Implemented</span></td><td>QEMU/bare-metal vs laptop</td></tr>
<tr><td>Love / God chapters prove physics</td><td>Sacred operator language beside math</td><td><span class="tag phil">Philosophy</span></td><td>Ch 16–18 optional track</td></tr>
<tr><td>Sub-micron SEM in shaders</td><td>Procedural pixel detail tiers</td><td><span class="tag meta">Metaphor</span></td><td>Spiderweb simulate tier</td></tr>
<tr><td>Tesla valve in chassis</td><td><code>TESLA_R_*</code> bias; <code>data_bus</code> slots</td><td><span class="tag meta">Metaphor</span></td><td>No fluidic part shipped</td></tr>
<tr><td>96% lies / device cannot drift</td><td>Security posture narrative</td><td><span class="tag phil">Philosophy</span></td><td>Not statistical claim</td></tr>
<tr><td>Illustration density ~1/1000 words</td><td>Mayer segmenting standard for v5</td><td><span class="tag phil">Philosophy</span></td><td>Editorial rule, Ch 1</td></tr>
<tr><td>Shannon H on fabric texels</td><td>Entropy Oracle on <em>files</em></td><td><span class="tag impl">Implemented</span></td><td>Separate from ThermoAccountant</td></tr>
<tr><td>Sealed / sovereign time</td><td><code>TotalTime::seal()</code> + HMAC pulses</td><td><span class="tag impl">Implemented</span></td><td><code>SQUIDGIE</code> on verify fail</td></tr>
<tr><td>x86.comp decorative</td><td>Default <code>./linux.sh run</code> path</td><td><span class="tag impl">Implemented</span></td><td>Field Die product</td></tr>
<tr><td>Equations without bindings</td><td>Theory vocabulary until grep proves</td><td><span class="tag meta">Metaphor</span></td><td>Ch 12 capstone table layers</td></tr>
<tr><td>Grok16 2.0 single fabric</td><td><code>belt_2_0</code> chunked redata · one amplitude at depth 0</td><td><span class="tag impl">Implemented</span></td><td><code>test-battery-belt</code> · integrate env</td></tr>
<tr><td>Depth-field nested truth</td><td>Sealed and destroyed — <code>field_depth</code> cannot persist at any gate</td><td><span class="tag impl">Implemented</span></td><td>field-depth-singularizer · Queen browser</td></tr>
<tr><td>DNS egress MITM-free</td><td>Permitted egress hash match logging</td><td><span class="tag impl">Implemented</span></td><td><code>dns-egress-integrity.jsonl</code></td></tr>
<tr><td>Host desktop first page</td><td>Mirror incumbent OS · field startbar</td><td><span class="tag impl">Implemented</span></td><td><code>:9477/field</code></td></tr>
<tr><td>this_one / that_one</td><td>Phantom lanes blocked until existence correlates</td><td><span class="tag impl">Implemented</span></td><td>ironclad-spatial-existence doctrine</td></tr>
</tbody></table>
<p><strong>Open questions</strong> (honest gaps — not roadmap promises): calibrated GPU joules vs proxy entropy; wire DNSSEC validation beyond stub counters; Queen production parity across all gate classes; reproducible cross-host sovereign time under adversarial NTP; belt_2_0 runtime wins on large redata workloads (micro-bench may favor host <code>-O2</code>). File issues against AMOURANTHRTX / NEXUS / Grok16 when you close a gap — then update this row.</p>
"""


def inject_master_rocks(body: str, chapter_key: str) -> str:
    """Prepend master rocks appendix to Chapter 22 glossary."""
    if chapter_key != "22":
        return body
    if MASTER_ROCKS_ID in body:
        return body
    return MASTER_ROCKS_HTML + "\n" + body


def master_rocks_index_rows() -> str:
    """HTML table rows for docs/index.html rocks section."""
    return """
          <tr><td>Publisher-ready textbook</td><td>Manuscript-grade operator course — not externally certified</td></tr>
          <tr><td>Textbook of 2026</td><td>Edition name — teaching ambition, not accreditation</td></tr>
          <tr><td>Landauer on GPU</td><td>Proxy integral — <span class="tag meta">Metaphor</span></td></tr>
          <tr><td>Packet field</td><td>Local sockets + heuristics — not cloud omniscience</td></tr>
          <tr><td>Queen / DARPA robot brain</td><td>In-process gate stack when <code>QUEEN_READY</code> — architecture <span class="tag meta">Metaphor</span></td></tr>
          <tr><td>SDF brain imaging</td><td>Hostess 7 procedural plates — <span class="tag meta">Metaphor</span>; not fMRI</td></tr>
          <tr><td>Love &amp; God chapters</td><td><span class="tag phil">Philosophy</span> track (16–18) — optional beside engineering core</td></tr>
          <tr><td>Illustration density</td><td>~1 figure / 1,000 words — Mayer segmenting, not wallpaper</td></tr>
          <tr><td>Full rocks list</td><td><a href="chapters/22-glossary.html#master-rocks">Chapter 22 master table →</a></td></tr>"""
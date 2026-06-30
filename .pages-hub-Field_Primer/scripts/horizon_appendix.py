"""Horizon appendix — aspirational material, not mixed into technical spine."""

from __future__ import annotations

HORIZON_ID = "horizon"

HORIZON_HTML = f"""
<h2 id="{HORIZON_ID}">Horizon appendix — proposed, not promised</h2>
<p><span class="tag phil">Philosophy / roadmap discipline.</span> Items here are honest gaps and research directions. They do not appear in the engineering spine (Chapters 2–12, 19–21) as if shipped. When an item closes, move it to Chapter 12 or the <a href="#master-rocks">master rocks</a> table with an <span class="tag impl">Implemented</span> row.</p>
<table><thead><tr><th>Horizon item</th><th>Today</th><th>Proposed</th><th>Label</th></tr></thead>
<tbody>
<tr><td>GPU Landauer joules</td><td><code>entropyThisFrame</code> proxy</td><td>Calibrated package power correlation</td><td><span class="tag meta">Metaphor</span> → future <span class="tag impl">Implemented</span></td></tr>
<tr><td>DNSSEC wire validation</td><td>Stub counters + <code>dig +trace</code> discipline</td><td>Full validator in field-services stack</td><td><span class="tag meta">Metaphor</span> phase 2</td></tr>
<tr><td>Queen gate parity</td><td><code>QUEEN_READY</code> when built</td><td>All gate classes on production parity</td><td><span class="tag impl">Implemented</span> partial</td></tr>
<tr><td>Cross-host sovereign time</td><td>HMAC pulses + <code>SQUIDGIE</code> posture</td><td>Adversarial NTP soak tests</td><td><span class="tag impl">Implemented</span> posture</td></tr>
<tr><td>Hostess SDF at scale</td><td>Segment workflow + human plates</td><td>Cross-corpus ZAC monolith verify at scale</td><td><span class="tag meta">Metaphor</span> + <span class="tag impl">Implemented</span> doctrine</td></tr>
<tr><td>RF planetary shell</td><td><code>planetary_weave.comp</code> visual</td><td>Field Antenna + calibrated spectrum path</td><td><span class="tag vis">Visual</span> today</td></tr>
<tr><td>Sub-micron SEM tiers</td><td>Procedural Adept detail</td><td>Lab instrument correlation</td><td><span class="tag meta">Metaphor</span></td></tr>
<tr><td>KILROY daily driver</td><td>bzImage + QEMU boot</td><td>Production host parity on operator laptops</td><td><span class="tag impl">Implemented</span> image</td></tr>
</tbody></table>
<p><strong>Operator rule:</strong> Do not cite Horizon rows in status email as shipped. Cite grep from the validation table in <a href="chapters/01-preface.html">Chapter 1</a> or evidence anchors in the chapter you are defending.</p>
"""


def inject_horizon(body: str, chapter_key: str) -> str:
    if chapter_key != "22":
        return body
    if HORIZON_ID in body:
        return body
    return body + "\n" + HORIZON_HTML
"""High-fidelity mechanism schematics — wave, scoring, enforcement (SVG inline)."""

from __future__ import annotations

SCHEMATICS: dict[str, str] = {
    "03": """
<figure class="figure schematic" id="schematic-wave-cfl">
<svg viewBox="0 0 720 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Wave CFL phase diagram">
  <rect width="720" height="200" fill="#0a1020" rx="8"/>
  <text x="24" y="28" fill="#8ec8ff" font-family="monospace" font-size="14">Wave phases — host guard before dispatch</text>
  <rect x="40" y="50" width="120" height="56" fill="#1a2840" stroke="#38bdf8" rx="4"/>
  <text x="52" y="72" fill="#e2e8f0" font-size="11">1. Sample Φ, Flow</text>
  <text x="52" y="90" fill="#94a3b8" font-size="10">harmonics read</text>
  <path d="M160 78h40" stroke="#38bdf8" marker-end="url(#arr)"/>
  <rect x="200" y="50" width="140" height="56" fill="#1a2840" stroke="#f0d060" rx="4"/>
  <text x="212" y="72" fill="#e2e8f0" font-size="11">2. CFL check</text>
  <text x="212" y="90" fill="#94a3b8" font-size="10">c·Δt/Δx ≤ 1</text>
  <path d="M340 78h40" stroke="#38bdf8"/>
  <rect x="380" y="50" width="120" height="56" fill="#1a2840" stroke="#4ade80" rx="4"/>
  <text x="392" y="72" fill="#e2e8f0" font-size="11">3. Scale dt</text>
  <text x="392" y="90" fill="#94a3b8" font-size="10">or refuse step</text>
  <path d="M500 78h40" stroke="#38bdf8"/>
  <rect x="540" y="50" width="140" height="56" fill="#1a2840" stroke="#a78bfa" rx="4"/>
  <text x="552" y="72" fill="#e2e8f0" font-size="11">4. vkCmdDispatch</text>
  <text x="552" y="90" fill="#94a3b8" font-size="10">fabric evolve</text>
  <text x="40" y="150" fill="#64748b" font-size="10">Evidence: grep CFL / harmonics in run.log — Ch 3, 9</text>
  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#38bdf8"/></marker></defs>
</svg>
<figcaption>Figure 3.S — Wave phase pipeline: sample → CFL guard → scale → dispatch. <span class="tag impl">Implemented</span> host path.</figcaption>
</figure>
""",
    "05": """
<figure class="figure schematic" id="schematic-gatekeeper">
<svg viewBox="0 0 720 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Gatekeeper scoring pipeline">
  <rect width="720" height="220" fill="#0a1020" rx="8"/>
  <text x="24" y="28" fill="#8ec8ff" font-family="monospace" font-size="14">Enforcement topology — ten-axis scorer</text>
  <rect x="30" y="48" width="100" height="40" fill="#1e293b" stroke="#64748b" rx="3"/><text x="42" y="72" fill="#e2e8f0" font-size="10">socket TX/RX</text>
  <rect x="30" y="100" width="100" height="40" fill="#1e293b" stroke="#64748b" rx="3"/><text x="42" y="124" fill="#e2e8f0" font-size="10">field jsonl</text>
  <path d="M130 68h50v64h50" stroke="#38bdf8" fill="none"/>
  <rect x="230" y="70" width="160" height="80" fill="#1a2840" stroke="#f0d060" rx="4"/>
  <text x="242" y="92" fill="#f0d060" font-size="11">Connection Gatekeeper</text>
  <text x="242" y="110" fill="#94a3b8" font-size="9">axis₁…axis₁₀ → score</text>
  <text x="242" y="128" fill="#94a3b8" font-size="9">watchlist before KILL</text>
  <path d="M390 110h50" stroke="#38bdf8"/>
  <rect x="440" y="55" width="110" height="36" fill="#14532d" stroke="#4ade80" rx="3"/><text x="452" y="77" fill="#bbf7d0" font-size="10">USER_OK</text>
  <rect x="440" y="100" width="110" height="36" fill="#422006" stroke="#fbbf24" rx="3"/><text x="452" y="122" fill="#fde68a" font-size="10">SUSPICIOUS</text>
  <rect x="440" y="145" width="110" height="36" fill="#450a0a" stroke="#f87171" rx="3"/><text x="452" y="167" fill="#fecaca" font-size="10">HARM_CANDIDATE</text>
  <rect x="580" y="85" width="110" height="50" fill="#1a2840" stroke="#a78bfa" rx="4"/>
  <text x="592" y="108" fill="#e2e8f0" font-size="10">Panel :9477</text>
  <text x="592" y="124" fill="#94a3b8" font-size="9">human correlate</text>
  <text x="30" y="195" fill="#64748b" font-size="10">Local scope only — not cloud omniscience. Ch 5, 11.</text>
</svg>
<figcaption>Figure 5.S — Scoring pipeline: jsonl + sockets → ten-axis gatekeeper → tiered verdict → panel. <span class="tag impl">Implemented</span> local.</figcaption>
</figure>
""",
    "07": """
<figure class="figure schematic" id="schematic-dispatch">
<svg viewBox="0 0 720 180" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Dispatch enforcement topology">
  <rect width="720" height="180" fill="#0a1020" rx="8"/>
  <text x="24" y="28" fill="#8ec8ff" font-family="monospace" font-size="14">AMOURANTHRTX dispatch spine</text>
  <rect x="40" y="50" width="90" height="44" fill="#1e293b" stroke="#64748b" rx="3"/><text x="52" y="76" fill="#e2e8f0" font-size="10">main loop</text>
  <path d="M130 72h36" stroke="#38bdf8"/>
  <rect x="166" y="50" width="130" height="44" fill="#1a2840" stroke="#38bdf8" rx="3"/><text x="178" y="76" fill="#e2e8f0" font-size="10">dispatch_canvas()</text>
  <path d="M296 72h36" stroke="#38bdf8"/>
  <rect x="332" y="42" width="200" height="60" fill="#1a2840" stroke="#a78bfa" rx="4"/>
  <text x="344" y="62" fill="#c4b5fd" font-size="10">bindings 1,2,8,9,10</text>
  <text x="344" y="78" fill="#94a3b8" font-size="9">Die · ThermoAcct · Φ Thermo Flow</text>
  <text x="344" y="94" fill="#94a3b8" font-size="9">FIELD_LAYOUT_VERSION=5</text>
  <path d="M532 72h36" stroke="#38bdf8"/>
  <rect x="568" y="50" width="120" height="44" fill="#1a2840" stroke="#4ade80" rx="3"/><text x="580" y="76" fill="#e2e8f0" font-size="10">x86.comp default</text>
  <text x="40" y="140" fill="#64748b" font-size="10">grep FIELD_LAYOUT_VERSION Navigator/engine/Pipeline.cpp</text>
</svg>
<figcaption>Figure 7.S — Enforcement topology: thin host, GPU dispatch, layout contract. <span class="tag impl">Implemented</span>.</figcaption>
</figure>
""",
}


def inject_schematics(body: str, chapter_key: str) -> str:
    block = SCHEMATICS.get(chapter_key)
    if not block:
        return body
    if 'class="figure schematic"' in body:
        return body
    marker = '<div class="evidence-anchor"'
    if marker in body:
        return body.replace(marker, block + "\n" + marker, 1)
    return body + "\n" + block
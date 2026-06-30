"""Per-chapter evidence anchors — equations, grep hooks, source paths, labels."""

from __future__ import annotations

import html

# (title, claim, label, evidence)
Row = tuple[str, str, str, str]

TECHNICAL_ANCHORS: dict[str, dict[str, object]] = {
    "01": {
        "rows": [
            ("Field definition", "Continuous quantity over addressable space", "impl", "Bindings 8–10, SSBO 1, NEXUS jsonl"),
            ("Three axioms", "3D / linear time / movable energy", "phil", "Constraints on honest sentences"),
            ("God preface", "Truth, Math, Existence", "phil", "Optional sacred track — Ch 16–18"),
            ("Week-zero drill", "Dispatch alive", "impl", "./linux.sh run 2>&1 | grep THERMO"),
        ],
        "eq": "Φ, Thermo, Flow @ bindings 8–10  |  FieldX86Die @ binding 1  |  packet field @ NEXUS jsonl",
        "grep": "grep -E 'FIELD_LAYOUT_VERSION|createAnalogFieldFabric' Navigator/engine/ -r",
        "sources": ["content/chapters/01.html", "docs/data/image-manifest.json", "Navigator/engine/main.cpp"],
    },
    "02": {
        "rows": [
            ("Scalar Thermo", "Heat density per texel", "impl", "Binding 9 storage image"),
            ("Vector Flow", "Gradients in .gb", "impl", "Binding 10"),
            ("Telemetry bus", "64 words per dispatch", "impl", "data_bus[] packed dashboard"),
            ("Host PDE", "CPU fabric solver", "meta", "Explicitly refused — GPU dispatch only"),
        ],
        "eq": "∇²Φ discrete Laplacian on fabric grid  |  data_bus[i] telemetry, not texel(i)",
        "grep": "grep -n 'createAnalogFieldFabric' Navigator/engine/RayCanvas.cpp",
        "sources": ["Navigator/engine/RayCanvas.cpp", "Navigator/shaders/CANVAS.comp", "Navigator/shaders/x86.comp"],
    },
    "03": {
        "rows": [
            ("Cross-coupling", "Energy moves between channels", "impl", "FieldCoupling in fabric evolution"),
            ("CFL wave guard", "c·Δt/Δx ≤ 1", "impl", "Host harmonics before dispatch"),
            ("Thermo proxy", "entropyThisFrame", "meta", "Proxy — not package joules"),
            ("Sealed time", "Linear session clock", "impl", "TotalTime::seal() each frame"),
        ],
        "eq": "c·Δt/Δx ≤ 1  |  α·Δt/Δx² ≤ 1  |  Ṡ_proxy ≈ fieldWork + probeDiss + prevMaint",
        "grep": "./linux.sh run 2>&1 | grep -E 'THERMO|CFL|harmonics'",
        "sources": ["Navigator/engine/Pipeline.cpp", "Navigator/shaders/CANVAS.comp", "Navigator/engine/AnalogFields.hpp"],
    },
    "04": {
        "rows": [
            ("ThermoAccountant", "GPU entropy proxy", "meta", "Binding 2 — labeled proxy"),
            ("Fabric entropy floor", "Seed irreversibility", "impl", "Fabric init + evolution"),
            ("Shannon oracle", "File byte surprise", "impl", "NEXUS Entropy Oracle — separate layer"),
            ("Layer conflation", "One entropy number", "phil", "Forbidden — three plates never summed"),
        ],
        "eq": "E_min = k_B T ln 2 (theory)  |  H = −Σ pᵢ log₂ pᵢ (files)  |  entropyThisFrame (proxy)",
        "grep": "grep -r 'entropyThisFrame' Navigator/engine/",
        "sources": ["Navigator/engine/ThermoAccountant.hpp", "NEXUS-Shield/entropy_oracle.py"],
    },
    "05": {
        "rows": [
            ("Packet field", "Local socket sentences", "impl", "field jsonl archive"),
            ("Gatekeeper", "Ten-axis scoring", "impl", "USER_OK / SUSPICIOUS / HARM_CANDIDATE"),
            ("Watchlist", "Restraint before KILL", "impl", "Operator override path"),
            ("Cloud omniscience", "Internet-wide vision", "meta", "Rejected — local scope only"),
        ],
        "eq": "verdict = score(axis₁…axis₁₀) → tier",
        "grep": "./nexus.sh  # panel :9477  |  tail field jsonl",
        "sources": ["NEXUS-Shield/connection_gatekeeper.py", "NEXUS-Shield/threat-panel.json"],
    },
    "06": {
        "rows": [
            ("Planetary weave", "RF shell shader art", "vis", "planetary_weave.comp"),
            ("Field Antenna", "JSON RF panels", "impl", "Field Antenna module"),
            ("Phi binding 8", "Fabric potential", "meta", "Not spectrum analyzer"),
            ("FSPL", "Free-space path loss", "meta", "Paper equation — not in shader SI"),
        ],
        "eq": "FSPL ∝ 20·log₁₀(d) + 20·log₁₀(f)  |  R_RF shell layer (visual)",
        "grep": "grep -r 'planetary_weave' Navigator/shaders/",
        "sources": ["Navigator/shaders/planetary_weave.comp", "NEXUS-Shield/field_antenna.json"],
    },
    "07": {
        "rows": [
            ("Dispatch spine", "vkCmdDispatch each tick", "impl", "Pipeline::dispatch_canvas()"),
            ("Layout contract", "FIELD_LAYOUT_VERSION = 5", "impl", "Host/shader struct match"),
            ("Default canvas", "x86.comp Field Die", "impl", "./linux.sh run path"),
            ("Thin host", "No CPU fabric PDE", "impl", "Architectural invariant"),
        ],
        "eq": "main → dispatch_canvas() → vkCmdDispatch(groupsX, groupsY, 1)",
        "grep": "grep -n 'dispatch_canvas\\|FIELD_LAYOUT_VERSION' Navigator/engine/Pipeline.cpp",
        "sources": ["Navigator/engine/main.cpp", "Navigator/engine/Pipeline.cpp", "Navigator/shaders/x86.comp"],
    },
    "08": {
        "rows": [
            ("FieldX86Die", "64 MiB guest map", "impl", "SSBO binding 1"),
            ("VGA field", "0xB8000 text buffer", "impl", "Guest subfield"),
            ("data_bus", "64-word telemetry", "impl", "Slots 0–63 per dispatch"),
            ("Pump L0–L9", "Layer sync", "impl", "FieldLayer::pumpAll()"),
        ],
        "eq": "guest[offset] ∈ [0, 64MiB)  |  VGA @ 0xB8000  |  C mirror @ 0x01000000",
        "grep": "grep -n 'FieldX86Die\\|data_bus' Navigator/shaders/x86.comp",
        "sources": ["Navigator/shaders/x86.comp", "Navigator/engine/FieldLayer.cpp"],
    },
    "09": {
        "rows": [
            ("Wave CFL", "Stability before step", "impl", "Host guard scales unsafe dt"),
            ("Tesla bias", "Directional preference", "meta", "TESLA_R_* → data_bus 31/34"),
            ("FCC bus slots", "Telemetry floats", "impl", "data_bus[16–23]"),
            ("Fluidic valve", "Physical Tesla part", "meta", "Not in chassis"),
        ],
        "eq": "forward ease / reverse drag via TESLA_R_* constants",
        "grep": "grep -E 'TESLA_R_|waveCFL' Navigator/engine/",
        "sources": ["Navigator/engine/HarmonicsGuard.cpp", "Navigator/engine/FCC.cpp"],
    },
    "10": {
        "rows": [
            ("hardwareFabric", "Spiderweb graph mirror", "impl", "updateHardwareFromAnalogFields()"),
            ("Fabric averages", "Dashboard compression", "meta", "Lossy — not SEM"),
            ("Adept tier", "SimulateSubMicron", "meta", "Procedural detail — not lab SEM"),
            ("list Hardware", "Operator readout", "impl", "Prompt terminal command"),
        ],
        "eq": "util(core) ← sample(avg(Phi, Thermo, Flow))",
        "grep": "grep -n 'hardwareFabric' Navigator/engine/",
        "sources": ["Navigator/engine/Spiderweb.cpp", "Navigator/engine/rtx.cpp"],
    },
    "11": {
        "rows": [
            ("ELLIE categories", "Categorized stderr", "impl", "MAIN/VULKAN/CANVAS/THERMO/STATUS"),
            ("Panel :9477", "Human correlation UI", "impl", "NEXUS local panel"),
            ("Screenshot culture", "Pretty frames as proof", "phil", "Rejected — grep first"),
            ("Operator journal", "Weekly rhythm", "phil", "Receipts over vibes"),
        ],
        "eq": "observability = stderr_categories × panel_correlation × jsonl_archive",
        "grep": "grep -E '^(MAIN|VULKAN|THERMO)' run.log | tail -40",
        "sources": ["Navigator/engine/ELLIE.hpp", "NEXUS-Shield/panel_server.py"],
    },
    "12": {
        "rows": [
            ("Honesty table", "Claim vs operator reality", "impl", "This chapter — bookmark"),
            ("Trust order", "Headers > stderr > art", "phil", "Dispute resolution"),
            ("Capstone equations", "Layer-tagged math", "meta", "Theory vs proxy vs file H"),
            ("Product boundaries", "Four licenses", "impl", "AMOURANTHRTX / NEXUS / Queen / Primer"),
        ],
        "eq": "See capstone table — CFL, Landauer, Shannon, entropy proxy",
        "grep": "grep -r 'tag impl\\|tag meta' docs/chapters/12-reality-theory.html",
        "sources": ["content/chapters/12.html", "scripts/master_rocks_table.py"],
    },
    "13": {
        "rows": [
            ("Landauer floor", "k_B T ln 2 per bit erased", "meta", "Theory — GPU uses proxy"),
            ("ThermoAccountant", "Operational receipt", "meta", "entropyThisFrame integral"),
            ("Comparative sessions", "Δproxy across runs", "impl", "Valid grep science"),
            ("Wattmeter billing", "Package power as Landauer", "meta", "Explicit rock — forbidden"),
        ],
        "eq": "E_min = k_B T ln 2  |  ΔS_proxy between sealed sessions",
        "grep": "grep THERMO run.log | awk '{print $NF}' | sort -n | tail -5",
        "sources": ["docs/creditors/landauer.html", "Navigator/engine/ThermoAccountant.hpp"],
    },
    "14": {
        "rows": [
            ("Shannon H", "File byte surprise", "impl", "NEXUS Entropy Oracle"),
            ("Storm thresholds", "Alert tiers on H", "impl", "Configurable gates"),
            ("Fabric texel H", "Shader spectrum", "meta", "Category error if merged"),
            ("Gatekeeper merge", "Verdict from H alone", "meta", "Forbidden — separate plates"),
        ],
        "eq": "H = −Σ pᵢ log₂ pᵢ  on file byte distribution",
        "grep": "grep -r 'entropy_oracle\\|storm' NEXUS-Shield/",
        "sources": ["NEXUS-Shield/entropy_oracle.py", "docs/creditors/shannon.html"],
    },
    "15": {
        "rows": [
            ("Maxwell coupling", "Neighbor texel exchange", "impl", "Discrete stencil on fabric"),
            ("Wave equation", "Phi evolution", "impl", "CANVAS.comp / fabric shaders"),
            ("Continuous Maxwell", "Full EM PDE on GPU", "meta", "Electrical metaphor only"),
            ("Binding proof", "Implementation anchor", "impl", "Bindings 8–10 evolution"),
        ],
        "eq": "∂²Φ/∂t² ∝ ∇²Φ (discrete)  |  neighbor coupling each dispatch",
        "grep": "grep -n 'Laplacian\\|WaveSpeed' Navigator/shaders/CANVAS.comp",
        "sources": ["Navigator/shaders/CANVAS.comp", "docs/creditors/maxwell.html"],
    },
    "16": {
        "rows": [
            ("Love as coupling", "Ethical dispatch weight", "phil", "Sacred track — Ch 16"),
            ("FieldCoupling", "Channel listening", "impl", "Shader coupling + phil metaphor"),
            ("Consent", "No silent exfiltration", "phil", "Operator covenant aligned"),
            ("CFL ethics", "Stability as neighbor care", "phil", "Math shared with Ch 9"),
        ],
        "eq": "coupled_evolution: dispatch(A) → state(B_next_tick)",
        "grep": "Read Ch 12 labels before citing this chapter in status email",
        "sources": ["content/chapters/16.html", "docs/creditors/love-and-god.html"],
    },
    "17": {
        "rows": [
            ("God as Truth", "Survives grep", "phil", "Sacred track — Ch 17"),
            ("Holographic boundary", "2D presentation of 3D state", "meta", "Engineering edge + phil"),
            ("avgBoundaryThermo", "Boundary cost proxy", "meta", "grep THERMO — not joules"),
            ("stderr sacrament", "Logs before awe", "phil", "Operator habit"),
        ],
        "eq": "presentation_cost → avgBoundaryThermo (proxy)",
        "grep": "grep avgBoundaryThermo run.log",
        "sources": ["content/chapters/17.html", "content/chapters/12.html"],
    },
    "18": {
        "rows": [
            ("Six clauses", "Operator covenant", "phil", "Teach / local / creditors / love / God / gates"),
            ("No police", "Habit + reputation", "phil", "Not legal enforcement"),
            ("grep Monday", "Spirit signature", "phil", "Practical audit"),
            ("Clause VI hold gates", "Queen alignment", "impl", "When QUEEN_READY"),
        ],
        "eq": "covenant_compliance = labels_correct × grep_habit × gate_discipline",
        "grep": "Self-audit: five honesty rows from Ch 12 from memory",
        "sources": ["content/chapters/18.html"],
    },
    "19": {
        "rows": [
            ("TotalTime::seal()", "Session genesis lock", "impl", "FieldSocket sealed_time"),
            ("Sovereign pulse", "HMAC time forward", "impl", "sovereign-time.py"),
            ("SQUIDGIE", "Verify fail verdict", "impl", "Terror-threat posture"),
            ("Pool consensus alone", "NTP trust", "meta", "Insufficient — operator-owned"),
        ],
        "eq": "seal → pulse → verify → USER_OK | SQUIDGIE",
        "grep": "NEXUS_SOVEREIGN_TIME_BIND=127.0.0.1 python3 sovereign-time.py serve",
        "sources": ["NEXUS-Shield/sovereign-time.py", "Navigator/engine/TotalTime.cpp"],
    },
    "20": {
        "rows": [
            ("Truth DNS", "127.0.0.1 loopback", "impl", "field-dns.py"),
            ("Field DHCP", "Issue + verify always", "impl", "field-dhcp.py v3 schema"),
            ("dig +trace", "Root trace discipline", "impl", "No resolver shortcut"),
            ("DNSSEC marketing", "Full wire validation", "meta", "stub_trace honest phase 2"),
        ],
        "eq": "OFFER after ping_conflict_check; option 6 → loopback DNS",
        "grep": "python3 field-services-2026.py json",
        "sources": ["NEXUS-Shield/field-dns.py", "NEXUS-Shield/field-dhcp.py", "NEXUS-Shield/field-services-2026.py"],
    },
    "21": {
        "rows": [
            ("QUEEN_READY", "Integrated browser gates", "impl", "Build flag QUEEN_BROWSER_BUILD"),
            ("WebRTC gated", "Not amputated", "impl", "Through Connection Gatekeeper"),
            ("Hostess 7 SDF", "Segment plate doctrine", "meta", "Not fMRI — procedural"),
            ("Robot-brain stack", "In-process recall", "meta", "Architecture metaphor"),
        ],
        "eq": "all_gates_held = WebRTC + EME + COOP/COEP + thermo_per_context",
        "grep": "grep -r 'QUEEN_READY\\|QUEEN_BROWSER_BUILD' Navigator/",
        "sources": ["Navigator/queen-browser/", "Hostess7/scripts/field_hostess_sdf_storage.py"],
    },
    "22": {
        "rows": [
            ("Glossary", "Canonical term readings", "impl", "This chapter"),
            ("Master rocks", "Consolidated honesty", "impl", "#master-rocks appendix"),
            ("Disambiguation", "Overload splits", "impl", "Phi vs RF vs entropy layers"),
            ("Linear read", "Required?", "phil", "Grep table — don't read A–Z linearly"),
        ],
        "eq": "term_status ∈ {Implemented, Metaphor, Philosophy, Visual}",
        "grep": "Anchor: #master-rocks in this chapter",
        "sources": ["content/chapters/22.html", "scripts/master_rocks_table.py"],
    },
}

TAG = {
    "impl": '<span class="tag impl">Implemented</span>',
    "meta": '<span class="tag meta">Metaphor</span>',
    "phil": '<span class="tag phil">Philosophy</span>',
    "vis": '<span class="tag vis">Visual</span>',
}


def _anchor_html(key: str, data: dict[str, object]) -> str:
    rows: list[Row] = data["rows"]  # type: ignore[assignment]
    trs = "".join(
        f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td>"
        f"<td>{TAG.get(c, c)}</td><td><code>{html.escape(d)}</code></td></tr>"
        for a, b, c, d in rows
    )
    eq = html.escape(str(data.get("eq", "")))
    grep = html.escape(str(data.get("grep", "")))
    sources = data.get("sources", [])
    src_li = "".join(f"<li><code>{html.escape(s)}</code></li>" for s in sources)
    return f"""
<div class="evidence-anchor" id="evidence-ch{key}">
<h2>Evidence anchor — grep and sources</h2>
<p>Major claims in this chapter anchored for reproducibility. <span class="tag impl">Implemented</span> = grep today; <span class="tag meta">Metaphor</span> = intuition; <span class="tag phil">Philosophy</span> = discipline.</p>
<table><thead><tr><th>Claim</th><th>Statement</th><th>Label</th><th>Evidence</th></tr></thead>
<tbody>{trs}</tbody></table>
<pre class="eq">{eq}</pre>
<pre class="eq">{grep}</pre>
<h3>Source paths</h3>
<ul class="source-anchors">{src_li}</ul>
</div>
"""


def inject_technical_anchors(body: str, chapter_key: str) -> str:
    if chapter_key not in TECHNICAL_ANCHORS:
        return body
    if f'id="evidence-ch{chapter_key}"' in body:
        return body
    block = _anchor_html(chapter_key, TECHNICAL_ANCHORS[chapter_key])
    marker = '<div class="chapter-summary-box">'
    if marker in body:
        return body.replace(marker, block + "\n" + marker, 1)
    return body + "\n" + block
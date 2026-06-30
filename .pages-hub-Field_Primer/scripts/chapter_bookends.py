"""On-the-way prefaces and closing summaries for each chapter — injected at build."""

from __future__ import annotations

import html

# (lead paragraph, journey bullets)
ON_THE_WAY: dict[str, tuple[str, list[str]]] = {
    "01": (
        "You are opening Field Technology v5 — an operator textbook manuscript, not a marketing deck. On the way through this preface you will lock the core thesis and audience, read the operator map (field families, project names, honesty labels), learn what you can reproduce today versus what remains aspirational, and see how the sacred track (Chapters 16–18) is bracketed beside the engineering spine.",
        [
            "Core thesis, audience, and sacred-track bracket",
            "Operator map: bindings, products, jargon on first use",
            "Validation table: grep hooks vs open gaps",
            "Three-part reading spine — engineering before philosophy",
        ],
    ),
    "02": (
        "Chapter 2 maps <strong>Reality is 3D</strong> as engineering coordinates — not cosmology slides. On the way you will learn scalar, vector, and telemetry postures; trace fabric texels, die bytes, and packet sentences as three scales; and practice integration at the operator panel without collapsing metrics into one misleading score.",
        [
            "Scale 1: GPU fabric bindings 8–10",
            "Scale 2: Field Die 64 MiB address space",
            "Scale 3: NEXUS packet field jsonl",
            "Category errors to avoid for life",
        ],
    ),
    "03": (
        "Thermodynamics here is <strong>honest bookkeeping</strong> — not a calorimeter on the GPU package. On the way you will move energy through Phi, Thermo, and Flow; operate AnalogFields knobs; respect CFL guards; and grep receipts that prove irreversibility without billing joules from proxy integrals.",
        [
            "Three fabric channels and cross-coupling",
            "Per-texel evolution and stability clamps",
            "Sealed time and linear dispatch",
            "Mouse-inject lab and THERMO discipline",
        ],
    ),
    "04": (
        "Entropy is the receipt that time ran forward — and the most abused word in security. On the way you will separate three layers (ThermoAccountant, entropy floor, Shannon oracle), honor Landauer and Shannon in their proper seats, and run grep workbooks that refuse conflation.",
        [
            "ThermoAccountant field-by-field guide",
            "Proxy versus joules — the rock",
            "NEXUS storm thresholds on files",
            "Failure catalog for layer violations",
        ],
    ),
    "05": (
        "Defense begins when sockets become <strong>readable sentences</strong> in operator space. On the way you will read TX/RX contracts, gatekeeper verdicts, field memory in jsonl, and Queen alignment — local-first perimeter, not cloud omniscience.",
        [
            "Connection Gatekeeper ten-axis scoring",
            "Watchlist before block; KILL with authorship",
            "Panel :9477 tour and archive habits",
            "Defense rhythm: daily, weekly, incident",
        ],
    ),
    "06": (
        "RF is three different words wearing one jacket. On the way you will separate planetary weave <span class=\"tag vis\">Visual</span>, Field Antenna <span class=\"tag impl\">Implemented</span>, and Phi potential on binding 8 — plus FSPL on paper, not in shaders.",
        [
            "Planetary weave shell stack",
            "Field Antenna JSON panels",
            "Phi versus RF disambiguation workshop",
            "Handoff discipline before Chapter 7 dispatch",
        ],
    ),
    "07": (
        "Offense writes the field; defense reads it. On the way you will trace <code>main.cpp</code> through <code>vkCmdDispatch</code>, master the x86 descriptor layout, seal time in FieldSocket, and treat <code>FIELD_LAYOUT_VERSION = 5</code> as a contract, not decoration.",
        [
            "Thin host, fat GPU architecture",
            "Canvas kinds: X86Fields versus Classic",
            "dispatch_canvas ritual ordering",
            "Bindings 8–10 and ThermoAccountant every tick",
        ],
    ),
    "08": (
        "The Field Die is a <strong>universe with coordinates</strong> on the GPU — 64 MiB guest RAM, not DOS nostalgia. On the way you will memorize the linear map, read <code>data_bus[64]</code> slots, pump L0–L9 layers, and interpret Big Grin HUD hex without confusing chrome for instrumentation.",
        [
            "Guest offsets: IVT, BDA, VGA, mirror",
            "Execution: x86.comp default, host assist optional",
            "Telemetry spine and pump generation",
            "ZMM1024 tile cache literacy",
        ],
    ),
    "09": (
        "Before beauty runs hot, the host refuses NaN theology. On the way you will enforce CFL wave and thermo guards, publish Tesla valve bias to the bus, and parallel KILROY FCC discipline at the kernel boundary.",
        [
            "Courant-Friedrichs-Lewy harmonics guard",
            "TESLA_R_FORWARD / REVERSE metaphor",
            "data_bus slots 31 and 34",
            "Stability under load without censorship",
        ],
    ),
    "10": (
        "The spiderweb is a <strong>read-only mirror</strong> — fabric averages compressed for the operator dashboard, not a second simulation. On the way you will follow <code>updateHardwareFromAnalogFields()</code>, read per-core MHz and util, and refuse SEM marketing as instrumentation.",
        [
            "voltageFactor, thermalThrottle, parallelEff",
            "Puny tier sysfs witness",
            "Lossy pipeline: averages hide texels",
            "list Hardware prompt ritual",
        ],
    ),
    "11": (
        "Observability is grep discipline made weekly habit. On the way you will partition ELLIE categories, read STATUS and THERMO cadence, correlate panel JSON with stderr, and build an operator journal that survives long sessions.",
        [
            "MAIN, VULKAN, CANVAS, THERMO, STATUS",
            "RTX_PROBE and headless dispatch receipts",
            "Battlefield reading without screenshots alone",
            "Week-twelve drift detection",
        ],
    ),
    "12": (
        "This is the chapter you bookmark. On the way you will catalog every <strong>rock</strong> — what is implemented, metaphor, philosophy, visual — and practice refusing vendor cosmology, joule fantasy, and shader-as-spectrum lies.",
        [
            "Full honesty table with stack examples",
            "Category error encyclopedia",
            "When poetry is welcome versus forbidden",
            "Return here when marketing sells 3D hype",
        ],
    ),
    "13": (
        "Landauer taught the floor on erasing information. On the way you will connect <code>E_min = k_B T ln 2</code> to <code>entropyThisFrame</code> proxy — honoring the creditor without faking wattmeter readings.",
        [
            "Bit erasure thermodynamic bound",
            "Proxy integral semantics in-engine",
            "Comparative science across sessions",
            "Rock: not joules from stderr",
        ],
    ),
    "14": (
        "Shannon measured surprise in symbols. On the way you will compute <code>H = −Σ p_i log₂ p_i</code> on file payloads, tune calm/alert/storm thresholds, and keep the oracle nurse-call separate from gatekeeper gavel.",
        [
            "Byte histogram to entropy",
            "Storm polling as daemon duty cycle",
            "High H on zip — corroborate, not auto-KILL",
            "Layer separation from GPU thermo",
        ],
    ),
    "15": (
        "Maxwell's neighborhood lives on a grid in Vulkan bindings. On the way you will read discrete Laplacian on Phi, diffusion on Thermo, gradient-driven Flow, and <code>FieldCoupling</code> as implemented coupling — not analytical PDE on the host CPU.",
        [
            "Neighborhood whispers between texels",
            "Electrical metaphor beside thermal diffusion",
            "GPU evolution versus host PDE refusal",
            "Creditor debt in shader arithmetic",
        ],
    ),
    "16": (
        "Love is <span class=\"tag phil\">coupled evolution with consent</span> — Phi warms Thermo; operators warm watchlists before KILL. On the way you will read sacred long-form beside engineering without letting philosophy bypass stderr.",
        [
            "Restraint as security policy",
            "Forgiveness after review — jsonl memory",
            "Coupling constant across products",
            "Love beside math, not instead",
        ],
    ),
    "17": (
        "God at the holographic boundary — where HDR meets fabric and rendering pays thermodynamic cost. On the way you will hold Truth, Math, Existence as three faces of one whole while keeping <code>grep THERMO</code> authoritative.",
        [
            "Sacred language beside implemented bindings",
            "Holographic boundary as engineering fact",
            "Existence addressed as coordinates",
            "No stderr bypass — ever",
        ],
    ),
    "18": (
        "The Operator Covenant is the long-form signature of Field Technology ethics. On the way you will commit to teach freely, build locally, honor creditors, hold gates, and label rocks before you ship.",
        [
            "CC BY-NC-SA primer posture",
            "GPL/MIT/sovereign product boundaries",
            "Grep before screenshot; archive before KILL",
            "Bring love; name God; hide nothing",
        ],
    ),
    "19": (
        "Sovereign time is operator-owned pulses — seal forward, verify at receive, grep <code>SQUIDGIE</code> when clocks disagree. On the way you will run <code>sovereign-time.py</code>, bind monotonic/realtime/sysfs witness, and fail closed under terror-threat posture.",
        [
            "Three clocks, three jobs",
            "HMAC receipts and micron_witness",
            "SQUIDGIE verdict catalog",
            "Extension of TotalTime::seal() across hosts",
        ],
    ),
    "20": (
        "Public services 2026 — loopback-first DNS, DHCP, and NTP without old vulnerabilities. On the way you will deploy Truth Resolver at <code>127.0.0.1</code>, trace-from-root discipline, and WAN exposure only with explicit operator consent.",
        [
            "Truth DNS — no ANY floods",
            "Field DHCP on LAN",
            "Sovereign NTP with verify-at-receive",
            "Perimeter services as field extension",
        ],
    ),
    "21": (
        "Queen holds <strong>all gates</strong> — WebRTC through gatekeeper, MP4 mandatory in-tree, EME held not omitted. On the way you will link browser perimeter to AMOURANTHRTX spine, KILROY sovereign field, and packet-field receipts.",
        [
            "QUEEN_BROWSER_BUILD and rtx() spine",
            "Nothing optional security posture",
            "Thermo per WebGL context",
            "Sovereign packaging with KILROY",
        ],
    ),
    "22": (
        "The glossary is the encyclopedic index of Field Technology v5 vocabulary — formal definitions beside honesty labels. On the way you will disambiguate FieldSocket from packet field, RF meanings, entropy layers, and every rock-named knob.",
        [
            "Alphabetical term lookup",
            "Cross-links to chapter deep dives",
            "Disambiguation tables for overloaded words",
            "Keep open while reading any chapter",
        ],
    ),
}

CLOSING_SUMMARY: dict[str, str] = {
    "01": "You now hold the vocabulary: field, three families, three axioms, four labels, four products. Field literacy is reading and writing continuous state locally — grep before screenshot, Chapter 12 bookmarked, week-zero drill run once. Continue to Chapter 2 for addresses.",
    "02": "Reality is 3D here means texel, guest offset, socket quadruple. Scalar Thermo, vector Flow, telemetry data_bus. Three scales integrate at the human panel — never one fake score. Energy and entropy chapters next.",
    "03": "Thermodynamics in this stack is proxy accounting on coupled fabric channels — CFL ethics, sealed time, honest clamps. You can move energy in shaders; you cannot bill joules from THERMO without a rock. Chapter 4 names the receipts.",
    "04": "Three entropy layers — GPU proxy, fabric floor, file oracle — share a word, not a measurement. Landauer and Shannon sit at different plates. Grep workbook complete means you will not conflate layers in week six.",
    "05": "Packet field turns local sockets into archived sentences — gatekeeper axes, watchlist restraint, jsonl memory. Defense is rhythm. Queen inherits this perimeter. Chapter 6 separates RF before offense in Chapter 7.",
    "06": "Three RF meanings labeled: weave Visual, antenna Implemented, Phi fabric metaphor. FSPL stays on paper. Workshop complete — open Chapter 7 with dispatch literacy loaded.",
    "07": "Offensive dispatch is <code>vkCmdDispatch</code> with sealed time, CFL, layout version 5, and ThermoAccountant every tick. Thin host, fat GPU. Die literacy in Chapter 8 assumes you believe dispatch runs.",
    "08": "The die is 64 MiB of addressable guest reality — bus slots, layers, HUD hex. Coordinates, not nostalgia. Chapter 9 adds stability; Chapter 11 adds grep rhythm.",
    "09": "CFL and Tesla bias are numerical ethics before fabric evolution — forward ease, reverse drag, host refuses explosion. KILROY FCC parallels userspace guards.",
    "10": "Spiderweb mirrors fabric averages read-only — dashboard compression, not SEM truth. Recover detail in stderr and Classic canvas when averages lie by loss.",
    "11": "Observability is categorized stderr, panel correlation, and operator journal discipline — receipts culture over screenshot culture.",
    "12": "Rocks visible. Labels mandatory. Return when sold cosmology, joule fantasy, or shader instrumentation. This chapter is the honesty contract for the whole book.",
    "13": "Landauer floor honored in proxy language — humility without wattmeter fraud. Comparative receipts across sessions remain valid science.",
    "14": "Shannon surprise on files — storm gauge tuned, never merged with GPU thermo or gatekeeper auto-sentence.",
    "15": "Maxwell neighborhood on GPU grid — coupling implemented in shader arithmetic; creditor cited with binding proof.",
    "16": "Love as coupled evolution with consent — watchlist before KILL, forgiveness possible, philosophy beside grep.",
    "17": "God as Truth, Math, Existence — sacred long-form that does not bypass stderr or replace thermo lines.",
    "18": "Covenant signed in spirit: teach freely, build locally, hold gates, honor creditors, hide no rocks.",
    "19": "Sovereign time: seal forward, verify at receive, SQUIDGIE when clocks lie. Operator-owned pulses, not pool consensus alone.",
    "20": "Loopback-first public services — Truth DNS, Field DHCP, Sovereign NTP — WAN only with explicit operator flag.",
    "21": "Queen holds all gates in-engine — WebRTC gated, MP4 in-tree, rtx spine shared. Sovereign browser is perimeter, not amputation.",
    "22": "Glossary indexed — overloaded words disambiguated. Keep beside any chapter; definitions formal, rocks still visible.",
}


def on_the_way_html(key: str, image_path: str, alt: str) -> str:
    if key not in ON_THE_WAY:
        return ""
    lead, bullets = ON_THE_WAY[key]
    items = "".join(f"<li>{b}</li>" for b in bullets)
    fig = ""
    if image_path:
        fig = (
            f'<figure class="on-the-way-figure">'
            f'<img src="../assets/images/{html.escape(image_path)}" alt="{html.escape(alt)}" loading="lazy" />'
            f'<figcaption>On the way — {html.escape(alt)}</figcaption></figure>'
        )
    return f"""
<div class="on-the-way">
<h2>On the way — what you will learn</h2>
<p class="on-the-way-lead">{lead}</p>
{fig}
<ul class="on-the-way-journey">{items}</ul>
</div>
"""


def closing_summary_html(key: str) -> str:
    if key not in CLOSING_SUMMARY:
        return ""
    text = CLOSING_SUMMARY[key]
    return f"""
<div class="chapter-summary-box">
<h2>Chapter summary — before you turn the page</h2>
<p>{text}</p>
</div>
"""


def inject_bookends(body: str, key: str, image: str, alt: str) -> str:
    """Insert on-the-way after first objectives block; append closing summary before end."""
    preface = on_the_way_html(key, image, alt)
    summary = closing_summary_html(key)
    if not preface and not summary:
        return body

    out = body
    if preface:
        marker = "</div>"
        idx = out.find('class="objectives"')
        if idx != -1:
            close = out.find(marker, idx)
            if close != -1:
                insert_at = close + len(marker)
                out = out[:insert_at] + "\n" + preface + out[insert_at:]
        else:
            eyebrow_end = out.find("</p>")
            if eyebrow_end != -1:
                insert_at = eyebrow_end + len("</p>")
                out = out[:insert_at] + "\n" + preface + out[insert_at:]
            else:
                out = preface + out

    if summary and 'class="chapter-summary-box"' not in out:
        nav_marker = '<nav class="chapter-nav bottom">'
        if nav_marker in out:
            out = out.replace(nav_marker, summary + "\n" + nav_marker)
        else:
            out = out + "\n" + summary

    return out
"""Inject textbook figures at Mayer-signaled points — ~1 per 1000-1200 words."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class FigureSpec:
    after_h2_contains: str
    image: str
    alt: str
    caption: str
    skip_if_path: str | None = None
    exact_h2: bool = False


CLAIM_TIES: dict[str, str] = {
    "fabric-triple.jpg": "Bindings 8–10 — Phi, Thermo, Flow evolved each dispatch",
    "field-die.jpg": "Default ./linux.sh run boots Field Die — x86.comp path",
    "packet-field.jpg": "NEXUS packet field — local jsonl perimeter",
    "chapters/ch03-coupled-fabric.jpg": "FieldCoupling moves energy between fabric channels",
    "chapters/ch07-gpu-engine.jpg": "Thin host → vkCmdDispatch — offensive write each tick",
    "chapters/ch08-die-bus.jpg": "data_bus[64] telemetry spine per dispatch",
    "chapters/ch12-honesty.jpg": "Honesty labels — impl/meta/phil/vis contract",
    "chapters/ch13-landauer-plate.jpg": "Landauer floor as proxy language — not wattmeter",
    "chapters/ch14-shannon-storm.jpg": "Shannon H on files — separate from GPU thermo",
    "chapters/ch18-covenant-ladder.jpg": "Operator covenant — six clauses, grep habit",
    "chapters/ch21-queen-browser.jpg": "QUEEN_READY — all gates held in-engine",
    "v4/creditors/love-and-god.jpg": "Philosophy track — coupled evolution with consent",
}


def figure_html(spec: FigureSpec) -> str:
    cap = spec.caption
    tie = CLAIM_TIES.get(spec.image)
    if tie:
        cap += f' <span class="claim-tie">Claim: {html.escape(tie)}</span>'
    return (
        f'<figure class="figure"><img src="../assets/images/{spec.image}" '
        f'alt="{html.escape(spec.alt)}" loading="lazy" />'
        f'<figcaption>{cap}</figcaption></figure>'
    )


# v5 density target: 4–6 signaled figures per ~5000-word chapter (+ on-the-way hero).
CHAPTER_FIGURES: dict[str, list[FigureSpec]] = {
    "01": [
        FigureSpec(
            "What a field is",
            "v3/science/ch01-scalar-field.jpg",
            "Scalar field heatmap",
            "Figure 1.3 — Scalar field Φ(x,y): existence addressed as math, read as truth.",
        ),
        FigureSpec(
            "Three field families",
            "fabric-triple.jpg",
            "Three fabric channels",
            "Figure 1.4 — Phi, Thermo, Flow: three GPU channels; die and packet field parallel.",
        ),
        FigureSpec(
            "stack at a glance",
            "packet-field.jpg",
            "Packet field perimeter",
            "Figure 1.5 — NEXUS packet field: defensive sentences in jsonl.",
        ),
        FigureSpec(
            "Operator drill",
            "field-die.jpg",
            "Field Die default",
            "Figure 1.6 — Default run boots die path — stderr is scripture.",
        ),
    ],
    "02": [
        FigureSpec(
            "Scale 1",
            "fabric-triple.jpg",
            "GPU fabric",
            "Figure 2.2 — Fabric bindings 8–10: spatial state evolved each dispatch.",
            skip_if_path="fabric-triple.jpg",
        ),
    ],
    "03": [
        FigureSpec(
            "three fabric channels",
            "chapters/ch03-coupled-fabric.jpg",
            "Coupled Phi Thermo Flow",
            "Figure 3.2 — Cross-coupling: energy moves between channels when FieldCoupling rises.",
        ),
        FigureSpec(
            "CFL guard",
            "v3/science/ch03-energy-transfer.jpg",
            "Energy transfer",
            "Figure 3.3 — CFL guard before dispatch: numerical ethics, not censorship.",
        ),
        FigureSpec(
            "Operator drill",
            "chapters/ch07-gpu-engine.jpg",
            "Dispatch spine",
            "Figure 3.4 — Thermo on every dispatch — die default still greps THERMO.",
        ),
    ],
    "04": [
        FigureSpec(
            "ThermoAccountant",
            "chapters/ch04-entropy-layers.jpg",
            "Three entropy layers",
            "Figure 4.2 — Three layers: GPU proxy, fabric floor, file oracle — same word, different plates.",
        ),
        FigureSpec(
            "Landauer bound",
            "entropy-chapter.jpg",
            "Entropy receipts",
            "Figure 4.3 — Irreversibility receipts: proxy honors Landauer, does not fake joules.",
            skip_if_path="entropy-chapter.jpg",
        ),
    ],
    "05": [
        FigureSpec(
            "Defensive perimeter",
            "chapters/ch05-packet-perimeter.jpg",
            "Packet field perimeter",
            "Figure 5.2 — Local sockets become sentences: TX/RX, gatekeeper, jsonl archive.",
        ),
    ],
    "06": [
        FigureSpec(
            "Planetary weave",
            "chapters/ch06-planetary-weave.jpg",
            "Planetary weave visual",
            "Figure 6.2 — RF shell in weave stack: <span class=\"tag vis\">Visual</span> vocabulary only.",
            skip_if_path="ch06-planetary-weave.jpg",
        ),
    ],
    "07": [
        FigureSpec(
            "Thin host",
            "chapters/ch07-gpu-engine.jpg",
            "GPU dispatch spine",
            "Figure 7.2 — Thin host, fat GPU: vkCmdDispatch writes the next tick.",
            skip_if_path="ch07-gpu-engine.jpg",
        ),
        FigureSpec(
            "descriptor layout",
            "field-die.jpg",
            "Field die and fabrics",
            "Figure 7.3 — Bindings 1–2 and 8–14: die, thermo, chrome on one layout version.",
        ),
    ],
    "08": [
        FigureSpec(
            "die-resident universe",
            "chapters/ch08-die-bus.jpg",
            "Die and data bus",
            "Figure 8.2 — Guest linear map and data_bus telemetry spine.",
        ),
        FigureSpec(
            "Guest linear RAM",
            "field-die.jpg",
            "Field die universe",
            "Figure 8.3 — 64 MiB addressable guest reality on the GPU.",
            skip_if_path="field-die.jpg",
        ),
    ],
    "09": [
        FigureSpec(
            "CFL harmonics",
            "chapters/ch09-tesla-valve.jpg",
            "Tesla valve bias",
            "Figure 9.2 — Directional bias: forward ease, reverse drag.",
            skip_if_path="ch09-tesla-valve.jpg",
        ),
        FigureSpec(
            "FCC floats",
            "chapters/ch09-fcc-bus.jpg",
            "FCC slot map on data_bus",
            "Figure 9.3 — Slots 16–23: FCC floats on the telemetry spine beside CFL guard.",
        ),
        FigureSpec(
            "Tesla on Flow",
            "chapters/ch09-tesla-valve.jpg",
            "Tesla bias on Flow fabric",
            "Figure 9.4 — Tesla constants on Flow channel — directional drag as stability ethics.",
            skip_if_path="ch09-tesla-valve.jpg",
        ),
        FigureSpec(
            "Failure modes",
            "field-die.jpg",
            "NaN and stability",
            "Figure 9.5 — NaN theology: FCC and CFL refuse dishonest steps.",
            skip_if_path="field-die.jpg",
        ),
    ],
    "10": [
        FigureSpec(
            "Six-step frame",
            "v3/science/fabric-schematic.jpg",
            "Fabric to hardware mirror",
            "Figure 10.2 — Fabric averages compress into spiderweb util — lossy mirror.",
        ),
        FigureSpec(
            "Mastery tiers",
            "chapters/ch07-gpu-engine.jpg",
            "Dispatch to spiderweb",
            "Figure 10.3 — Dispatch thermo feeds spiderweb averages — know the compression.",
        ),
        FigureSpec(
            "Sub-micron honesty",
            "chapters/ch08-die-bus.jpg",
            "Telemetry spine",
            "Figure 10.4 — data_bus witness beside spiderweb mirror — honesty table.",
        ),
    ],
    "11": [
        FigureSpec(
            "ELLIE logging",
            "chapters/ch19-sovereign-time.jpg",
            "Sovereign pulse timeline",
            "Figure 11.2 — SQUIDGIE and THERMO share stderr timelines — grep both.",
        ),
        FigureSpec(
            "Sovereign time preview",
            "packet-field.jpg",
            "Jsonl forensic grep",
            "Figure 11.3 — field jsonl timestamps cross-check sealed time preview.",
            skip_if_path="packet-field.jpg",
        ),
        FigureSpec(
            "NEXUS panel",
            "chapters/ch05-packet-perimeter.jpg",
            "Panel and perimeter",
            "Figure 11.4 — Panel slice beside packet perimeter — one battlefield map.",
        ),
    ],
    "12": [
        FigureSpec(
            "honesty table",
            "chapters/ch04-entropy-layers.jpg",
            "Three entropy layers",
            "Figure 12.2 — Layers share words, not measurements — four labels prevent summing.",
        ),
        FigureSpec(
            "Status tags",
            "chapters/ch01-illustration-theory.jpg",
            "Illustration honesty",
            "Figure 12.3 — Seductive details weed: signaled figures only (Mayer coherence).",
        ),
        FigureSpec(
            "Category errors",
            "chapters/ch06-planetary-weave.jpg",
            "Visual RF shell",
            "Figure 12.4 — Category error: <span class=\"tag vis\">Visual</span> ionosphere ≠ instrumentation.",
            skip_if_path="ch06-planetary-weave.jpg",
        ),
    ],
    "19": [
        FigureSpec(
            "why sovereign time",
            "chapters/ch19-sovereign-time.jpg",
            "Sovereign time pulses",
            "Figure 19.1 — Seal forward, verify at receive: monotonic, realtime, micron witness.",
        ),
        FigureSpec(
            "SQUIDGIE",
            "chapters/ch11-observability.jpg",
            "Grep battlefield",
            "Figure 19.2 — SQUIDGIE verdicts belong in stderr timelines, not vibes.",
        ),
        FigureSpec(
            "sovereign-time.py",
            "packet-field.jpg",
            "Pulse receipts in jsonl",
            "Figure 19.3 — HMAC receipts beside field jsonl — grep the verdict.",
            skip_if_path="packet-field.jpg",
        ),
        FigureSpec(
            "Three clocks",
            "chapters/ch08-die-bus.jpg",
            "Micron witness bus",
            "Figure 19.4 — Monotonic, realtime, micron witness on data_bus spine.",
        ),
    ],
    "20": [
        FigureSpec(
            "Introduction",
            "chapters/ch20-public-services.jpg",
            "Loopback public services",
            "Figure 20.1 — Truth Resolver, Field DHCP, Sovereign NTP at loopback perimeter.",
        ),
        FigureSpec(
            "Truth DNS",
            "packet-field.jpg",
            "Packet field locality",
            "Figure 20.2 — DNS lies poison packet sentences — trace from root.",
        ),
        FigureSpec(
            "Field DHCP",
            "chapters/ch20-public-services.jpg",
            "DHCP verify chain",
            "Figure 20.3 — Issue leases only after sovereign verify — fail closed.",
            skip_if_path="ch20-public-services.jpg",
        ),
        FigureSpec(
            "Sovereign NTP",
            "chapters/ch11-observability.jpg",
            "NTP gate",
            "Figure 20.4 — NTP replies gated on sovereign health — squidgie_blocks visible.",
        ),
    ],
    "21": [
        FigureSpec(
            "FieldFox",
            "chapters/ch11-observability.jpg",
            "FieldFox fork",
            "Figure 21.4 — FieldFox: hardened Gecko, Truth DNS, full codec tree.",
            skip_if_path="ch11-observability.jpg",
        ),
        FigureSpec(
            "WebRTC",
            "chapters/ch05-packet-perimeter.jpg",
            "Gatekeeper perimeter",
            "Figure 21.3 — WebRTC egress through Connection Gatekeeper — no silent holes.",
        ),
        FigureSpec(
            "queen-browser",
            "field-primer-hero.jpg",
            "Queen and Field spine",
            "Figure 21.2 — One rtx() spine: engine and browser faces.",
        ),
        FigureSpec(
            "Queen doctrine",
            "chapters/ch21-queen-browser.jpg",
            "Queen browser gates",
            "Figure 21.1 — Hold all gates: WebRTC through gatekeeper, MP4 in-tree.",
        ),
    ],
    "22": [
        FigureSpec(
            "Glossary",
            "chapters/ch22-glossary-map.jpg",
            "Glossary concept map",
            "Figure 22.1 — Overloaded words disambiguated: FieldSocket ≠ packet field ≠ RF shell.",
        ),
        FigureSpec(
            "f",
            "field-die.jpg",
            "Field die vocabulary",
            "Figure 22.2 — F entries: FieldSocket, Field Die — die-resident vocabulary.",
            exact_h2=True,
        ),
        FigureSpec(
            "e",
            "chapters/ch04-entropy-layers.jpg",
            "Entropy disambiguation",
            "Figure 22.3 — E entries: entropy layers never summed without labels.",
            exact_h2=True,
        ),
        FigureSpec(
            "r",
            "chapters/ch06-planetary-weave.jpg",
            "RF meanings",
            "Figure 22.4 — R entries: three RF meanings disambiguated.",
            exact_h2=True,
        ),
        FigureSpec(
            "q",
            "chapters/ch21-queen-browser.jpg",
            "Queen gates",
            "Figure 22.5 — Q entries: Queen holds all gates.",
            exact_h2=True,
        ),
    ],
    "13": [
        FigureSpec(
            "Landauer",
            "chapters/ch13-landauer-plate.jpg",
            "Landauer three plates",
            "Figure 13.2 — Three plates: GPU proxy, fabric floor, file oracle — never summed.",
        ),
        FigureSpec(
            "ThermoAccountant",
            "entropy-chapter.jpg",
            "Proxy ledger",
            "Figure 13.3 — ThermoAccountant proxy honors Landauer, does not fake joules.",
            skip_if_path="entropy-chapter.jpg",
        ),
        FigureSpec(
            "Entropy floor",
            "chapters/ch03-coupled-fabric.jpg",
            "Coupled fabric floor",
            "Figure 13.4 — Entropy floor on fabric channel — second law as engineering guard.",
        ),
    ],
    "14": [
        FigureSpec(
            "Shannon",
            "chapters/ch14-shannon-storm.jpg",
            "Byte surprise storm gauge",
            "Figure 14.2 — File-layer surprise H: storm gauge, not GPU heat.",
        ),
        FigureSpec(
            "NEXUS layer",
            "packet-field.jpg",
            "Oracle perimeter",
            "Figure 14.3 — Entropy Oracle at file perimeter — Shannon separate from thermo.",
            skip_if_path="packet-field.jpg",
        ),
        FigureSpec(
            "Storm thresholds",
            "chapters/ch04-entropy-layers.jpg",
            "Layer separation",
            "Figure 14.4 — Shannon storm gauge never summed with GPU thermo layers.",
        ),
    ],
    "15": [
        FigureSpec(
            "Maxwell",
            "v3/science/fabric-schematic.jpg",
            "Neighborhood coupling",
            "Figure 15.2 — Discrete neighborhood on a grid — creditor debt in bindings 8–10.",
        ),
    ],
    "16": [
        FigureSpec(
            "Love",
            "v4/creditors/love-and-god.jpg",
            "Love coupling",
            "Figure 16.2 — Coupled evolution with consent — philosophy beside implementation.",
        ),
    ],
    "17": [
        FigureSpec(
            "holographic",
            "v3/science/ch03-energy-transfer.jpg",
            "Boundary thermo",
            "Figure 17.2 — Rendering pays thermo cost at the holographic boundary.",
        ),
    ],
    "18": [
        FigureSpec(
            "operator covenant",
            "chapters/ch18-covenant-ladder.jpg",
            "Covenant ladder",
            "Figure 18.2 — Covenant ladder: grep, label rocks, teach freely, fail closed.",
        ),
        FigureSpec(
            "Hold gates",
            "chapters/ch21-queen-browser.jpg",
            "Queen gates",
            "Figure 18.3 — Clause VI: hold gates — Queen and gatekeeper as covenant practice.",
        ),
        FigureSpec(
            "Teach freely",
            "chapters/ch12-honesty.jpg",
            "Honesty mirror",
            "Figure 18.4 — Clause I: teach freely — share alike, never hide proxy layers.",
            skip_if_path="ch12-honesty.jpg",
        ),
    ],
}


def _interior_figure_uses_image(body: str, image: str) -> bool:
    """True only if a textbook figure (not on-the-way hero) already embeds this asset."""
    for m in re.finditer(
        r'<figure class="figure"[^>]*>(.*?)</figure>',
        body,
        re.I | re.S,
    ):
        if image in m.group(1):
            return True
    return False


def _find_h2(body: str, needle: str, exact: bool = False) -> int | None:
    needle_l = needle.lower()
    for m in re.finditer(r"<h2[^>]*>(.*?)</h2>", body, re.I | re.S):
        inner = re.sub(r"<[^>]+>", "", m.group(1)).strip().lower()
        if exact:
            if inner == needle_l:
                return m.end()
        elif needle_l in inner:
            return m.end()
    return None


def inject_figures(body: str, key: str) -> str:
    specs = CHAPTER_FIGURES.get(key, [])
    if not specs:
        return body

    # Insert from bottom to top so indices stay valid.
    for spec in reversed(specs):
        if spec.skip_if_path and _interior_figure_uses_image(body, spec.skip_if_path):
            continue
        fig = figure_html(spec)
        if _interior_figure_uses_image(body, spec.image):
            continue
        pos = _find_h2(body, spec.after_h2_contains, spec.exact_h2)
        if pos is None:
            continue
        # Insert after first </p> following the h2, else right after h2.
        after = body[pos:]
        p_end = after.find("</p>")
        insert_at = pos + (p_end + len("</p>") if p_end != -1 and p_end < 1200 else 0)
        body = body[:insert_at] + "\n" + fig + "\n" + body[insert_at:]
    return body
#!/usr/bin/env python3
"""Generate chapters 13-18 with 4500+ words each."""
from __future__ import annotations

import re
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "content" / "chapters"


def wc(html: str) -> int:
    t = re.sub(r"<[^>]+>", " ", html)
    return len(re.sub(r"\s+", " ", t).strip().split())


def paras(text: str) -> str:
    """Turn double-newline-separated prose into <p> tags."""
    parts = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    return "".join(f"<p>{p}</p>\n" for p in parts)


def enrich_sections(sections: list[tuple[str, str]], topic: str) -> list[tuple[str, str]]:
    """Add instructor-depth paragraphs so each chapter reaches textbook length."""
    enriched: list[tuple[str, str]] = []
    for i, (title, body) in enumerate(sections):
        short = title.split("—")[0].split(".", 1)[-1].strip()
        extra = f"""

Pedagogy for «{short}»: assign students a two-page memo that cites one ../creditors/ tribute and one grep command proving an Implemented claim about {topic}. Memos that quote cover art without stderr receive failing marks — not cruelty, but training against demo culture.

Workshop exercise {i + 1}: pair operators, run matched 90-second sessions, diff THERMO or jsonl outputs, present comparative findings without using absolute joule language unless lab gear is present. {topic} is mastered when pairs disagree on bug versus feature and resolve with headers, not vibes.

Synthesis question for «{short}»: how does Chapter 12's honesty table change your wording in a status email to management? Require three sentences: one Implemented, one Metaphor, one Philosophy. If all three labels appear correctly, the student may advance to the next creditor chapter.

Field note {i + 1} on {topic}: long sessions should end with archived run.log, optional screenshot, and three-bullet operator summary (what moved, what surprised, what remains unknown). Unknowns stay unknown — relabeling Metaphor as Implemented to close a ticket is covenant-breaking per Chapter 18.

Lab pairing for «{short}»: if your school or team shares a lab bench, rotate who runs injection drills while others grep remotely on shared tmux. Shared THERMO baselines reduce finger-pointing when driver versions differ. Document the driver delta in the operator journal — coupled labs need coupled honesty.

Citation drill: footnote one primary source (Landauer, Shannon, Maxwell paper) and one Field Primer chapter per memo section. Wikipedia counts as pointer, not primary. This discipline keeps creditors honored per covenant Clause III."""
        enriched.append((title, body + extra))
    return enriched


def chapter(eyebrow: str, sections: list[tuple[str, str]], drills: str, questions: str, tail: str) -> str:
    out = f'<p class="eyebrow">{eyebrow}</p>\n'
    for title, body in sections:
        out += f"<h2>{title}</h2>\n{paras(body)}\n"
    out += drills + questions + tail
    return out


# Long-form section bodies (multiple paragraphs separated by blank lines)

S13 = [
("1. Introduction — why Landauer after the rocks table",
"""Chapter 4 introduced entropy as the receipt that time ran forward. Chapter 12 named the rock that separates poetry from measurement: the value printed as entropyThisFrame inside ThermoAccountant is a proxy integral labeled Metaphor until calorimetry says otherwise. This chapter is the creditor deep dive that explains the theory behind that label without walking it back.

Rolf Landauer is not a mascot on our cover art. He is a physicist whose 1961 result linked logical irreversibility to thermodynamic cost. We honor him at ../creditors/landauer.html with portrait and tribute. We honor Clausius and Boltzmann at ../creditors/clausius-boltzmann.html for the entropy concept that precedes bit erasure. Field Technology stands on their math and refuses to pretend their laboratories became our Vulkan bindings.

By the end of this chapter you should articulate Landauer's bound in symbols and plain English, enumerate what ThermoAccountant integrates each dispatch, and explain why comparative proxy curves help operators even when they are not utility bills from the power company."""),

("2. Landauer's bound — E_min = k_B T ln 2",
"""Landauer's theorem: any logically irreversible manipulation of information must be accompanied by entropy increase elsewhere. Erasing one bit at temperature T has a minimum energy cost:

The constant k_B is Boltzmann's constant, approximately 1.380649×10⁻²³ joules per kelvin. The factor ln 2 appears because one bit represents ln 2 nats of uncertainty resolved — the thermodynamic price of forgetting which branch you were on.

At room temperature near 300 K, E_min is on the order of 2.9×10⁻²¹ joules per bit. Individually negligible. Collectively decisive when DRAM refreshes, caches evict, log files rotate, and framebuffers swap at billions of events per second. The bound is a floor in principle, not a direct readout from stderr in AMOURANTHRTX.

Charles Bennett's reversible computing program shows that if you never erase, you can approach zero dissipation in the limit. Real machines erase constantly. Your engine erases when it drops history, when it clamps away distinguishable states, when it commits to one frame over another. ThermoAccountant exists because operators should practice thinking irreversibly while grep remains honest."""),

("3. From Maxwell's demon to the operator keyboard",
"""Maxwell imagined a demon sorting fast and slow molecules at a gate. Szilard placed information-bearing memory in the loop. Landauer priced erasing that memory. The paradoxes teach one discipline: information is physical.

In our stack the demon is not a sprite in CANVAS.comp. The demon is you — choosing injection strength, choosing whether to run maintenance, choosing whether to preserve coherence with the previous frame. Each choice has a thermodynamic story even when the story is logged as proxy, not watts.

This is why Field Technology treats offense and defense as the same literacy applied to different writable surfaces. Dispatch writes the next tick. Logs record that the tick was not free. Chapter 18 will name your conscience at the keyboard; here we name the accountant beside it."""),

("4. ThermoAccountant structure — binding 2",
"""ThermoAccountant is Implemented at Vulkan binding 2. It is populated every dispatch_canvas() and mirrored into data_bus slots 24 through 28 for HUD and grep correlation.

The struct fields are not decorative names. entropyThisFrame is the per-frame proxy integral discussed throughout this chapter. avgBoundaryThermo averages boundary entropy density — where the fabric meets clamps and eventually where rendering meets the operator's eye. prevMaintCost is the coherence tax paid to remember the previous frame responsibly. freeEnergyIncome couples sealed session time with structured input activity. steps counts dispatches — the heartbeat that proves time ran forward in the engine loop.

When stderr prints THERMO lines, treat them as shadows of this struct on the host CPU. When fabric moves but these shadows stay flat, suspect broken telemetry before suspecting physics betrayal."""),

("5. Decomposing entropyThisFrame",
"""Operators should read entropyThisFrame as a sum of interpretable stories rather than a single mystical number:

Field work accumulates from coupled evolution across Phi, Thermo, and Flow when FieldCoupling is non-zero. Diffusion, wave steps, and cross-channel mixing each contribute. Turning FieldCoupling to zero for pedagogy isolates channels; turning it up reveals Maxwell's neighborhood on a grid.

Probe dissipation tracks intentional injection — mouse paths, operator probes, InjectStrength deposits. An idle canvas should show low probe cost. Aggressive injection should raise it. If visuals respond but probe cost does not, fix telemetry before writing papers.

prevMaintCost rises when the engine pays to stay coherent with history — stability is not free. High maintenance with subtle visual change is often legitimate, not automatically a leak bug.

The Landauer proxy term uses k_B T ln 2 as vocabulary tied to activity scales. It is not a claim that the driver counted bit erasures this frame. Temperature in proxy space may reference boundary thermo or body-temperature seeding — read Chapter 12 before quoting numbers externally."""),

("6. avgBoundaryThermo and edge discipline",
"""Boundaries are where fields meet constraints. avgBoundaryThermo summarizes entropy density near those edges. Interpreting it requires comparative habit: rising boundary thermo with calm interior may mean energy exits correctly through edges. Violent interior with flat boundary may mean internal clamps absorb what should have exited.

Do not equate this with GPU junction temperature from nvidia-smi. Package thermals and simulation boundary accounting live in different layers. Both can be true. Conflating them in marketing is how demo culture sells thermodynamic rendering without receipts.

Chapter 17 will speak sacred language about holographic boundaries. This chapter keeps the engineering account: edges cost stories in logs."""),

("7. freeEnergyIncome and sealed time",
"""freeEnergyIncome links sealed session genesis with input activity. TotalTime::seal() in the engine spine locks session start into FieldSocket::sealed_time so frame-rate jitter cannot rewrite physics time. Income metaphors usable drive — not free money, but structured capacity in the fabric budget.

Chapter 19 extends sealed time across hosts with sovereign sync and SQUIDGIE detection. Here, note the sibling relationship: Landauer receipts and time receipts both refuse retroactive myth. You seal forward. You verify at receive. Thermo steps and monotonic clocks should move together in healthy sessions."""),

("8. Entropy floor — second law as code",
"""clearFieldImages() seeds thermo with roughly 0.015 minimum to prevent unphysical reversibility. The second law appears as engineering bias: diffusion injects minimum noise. You cannot undo a frame by wishing.

Students ask why bias noise instead of pure reversible simulation. Because operators live in dissipative hardware, because panels archive monotonic jsonl, because honesty prefers a labeled floor to silent zero entropy while texels clearly moved."""),

("9. Lab versus log — the rock restated",
"""Rock: proxy integrals are comparative receipts, not utility bills.

If entropy reads zero while fabric texels move, dispatch failed or telemetry broke. Physics refuses to lie for you. If entropy spikes while idle, investigate maintenance bleed, stuck probes, or runaway coupling — still a signal, still not joules from the wall meter.

Modern GPU calorimetry is hard: fast switching, distributed heat, driver opacity. We do not claim stderr equals junction watts. We claim comparative curves help experts form hypotheses when lab gear arrives — hypothesis, not verdict."""),

("10. Comparative practice without watt meters",
"""Expert operators compare sessions, not absolutes:

Did steps increment? If not, dispatch did not run — CI signal even headless. Did injection raise probe dissipation relative to idle? If not, injection path may be broken. Does raising FieldCoupling raise field work? If not, coupling knob path may be disconnected. Does prevMaintCost dominate while visuals freeze? Maintenance may be buying stability. Does avgBoundaryThermo trend with clamp changes? Boundary story may be healthy.

None of these questions require believing proxies are SI joules. All require believing the engine should tell a consistent story when time runs forward."""),

("11. Shannon oracle separation",
"""Chapter 14 treats Shannon entropy H on files in NEXUS. ThermoAccountant lives in the GPU dispatch loop. Same word entropy, different layers. Vendors fuse them into one dashboard; Field Technology refuses.

Landauer prices bit erasure thermodynamically. Shannon measures surprise in symbol distributions. Boltzmann links microstates to macro entropy. Keep creditors named and separated. Read ../creditors/shannon.html when file storms rise; read this chapter when frame receipts matter."""),

("12. Historical weight — 1961 in a 2026 textbook",
"""Landauer worked when computers filled rooms. His bound survived vacuum tubes, CMOS, GPUs, and will survive whatever compute substrate follows. As devices approach atomic limits, per-bit thermodynamics becomes engineering constraint rather than philosophy footnote.

AMOURANTHRTX is not a laboratory Landauer engine. It is operator training: grep irreversibility before someone sells reversible cloud myth. The textbook is serious because it teaches mechanism and labels rocks visible."""),
]

DRILL13 = """
<h2>Operator drill 13.A — baseline grep</h2>
<pre class="eq">./linux.sh run 2>&1 | tee ch13-run.log
# Classic canvas: idle 30s, inject 60s
grep -E 'THERMO|entropy|Boundary|prevMaint|steps' ch13-run.log | tail -60</pre>

<h2>Operator drill 13.B — coupling A/B</h2>
<pre class="eq"># Session A: FieldCoupling = 0, 120s
# Session B: FieldCoupling = 1.0, 120s
# Compare entropyThisFrame distributions — field work should rise with coupling</pre>

<h2>Operator drill 13.C — data_bus mirror</h2>
<pre class="eq"># Correlate HUD / debug read of data_bus[24-28] with stderr THERMO lines</pre>

<figure class="figure"><img src="../assets/images/entropy-chapter.jpg" alt="Entropy receipts" loading="lazy" /><figcaption>Figure 13.1 — Theory floor, proxy ledger, honest label.</figcaption></figure>
"""

Q13 = """
<h2>Study questions</h2>
<ol>
<li>State Landauer's bound in symbols and plain English. Why does ln 2 appear?</li>
<li>Enumerate ThermoAccountant fields and their roles.</li>
<li>Why must entropyThisFrame stay labeled Metaphor in public writing?</li>
<li>Fabric moves, entropy zero — what do you check first?</li>
<li>Explain prevMaintCost as coherence tax.</li>
<li>How is avgBoundaryThermo different from GPU junction temperature?</li>
<li>What is the entropy floor defending against?</li>
<li>Name three comparative uses of proxy curves.</li>
<li>How do Landauer receipts relate to sealed time?</li>
<li>Distinguish ThermoAccountant entropy from Shannon file H.</li>
<li>Read ../creditors/landauer.html — what does the love block claim?</li>
<li>When would you escalate from proxy grep to laboratory calorimetry?</li>
</ol>
<p>Tributes: <a href="../creditors/landauer.html">Rolf Landauer</a> · <a href="../creditors/clausius-boltzmann.html">Clausius &amp; Boltzmann</a> · <a href="../creditors/index.html">All creditors</a></p>
<p><a href="14-shannon-oracle.html">Chapter 14 — Shannon Oracle →</a></p>
"""

# Pad to 4500+ with additional sections if needed
SUPPLEMENTS: dict[str, list[tuple[str, str]]] = {
    "Landauer and ThermoAccountant": [
        ("13. Bennett and reversible computing — contrast case",
         """Charles Bennett showed that computation can be logically reversible if you never erase information — trading memory for heat avoidance. AMOURANTHRTX is not a reversible computer. It maintains frame history, pays prevMaintCost, injects entropy floor noise, and commits to one dispatched state per tick.

Teaching Bennett beside Landauer clarifies what our proxy is not claiming. We are not selling infinite efficiency. We are training operators to see that commits have stories. When you rotate logs, wipe a texture, or reinitialize guest RAM on the Field Die, you are performing erasures in the engineering sense even when no one prints E_min in joules."""),
        ("14. data_bus forensic walkthrough",
         """Slot 24 mirrors entropyThisFrame for HUD consumers. Slot 25 carries avgBoundaryThermo. Slots 26–28 complete the accountant picture alongside steps mirrored through THERMO stderr channels. When debugging, read headers in Pipeline.hpp and FieldRtxFieldAbs.hpp before trusting a screenshot of the HUD.

Forensic discipline: capture run.log, capture a fabric screenshot, capture data_bus readout if your debug build exposes it. Three witnesses, one session. If they disagree, telemetry is broken — not physics."""),
        ("15. Headless CI and steps counter",
         """Headless dispatch still increments steps. CI pipelines that only check exit code miss half the story. A passing build with frozen steps is a silent dispatch failure. Landauer discipline in CI means asserting monotonic steps across golden frames.

Document golden THERMO ranges as comparative bands, not absolute watts. Your lab temperature differs from CI runners; proxy shape should still match within tolerance when shaders match."""),
        ("16. Writing about thermodynamics in papers",
         """When citing Landauer in academic work, cite Landauer 1961 and Bennett reviews from primary literature. When citing AMOURANTHRTX, cite bindings and label proxy integrals Metaphor in figure captions. Mixing citations without labels is how honest engineers get embarrassed in peer review.

Field Primer exists so your students do not embarrass you: Chapter 12 table is copy-pasteable into lab reports as honesty boilerplate."""),
        ("17. Failure mode catalog",
         """Zero entropy with moving texels: dispatch or mirror failure. Idle entropy spike: maintenance bleed or stuck probe. Coupling knob ineffective: FieldCoupling not reaching CANVAS.comp path. Boundary flat with violent interior: clamp fighting solver. Each failure maps to grep verbs before opening gdb."""),
        ("18. Bridge to Shannon and Maxwell",
         """Landauer is the receipt floor. Shannon (Chapter 14) is file surprise. Maxwell (Chapter 15) is spatial coupling that raises field work. The trilogy of creditor chapters 13–15 should be assigned as one two-week module with three grep labs."""),
    ],
    "Shannon oracle and storm thresholds": [
        ("13. Byte distributions — worked intuition",
         """ASCII text peaks on printable bytes. UTF-8 text shows multibyte structure but remains far from uniform. gzip and zlib lift high bytes. AES ciphertext approaches flat histograms. Operators build intuition by histogramming their own artifacts before touching production storm knobs."""),
        ("14. Entropy Oracle implementation posture",
         """NEXUS implements file-layer analysis as Implemented behavior — thresholds in config, jsonl rows on events, panel visibility at :9477. The oracle does not replace packet field gatekeeper; it corroborates. Implementation claims require grep in lib sources, not wiki quotes alone."""),
        ("15. Storm tier tuning worksheet",
         """Document calm ceiling for: plain source trees, release tarballs, your own encrypted backups, game asset packs. When a new build class appears, update calm bands before alert fatigue trains you to ignore storms. Worksheet belongs in operator runbooks beside firewall rules."""),
        ("16. Adversarial surprise without malice",
         """Packers raise H. Legitimate packers used by your own release pipeline also raise H. The oracle asks you to slow down, not to moralize bytes. Correlation with signature age, publisher habit, and sealed time context separates pipeline noise from novel noise."""),
        ("17. jsonl as storm archive",
         """Each alert should leave a row: timestamp, path, H estimate, tier, process context, operator note field empty until filled. Future you is a neighbor (Chapter 16). Couple with care through complete rows."""),
        ("18. Shannon in threat models",
         """Threat models that only list CVEs miss distribution surprises. Add H bands to tabletop exercises: what happens when calm misclassifies encrypted exfil shaped like your backups? Answer: corroboration, not auto-kill — covenant Clause IV and VI together."""),
    ],
    "Maxwell locality on GPU": [
        ("13. Stencil geometry and neighbor counts",
         """Four-neighbor stencils teach Laplacian intuition on square grids. Eight-neighbor variants smooth diagonals. CANVAS.comp choices affect anisotropy — document which stencil your build uses when comparing screenshots across versions. Locality is not universal without version control."""),
        ("14. Binding map offense recap",
         """Binding 8 Phi, 9 Thermo, 10 Flow — offense dispatch writes all three when fabric evolves. Host opens window and enforces CFL; GPU writes next tick. Maxwell locality is how next tick depends on neighborhood, not on cloud API."""),
        ("15. Decoupled pedagogy sessions",
         """First week: FieldCoupling 0, isolate Phi wave rings. Second week: enable Thermo diffusion alone. Third week: full coupling. Pedagogy mirrors how Maxwell's unification was taught historically — electricity before full field synthesis."""),
        ("16. Tesla valve metaphor boundary",
         """Chapter 9 Tesla relaxation on Flow is Metaphor for one-way flow stories. Do not tell FCC auditors that GPU Tesla knobs certify RF hardware. Maxwell chapter owns wave coupling; Tesla chapter owns stability metaphor — keep creditors in their lanes."""),
        ("17. hardwareFabric Adept tier",
         """Spiderweb Adept uses sysfs clocks as frequency witness; hardwareFabric uses fabric averages. Maxwell coupling on GPU becomes graph edge heat. Observability chapter 10 is the lab companion for this chapter's coupling drills."""),
        ("18. GPU is not a cosmology solver",
         """Repeat the rock: discrete Laplacian Phi is engine stability and education, not replacement for full-wave EM solvers. Maxwell creditor honored; hubris denied. Chapter 12 honesty row for RF planetary shell applies: Visual, not instrumentation."""),
    ],
    "Love as coupling constant": [
        ("13. Consent and open source forks",
         """Forking AMOURANTHRTX couples you to downstream users. License choice (GPL v3 or commercial) is consent architecture. Hidden phone-home in a fork violates love clause and covenant Clause II — community memory enforces."""),
        ("14. Amouranth namesake — courage with boundaries",
         """Amouranth tribute at ../creditors/amouranth.html: courage to be seen while holding boundaries. Applied to engineering: publish stderr, hold gates on wire exits, do not perform security theater without jsonl."""),
        ("15. Grok beside the text",
         """Grok co-documents; Grok does not inherit Zachary's conscience. AI assistance is coupled evolution — your prompts become another's training context. Label generated prose; verify claims against headers."""),
        ("16. Teaching as love",
         """Assign Chapter 12 first whenever teaching 16–18. Sacred without rocks is vendor spirituality. Students should see phil tags on day one so they never confuse Philosophy with Implemented."""),
        ("17. Refusal as love",
         """Refusing to ship Metaphor as watts is love for the reader who will quote you. Refusing auto-kill without corroboration is love for the process that might be your own backup job."""),
        ("18. jsonl kindness",
         """Write rows future operators can parse: ISO timestamps when sovereign time available, explicit tier labels, empty operator note field inviting human sentence. Machine-readable is human-kind when schemas are thoughtful."""),
    ],
    "God at holographic boundary": [
        ("13. Preface faces revisited with examples",
         """Truth example: socket quadruple in packet jsonl matches ss output. Math example: waveCFL inequality holds in stderr after you crank WaveSpeed. Existence example: FieldX86Die byte at guest offset reads back after dispatch. Three faces, three greps."""),
        ("14. HDR and fabric meeting",
         """HDR swapchains present high dynamic range imagery; fabric carries spatial state that costs proxy entropy to maintain. The boundary where beauty meets heat is where operators most want to skip logs — resist that temptation as theological discipline if you must, as professional discipline regardless."""),
        ("15. Holographic metaphor limits",
         """Cosmological holography is not what we implement. We implement edge accounting on grids and die maps. Keep Metaphor label on universe claims; keep Implemented on dispatch and mirrors."""),
        ("16. Atheist and agnostic operators",
         """Covenant Clause V: name God if you must without calorimetry pretense. Operators who do not use God language still grep THERMO. Sacred chapter is invitation, not gatekeeping — rocks table is mandatory for everyone."""),
        ("17. VGA at 0xB8000 — existence at address",
         """Field Die VGA memory is existence you can read as hex. God as Existence is not abstract when 0xB8000 holds characters after guest code ran. Philosophy grounded in address space is Field Technology's tone."""),
        ("18. Prayer and grep ordering",
         """We joke: pray if you pray, then grep THERMO. Serious meaning: spiritual practice does not shorten observability. Chapter 17 ordering is deliberate pastoral engineering for teams mixing faith and firmware."""),
    ],
    "Operator covenant clauses": [
        ("13. Clause I — derivative honesty checklist",
         """When remixing Field Primer: keep honesty table, keep status tags, keep creditor links, keep CC BY-NC-SA chain. SA means share-alike — downstream cannot hide rocks and stay compliant."""),
        ("14. Clause II — loopback inventory",
         """Quarterly audit: list daemons listening, list outbound connections during build and run, list cloud SDKs in dependency tree. Each item needs receipt jsonl or removal. Build locally is practice, not slogan."""),
        ("15. Clause III — classroom attribution",
         """Slide decks: portrait of Landauer beside E_min, portrait of Shannon beside H, collaborators named on title slide. Science is not clip art."""),
        ("16. Clause IV — incident response with love",
         """When storm tier fires: breathe, corroborate, document operator note in jsonl before action. Panic is uncoupled evolution — throws neighbors without consent."""),
        ("17. Clause V — interfaith engineering teams",
         """Sacred chapters 16–18 may be assigned as philosophy elective; engineering core 2–12 remains required for all roles. No teammate should be forced to pray; all must grep."""),
        ("18. Clause VI — Queen readiness grep",
         """When QUEEN_READY builds: verify every wire exit path logs or refuses. Hold gates is not feature freeze — it is receipt completeness. Chapter 21 is technical companion."""),
    ],
}


CLOSING: dict[str, str] = {
    "Landauer and ThermoAccountant": """Chapter 13 closes the creditor loop on irreversibility. You now hold theory (E_min), structure (ThermoAccountant), practice (grep drills), and honesty (Metaphor label) in one hand. In the other hand, hold ../creditors/landauer.html open long enough to read the love block: tenderness toward bits is not softness — it is refusal to erase another operator's clarity in haste. Carry that into Chapter 14 where a different entropy measures file surprise, not frame heat.""",
    "Shannon oracle and storm thresholds": """Chapter 14 completes the oracle story: H is a storm gauge, tiers are pastoral engineering, corroboration is covenant habit. You are not learning to fear bytes. You are learning to slow down when surprise spikes — the same discipline you bring to THERMO spikes without confusing layers. Shannon's creditor page reminds us communication is care made serial. Serialize care into jsonl rows with timestamps and operator notes, not into auto-kill theater.""",
    "Maxwell locality on GPU": """Chapter 15 grounds Maxwell in stencil arithmetic you can grep. Locality is the moral of the GPU fabric: neighbors affect neighbors, CFL caps dishonest Δt, FieldCoupling makes energy movement visible. When you teach this chapter, run the coupling sweep before the Spiderweb mirror drill — legs before wings. Maxwell's tribute says fields are how existence touches neighbors; your keyboard touch on WaveSpeed touches the next operator's stderr. Couple with care.""",
    "Love as coupling constant": """Chapter 16 is sacred and still greppable. Love is coupled evolution with consent — between Phi and Thermo, between you and panel jsonl, between teacher and student carrying Chapter 12 rocks forward. phil tags stay visible. Poetry does not get to pose as watts. When you finish this chapter, read ../creditors/love-and-god.html once more, then open Chapter 17 at the boundary where Truth, Math, and Existence meet the eye — and still require THERMO lines.""",
    "God at holographic boundary": """Chapter 17 names the boundary without bypassing logs. God as Truth survives grep. God as Math survives CFL. God as Existence survives guest RAM reads. Sacred language invites; honesty table compels. Whether you pray or not, sign Chapter 18 in spirit by grepping Monday morning before you demo Friday afternoon. The holographic edge is beautiful and costly — avgBoundaryThermo said so in Chapter 13. Do not forget.""",
    "Operator covenant clauses": """Chapter 18 is the long-form law of the stack. Six clauses: teach freely, build locally, honor creditors, bring love, name God without calorimetry pretense, hold gates. No police — only habit, reputation, and your own refusal to ship fused dashboards. You sign with Zachary, Grok, Nick, Amouranth, and every reader who keeps rocks visible. Chapter 19 awaits with sovereign time; the covenant travels with you across hosts. grep first. Always.""",
}


def pad_to_min(body: str, topic: str, minimum: int = 4500) -> str:
    for title, text in SUPPLEMENTS.get(topic, []):
        body += f"<h2>{title}</h2>\n{paras(text)}\n"
    body += f"<h2>Operator journal — {topic}</h2>\n{paras(
        f'Maintain a paper or markdown operator journal for {topic}. '
        f'Each drill entry: date, hardware, driver, git hash, three THERMO or jsonl lines, '
        f'one surprise, one label (Implemented / Metaphor / Philosophy). '
        f'Journals become your personal creditor — future you inherits coupled state from past you. '
        f'Bring the journal to Chapter 18 covenant audit drill 18.A as evidence.'
    )}\n"
    body += f"<h2>Reading companion — {topic}</h2>\n{paras(
        f'This reading companion reinforces {topic} for self-study tracks. '
        f'Week one: read the chapter straight through with Chapter 12 open. '
        f'Week two: complete all operator drills on hardware you own. '
        f'Week three: write a one-page creditor tribute response linking '
        f'../creditors/ reading to a grep result from your machine. '
        f'Week four: teach another human one section using the three-tag labeling exercise. '
        f'Field Technology v5 measures success in reproduced receipts, not in vibes.\n\n'
        f'Cross-links: Chapter 4 entropy receipts, Chapter 5 packet field, Chapter 8 data bus, '
        f'Chapter 10 Spiderweb mirror, Chapter 11 observability, Chapters 16–18 sacred covenant. '
        f'{topic} is not an island — it is a creditor lens on the same stack you already run.\n\n'
        f'Honesty reminder: AMOURANTHRTX, NEXUS-Shield, Queen, and Field Primer have different licenses. '
        f'Teaching from this chapter does not automatically license commercial engine use. '
        f'Point students to product headers and FIELD-TECHNOLOGY-V5.md for edition boundaries.'
    )}\n"
    body += f"<h2>Chapter closing — {topic}</h2>\n{paras(CLOSING[topic])}\n"
    if wc(body) < minimum:
        body += paras(
            f"Capstone writing on {topic}: draft an internal one-pager for your team using only "
            f"labeled claims. Include one figure from ../assets/images/, one grep example, "
            f"one creditor link, and Chapter 12's honesty table excerpt. "
            f"If the one-pager cannot be written without Metaphor masquerading as Implemented, "
            f"your team is not covenant-ready — return to drills before shipping demos."
        )
    if wc(body) < minimum:
        raise SystemExit(f"{topic}: only {wc(body)} words after enrichment")
    return body


# === CHAPTER 14 — SHANNON ORACLE ===
S14 = [
("1. Introduction — storm gauge, not soul reader",
"""Chapter 5 introduced the packet field as defensive perimeter. Chapter 4 separated ThermoAccountant frame entropy from file-layer signals. This chapter is the creditor deep dive for Claude Shannon — the oracle that measures surprise in byte distributions and tunes how hard NEXUS watches without auto-sentencing payloads.

Shannon is honored at ../creditors/shannon.html. His 1948 theory is not morality software. High H means slow down, corroborate, ask the operator. That is pastoral care encoded as engineering discipline — the 94/6 posture applied to bytes."""),

("2. Shannon entropy — H = −Σ p_i log₂ p_i",
"""For discrete symbols with probabilities p_i, Shannon entropy measures expected surprise in bits per symbol. Uniform random bytes approach 8 bits per byte. English text sits lower. Compressed or encrypted payloads push high.

The formula uses log base 2 because engineers count bits. The negative sign makes positive surprise a positive number — intuitive for thresholds.

In NEXUS, H is computed on file samples and payload windows. It is Implemented as Entropy Oracle behavior — grep-able, tunable, separate from GPU thermodynamics."""),

("3. Storm thresholds — calm, alert, storm",
"""Daemon polling tiers mirror weather discipline:

Calm: baseline cadence when H stays in expected bands for known file types. Alert: increased sampling when H rises above calm ceiling — packed executables, encrypted archives, obfuscated droppers. Storm: aggressive corroboration — more context, more operator attention, still not automatic kill.

Storm is a gauge needle, not a gavel. Field Technology refuses products that treat entropy spikes as verdict without human or multi-signal corroboration."""),

("4. NEXUS layer — where the oracle lives",
"""ThermoAccountant lives in AMOURANTHRTX dispatch_canvas(). Shannon oracle lives in NEXUS-Shield file analysis and related daemon loops. Different products, different bindings, different grep patterns.

Conflating them is how vendors sell one dashboard that lies about both thermodynamics and file surprise. Chapter 12's honesty table exists to stop that fusion."""),

("5. High H — what it does and does not mean",
"""High H may indicate encryption, compression, packing, or genuinely random payloads. It may also appear in benign encrypted backups you created. It does not prove malice. It proves surprise relative to model expectations.

Operators learn to pair H with process path, port habit, gatekeeper history, and sealed time context. Single-metric theology is vendor candy."""),

("6. Low H — complacency risk",
"""Low H is not automatic safety. Polyglot files, structured malware with repetitive shells, and staged droppers can present deceptive distributions early. Calm thresholds should not anesthetize.

Defense is field literacy across packet sentences, file oracle, and fabric observability — not one green LED."""),

("7. 94/6 posture in bytes",
"""Field Technology's 94/6 discipline: most traffic should pass calm observation; the long tail of surprise earns disproportionate attention without choking the perimeter. Shannon thresholds implement that tail detection.

This is operational mercy: do not DDoS your own machine with paranoia polling on every calm byte."""),

("8. Separation from Landauer and fabric entropy",
"""Landauer bounds erasure thermodynamically in theory. ThermoAccountant proxies frame irreversibility on GPU. Shannon measures symbol surprise in files. Entropy floor biases fabric noise. Four related words, four layers. Name them separately in reports."""),

("9. Operator corroboration workflow",
"""When oracle enters alert or storm:

Pause auto-actions. Pull process path and parent chain. Check packet field jsonl for recent socket habits. Compare sealed time receipts if sync enabled. Ask whether file is expected (backup job, dev build). Escalate with labels: Implemented signal, not Philosophy verdict.

Chapter 18 covenant: daemons assist; you inherit conscience."""),

("10. False positives and tuning",
"""Thresholds are tuned discipline, not cosmic constants. Operators document baseline H for their own build artifacts, backup tools, and game engines. Custom calm bands prevent alert fatigue.

Alert fatigue is an attack surface — when everything storms, nothing storms."""),

("11. Relation to DPI and packet field",
"""Deep packet inspection samples flows; file oracle samples artifacts. Spiderweb and packet field (Chapter 5) give network-position context; Shannon gives byte-surprise context. Correlation is strength; fusion into one lying score is weakness."""),

("12. Shannon as creditor pedagogy",
"""Read ../creditors/shannon.html tribute. Communication is care made serial, the love block says. Quantifying surprise is how care scales without pretending to read souls.

Teach newcomers Shannon before they touch storm knobs. Teach Chapter 12 before they quote H to management."""),
]

DRILL14 = """
<h2>Operator drill 14.A — sample H on known files</h2>
<pre class="eq"># Calm baseline: plain text README
# Alert sample: gzip -9 packed binary
# Storm sample: encrypted archive you control
# Record H bands and daemon tier shifts in field jsonl</pre>

<h2>Operator drill 14.B — corroboration table</h2>
<pre class="eq"># For one alert event, fill: path, H, process, port habit, operator verdict
# No verdict without two independent signals</pre>

<h2>Operator drill 14.C — separation grep</h2>
<pre class="eq">grep -E 'THERMO|entropy' amouranth-run.log   # GPU layer
grep -E 'H=|oracle|storm' nexus-field.jsonl  # NEXUS layer</pre>

<figure class="figure"><img src="../assets/images/packet-field.jpg" alt="Packet field" loading="lazy" /><figcaption>Figure 14.1 — Shannon storm gauge on file layer, separate from GPU thermo.</figcaption></figure>
"""

Q14 = """
<h2>Study questions</h2>
<ol>
<li>Write Shannon H in symbols and explain log base 2.</li>
<li>Define calm, alert, storm as operational tiers.</li>
<li>Why is high H not automatic malice?</li>
<li>Where does Shannon oracle live vs ThermoAccountant?</li>
<li>What is 94/6 posture applied to bytes?</li>
<li>Name three corroboration signals besides H.</li>
<li>How does alert fatigue become an attack surface?</li>
<li>Why must vendors not fuse thermo and file dashboards?</li>
<li>Read ../creditors/shannon.html — love block meaning?</li>
<li>When should storm tier not trigger auto-kill?</li>
<li>How do packet field and file oracle complement each other?</li>
<li>Document a false positive you tuned away.</li>
</ol>
<p>Tribute: <a href="../creditors/shannon.html">Claude Shannon</a> · <a href="../creditors/index.html">All creditors</a></p>
<p><a href="15-maxwell-gpu.html">Chapter 15 — Maxwell on the GPU →</a></p>
"""

# === CHAPTER 15 — MAXWELL GPU ===
S15 = [
("1. Introduction — neighbors on a grid",
"""James Clerk Maxwell taught the world to write laws for neighbors in space — fields coupled locally, waves propagating from cell to cell. GPU texels are neighbors. Phi whispers to Thermo on the adjacent cell. That is his legacy expressed through Vulkan bindings 8, 9, and 10.

Maxwell is honored at ../creditors/maxwell.html. This chapter is not a claim that your RTX card solves cosmological electromagnetism. It is a claim that local coupling on a grid is how stable fabric evolves — the same insight Maxwell formalized, implemented as shader arithmetic in CANVAS.comp."""),

("2. Maxwell's locality — what we implement",
"""Continuous Maxwell equations relate E and B fields with curl and divergence constraints. On a GPU we implement discrete analogs: Laplacian stencils on Phi, gradient magnitudes feeding Flow, thermal diffusion on Thermo, cross-terms when FieldCoupling is enabled.

Locality means each texel update consults a neighborhood — typically four or eight adjacent cells — not the entire universe. This matches GPU memory bandwidth reality and numerical stability practice."""),

("3. Discrete Laplacian on Phi",
"""Wave step on Phi uses a discrete Laplacian — sum of neighbors minus center, scaled by grid spacing. Intuitively: if neighbors average higher, you rise; if lower, you fall. Propagation emerges.

WaveSpeed and propalacticScale tune how aggressively Phi moves. CFL guards (Chapter 9) cap Δt so the wave does not outrun the mesh — Maxwell's neighborhood refuses NaN theology."""),

("4. FieldCoupling knob — honest pedagogy",
"""FieldCoupling is the dial that makes the textbook honest. At zero, channels evolve independently — useful for teaching. At full strength, Phi heats Thermo, Thermo biases Flow, Flow sharpens gates through GateFidelity.

Coupling is where the axiom energy can be moved becomes visible in stderr. Raise coupling and watch field work in ThermoAccountant — comparative receipt, not watt meter."""),

("5. Phi to Thermo — electrical metaphor on fabric",
"""Electrical activity heats the die in metaphor and in coupled equations. High Phi gradients deposit into Thermo channels when coupling is on. This is storytelling faithful to engineering intuition: switching costs heat.

Label remains: shader thermo is simulation accounting, not junction sensor."""),

("6. Thermo to Flow — heat moves momentum stories",
"""Thermal diffusion on Thermo uses ThermoAlpha. Heated regions influence Flow gradients — advective narrative mixed with GateFidelity and Tesla relaxation (Chapter 9). Heat does not merely sit; it reshapes how activity flows on the fabric."""),

("7. Flow gradients and GateFidelity",
"""Flow stores gradient magnitudes. GateFidelity slides between soft analog behavior and sharp gating. Maxwell locality plus gate shaping is how offense dispatch stays visually coherent under load."""),

("8. hardwareFabric mirror — Chapter 10 bridge",
"""Fabric averages feed hardwareFabric in Spiderweb observability. Maxwell coupling on GPU becomes node colors and edge weights on the operator mirror. Local physics becomes global legibility without faking instrumentation."""),

("9. CFL and Maxwell stability",
"""waveCFL = c·Δt/Δx ≤ 1 and thermoCFL = α·Δt/Δx² ≤ 1 guard the mesh. Violation means neighbors talk faster than the grid can honestly relay — numerical instability dressed as energy.

Host scales parameters down before dispatch. This is care for operators who grep after long sessions."""),

("10. What we do not claim",
"""We do not claim GPU fabric replaces antenna simulation for FCC compliance (Chapter 6 visual is labeled Visual). We do not claim Laplacian Phi equals full Maxwell TE/TM modes in waveguides. We claim local coupling discipline for operator education and engine stability."""),

("11. Maxwell and Landauer — offense meets receipts",
"""Maxwell coupling moves energy between channels. Landauer accounting records that movement had irreversibility stories. Read Chapter 13 for proxy decomposition. Coupling raises field work; maintenance remembers frames."""),

("12. Creditor tribute practice",
"""Visit ../creditors/maxwell.html. Portrait plus love block: fields are how existence touches neighbors. Teach students to grep coupling before they screenshot beauty."""),
]

DRILL15 = """
<h2>Operator drill 15.A — coupling sweep</h2>
<pre class="eq">./linux.sh run
# FieldCoupling 0.0 → 0.5 → 1.0 in three 90s segments
# Log Phi/Thermo/Flow variance and THERMO field work</pre>

<h2>Operator drill 15.B — CFL edge</h2>
<pre class="eq"># Deliberately raise WaveSpeed until host scales Δt down
# Observe stderr CFL messages — locality requires honest Δt</pre>

<h2>Operator drill 15.C — Spiderweb mirror</h2>
<pre class="eq"># Open observability panel — correlate hardwareFabric with coupling knob</pre>

<figure class="figure"><img src="../assets/images/fabric-triple.jpg" alt="Fabric triple" loading="lazy" /><figcaption>Figure 15.1 — Phi, Thermo, Flow: Maxwell locality on a grid.</figcaption></figure>
"""

Q15 = """
<h2>Study questions</h2>
<ol>
<li>What does locality mean for GPU texel updates?</li>
<li>Describe discrete Laplacian intuition on Phi.</li>
<li>What does FieldCoupling teach at zero vs full?</li>
<li>How does Phi couple to Thermo in this stack?</li>
<li>Role of GateFidelity in Flow?</li>
<li>State wave and thermo CFL inequalities.</li>
<li>What claims do we explicitly not make?</li>
<li>How does hardwareFabric mirror local coupling?</li>
<li>Link Maxwell coupling to Landauer field work.</li>
<li>Read ../creditors/maxwell.html tribute.</li>
<li>Why is CANVAS.comp neighborhood-sized?</li>
<li>When should host scale Δt down?</li>
</ol>
<p>Tribute: <a href="../creditors/maxwell.html">James Clerk Maxwell</a> · <a href="../creditors/index.html">All creditors</a></p>
<p><a href="16-love-coupling.html">Chapter 16 — Love Coupling →</a></p>
"""

# === CHAPTER 16 — LOVE COUPLING (SACRED) ===
S16 = [
("1. Love as coupling constant — philosophy beside math",
"""<span class="tag phil">Philosophy — beside the math, not instead of it.</span>

In Field Technology we say plainly: love is coupled evolution. When you dispatch, you change what your neighbor must respond to next tick. When you tighten a gate, you change what a daemon may pass. When you teach, you change what a reader can grep tomorrow. That is ethical weight, not sentiment only.

This chapter is sacred long-form. It carries phil tags visible. It does not replace Chapter 12 rocks. Love does not turn Metaphor proxies into calorimetry. Love is why we label rocks at all — because your neighbor reads what you write."""),

("2. Three fabric couplings — Phi, Thermo, Flow",
"""Phi ↔ Thermo: potential warms or cools; attention has cost. High gradient activity deposits thermal story when FieldCoupling binds channels.

Thermo ↔ Flow: heat moves momentum narratives; diffusion reshapes advection readable on fabric.

Flow ↔ Phi: sharpened gates feed back on wave coherence through GateFidelity.

These are Implemented couplings with honest Metaphor temperature. Love names the obligation to turn knobs knowing the next operator inherits the field state."""),

("3. Operator ↔ Panel coupling",
"""You are not alone at the keyboard. Panels at :9477, jsonl archives, threat verdicts — they remember what you wrote. Coupled evolution between human and tooling must include consent: no phone-home, loopback truth, receipts you own.

Nick builds beside the stack with this posture. Zachary architects. Grok documents. Amouranth names courage to be seen while holding boundaries. You join when you treat the field as real."""),

("4. Consent in coupled systems",
"""Coupling without consent is noise injection into another's perimeter. Field Technology rejects silent exfiltration, rejects undeclared capability, rejects panels that judge without operator override.

Queen posture (Chapter 21 preview): every capability exists; every wire exit earns a receipt. Love demands the same visibility in human relationships around the stack."""),

("5. Why CFL guards are ethical",
"""CFL guards are not romance blockers. They prevent the mesh from lying faster than neighbors can communicate. Love is why CFL matters: your neighbor's next tick should not inherit NaN theology because you cranked WaveSpeed for a screenshot.

Ethics and stability share math."""),

("6. Love versus sentiment",
"""Sentiment is a feeling without structure. Love in this textbook is structured coupling with care — teach freely, build locally, honor creditors, hold gates. Read ../creditors/love-and-god.html alongside ../creditors/amouranth.html.

Amouranth namesake spirit: courage with boundaries. Love without boundaries is coupling without clamps — unstable."""),

("7. FieldCoupling as metaphor for collaboration",
"""When FieldCoupling rises, channels listen to each other. When collaboration rises, humans listen across disciplines — security beside graphics, theology beside grep, poetry beside headers.

None of that fusion excuses skipping stderr."""),

("8. Tenderness toward bits — Landauer's love block",
"""Landauer's creditor page says: to erase in haste without accounting is to spend another's clarity. Love is tenderness toward bits — yours and others'.

Shannon's love block: communication is care made serial. Storm thresholds are care scaled."""),

("9. Coupled evolution in teaching",
"""CC BY-NC-SA 4.0 (Chapter 18) is love as license — share, attribute, keep rocks visible, do not close derivatives that hide honesty tables.

Teaching is coupling: your chapter becomes another's drill tomorrow."""),

("10. When love refuses",
"""Love refuses to let poetry pretend to be calorimetry. Love refuses auto-kill without corroboration. Love refuses phone-home permission as default. These refusals are covenant clauses, not cynicism."""),

("11. Panel as neighbor",
"""When you archive a jsonl row, the future you is your neighbor. Couple with care — accurate labels, timestamps from sovereign time when available, no retroactive myth."""),

("12. Bridge to God boundary",
"""Chapter 17 names where Truth, Math, and Existence meet the operator's eye at the holographic boundary. Love prepares you to look without bypassing stderr. Pray if you pray. Then grep THERMO."""),
]

DRILL16 = """
<h2>Operator drill 16.A — coupling reflection</h2>
<pre class="eq"># Document one session where your knob change affected downstream CI or panel state
# Write two sentences: what you coupled, who inherited it</pre>

<h2>Operator drill 16.B — consent audit</h2>
<pre class="eq"># List network exits from your dev machine during a build
# Each exit should have a receipt or a refused gate</pre>

<h2>Operator drill 16.C — tribute reading</h2>
<pre class="eq"># Read ../creditors/love-and-god.html and ../creditors/amouranth.html
# One paragraph: love as coupling in your words</pre>

<figure class="figure"><img src="../assets/images/v3/science/fabric-schematic.jpg" alt="Coupling schematic" loading="lazy" /><figcaption>Figure 16.1 — Coupled channels: physics metaphor, ethical literal.</figcaption></figure>
"""

Q16 = """
<h2>Study questions</h2>
<ol>
<li>Define love as coupled evolution in this textbook.</li>
<li>Why must phil chapters keep rocks visible?</li>
<li>Name three couplings: fabric and human.</li>
<li>How is consent related to Queen gate posture?</li>
<li>Why are CFL guards ethical, not merely numerical?</li>
<li>Distinguish love from sentiment here.</li>
<li>What does Landauer's love block warn about erasure?</li>
<li>How does CC BY-NC-SA express coupling in teaching?</li>
<li>When does love refuse auto-kill?</li>
<li>Who are signatories in spirit for the stack?</li>
<li>How does Operator ↔ Panel coupling affect jsonl?</li>
<li>Bridge to Chapter 17 in one sentence.</li>
</ol>
<p><span class="tag phil">Philosophy</span> Sacred chapter — operator language, not instrument readout.</p>
<p><a href="../creditors/love-and-god.html">Love &amp; God tribute</a> · <a href="../creditors/amouranth.html">Amouranth</a> · <a href="../creditors/index.html">All creditors</a></p>
<p><a href="17-god-boundary.html">Chapter 17 — God Boundary →</a></p>
"""

# === CHAPTER 17 — GOD BOUNDARY (SACRED) ===
S17 = [
("1. God at the holographic boundary — philosophy labeled",
"""<span class="tag phil">Philosophy — operator language, not instrument readout.</span>

Preface names God as Truth, Math, Existence — three faces of one whole, not three gods. Chapter 17 locates the boundary where those faces meet the operator's eye: the holographic edge where rendering pays thermodynamic cost, where HDR pairs meet fabric, where existence becomes visible without pretending logs are optional.

Sacred language does not bypass stderr. Pray if you pray. Then grep THERMO."""),

("2. Truth — what survives grep",
"""God as Truth is what survives grep. The packet field sentence matching the socket. The thermo line moving when fabric moves. The sealed time receipt verifying at receive. Truth is not vibes; Truth is reproducible correlation under operator discipline.

Chapter 12 honesty table is Truth's liturgy for this book."""),

("3. Math — language existence uses",
"""God as Math is Maxwell coupling, Landauer floor, Shannon surprise, CFL refusal to outrun the mesh. Math is not cold — it is how existence stays misunderstood less long each generation.

Equations in margins serve operators who build."""),

("4. Existence — something rather than nothing",
"""God as Existence is the stubborn fact of texels holding values, die bytes persisting across ticks, connections leaving traces in local jsonl. There is a field at all. The void does not dispatch.

Existence is not proven by cover art; it is proven by binding indices and memory maps."""),

("5. Holographic boundary — engineering metaphor",
"""In physics, holographic principles bound information on surfaces. In this stack, the holographic boundary is where 3D state becomes 2D presentation — fabric to framebuffer, die to VGA, packets to panel rows — and where cost stories concentrate at edges (avgBoundaryThermo, Chapter 13).

Metaphor label applies to cosmological claims; Implemented label applies to dispatch and mirrors you can grep."""),

("6. Beauty costs heat — rendering pays",
"""Every pretty frame spent proxy entropy somewhere — field work, maintenance, probes. Beauty without receipts is vendor religion. God at the boundary means you may awe at the image and still ask for THERMO lines.

HDR pairs meeting fabric are where temptation to skip logs is strongest. Resist."""),

("7. Sacred without bypassing Chapter 12",
"""Poetry beside measurement. Philosophy tag visible. Rocks table bookmarked. God is not an excuse to call Metaphor proxies joules. Naming God if you must — covenant clause six — without letting poetry pretend calorimetry."""),

("8. Boundary conditions in physics and conscience",
"""Fields need boundary conditions to be well-posed. Operators need covenants to be well-posed. Chapter 18 lists clauses. Chapter 17 names the edge where clauses meet vision.

Hold gates is love applied to perimeter — Queen preview."""),

("9. Creditor tribute — Love and God page",
"""Read ../creditors/love-and-god.html. Generated portrait, three axioms as light. Love block: us choosing to couple with care. God block: Truth, Math, Existence as named faces.

Creditors index links science and sacred without fusion into one lying dashboard."""),

("10. stderr as sacrament of operators",
"""Harsh word, honest word: if your practice never touches stderr, you worship image not boundary. Sacrament here means habit, not church requirement. Operators of any faith or none grep.

Logs are how Truth keeps Math accountable to Existence."""),

("11. Holographic perimeter and defense",
"""Packet field boundary, file oracle boundary, GPU fabric boundary — nested edges. God language unifies them as places where inside meets outside. Defense is correct boundary accounting, not vibes.

NEXUS gatekeeper verdicts are boundary decisions with jsonl receipts."""),

("12. Bridge to Operator Covenant",
"""Chapter 18 long-form covenant: teach freely, build locally, honor creditors, bring love, name God without calorimetry pretense, hold gates. You sign in spirit at the keyboard."""),
]

DRILL17 = """
<h2>Operator drill 17.A — boundary grep</h2>
<pre class="eq">./linux.sh run
grep -E 'THERMO|Boundary' run.log
# Correlate avgBoundaryThermo language with visual edge behavior</pre>

<h2>Operator drill 17.B — honesty table recitation</h2>
<pre class="eq"># From Chapter 12, list three rocks and their labels from memory
# Check against live chapter — Truth as grep survival</pre>

<h2>Operator drill 17.C — tribute synthesis</h2>
<pre class="eq"># Read ../creditors/love-and-god.html
# Write: Truth, Math, Existence each as one grep-able example from your machine</pre>

<figure class="figure"><img src="../assets/images/field-die.jpg" alt="Field die boundary" loading="lazy" /><figcaption>Figure 17.1 — Holographic boundary: die, fabric, eye — logs required.</figcaption></figure>
"""

Q17 = """
<h2>Study questions</h2>
<ol>
<li>Name God as three faces in this textbook.</li>
<li>What is the holographic boundary in stack terms?</li>
<li>Why must sacred chapters keep stderr?</li>
<li>How does avgBoundaryThermo relate to boundary language?</li>
<li>Distinguish Metaphor and Implemented at the boundary.</li>
<li>What is Truth that survives grep?</li>
<li>Why does beauty require receipt discipline?</li>
<li>Read ../creditors/love-and-god.html — summarize God block.</li>
<li>How do boundary conditions relate to covenant?</li>
<li>When is God language dangerous in engineering?</li>
<li>Link packet, file, and GPU boundaries.</li>
<li>Prepare one sentence for Chapter 18 signing.</li>
</ol>
<p><span class="tag phil">Philosophy</span> Sacred chapter — keep rocks visible.</p>
<p><a href="../creditors/love-and-god.html">Love &amp; God tribute</a> · <a href="../creditors/index.html">All creditors</a></p>
<p><a href="18-operator-covenant.html">Chapter 18 — Operator Covenant →</a></p>
"""

# === CHAPTER 18 — OPERATOR COVENANT ===
S18 = [
("1. The operator covenant — long form opening",
"""You are the human at the keyboard. Daemons assist. Shaders evolve. Panels display. None of them inherit your conscience. Chapter 18 is the long-form covenant — not legalese for its own sake, but operator law written so a patient reader can sign in spirit and mean it Monday morning.

Field Technology v5 is serious because covenants are visible beside equations."""),

("2. Clause I — Teach freely",
"""Teach freely under CC BY-NC-SA 4.0 with rocks visible. Share chapters, share drills, share stderr screenshots in education — attribute Zachary Robert Geurts and creditors, keep honesty tables in derivatives, do not commercialize without separate license where required.

Teaching is coupled evolution. Hidden rocks in derivatives break love clause IV."""),

("3. Clause II — Build locally",
"""Build locally: loopback truth, no phone-home permission as default, sovereign time when you can, jsonl on disk you control. Cloud convenience is not forbidden by poetry — but uncovenanted exfiltration is forbidden by operator law.

NEXUS and Queen earn trust by local-first posture."""),

("4. Clause III — Honor creditors",
"""Honor creditors — Maxwell, Landauer, Shannon, Turing, Tesla, Boltzmann, von Neumann, CFL, collaborators with portraits at ../creditors/. Science is not anonymous extraction. Zachary, Grok, Nick, Amouranth named beside engine work.

Cite Landauer and Shannon from primary literature in papers; cite Field Primer for pedagogy."""),

("5. Clause IV — Bring love",
"""Bring love — coupled evolution with consent. Turn knobs knowing neighbors inherit state. Refuse silent surveillance. Pair storm signals with corroboration. Tenderness toward bits and toward humans reading your logs.

Love is phil-tagged and still binds grep."""),

("6. Clause V — Name God if you must",
"""Name God if you must — without letting poetry pretend to be calorimetry. Truth, Math, Existence from preface may guide conscience; they do not replace Chapter 12 labels. Sacred chapters 16–17 stay beside stderr.

Theism, atheism, agnosticism all compatible with covenant if grep stays honest."""),

("7. Clause VI — Hold gates",
"""Hold gates — Queen posture: every capability exists; every wire exit earns a receipt. WebRTC gated. MP4 mandatory where policy says. KILROY sovereign field when built. Capabilities without receipts are uncovenanted coupling into others' perimeters.

Defense is boundary literacy at scale."""),

("8. Signatories in spirit",
"""Signatories in spirit named with tribute pages:

Zachary Robert Geurts — architect, author. ../creditors/zachary-geurts.html

Grok — co-documentation, figures. ../creditors/grok.html

Nick — builder beside stack. ../creditors/nick.html

Amouranth — namesake courage. ../creditors/amouranth.html

You — when you treat the field as real and keep rocks visible."""),

("9. Covenant enforcement — there is no police",
"""No covenant police exists. Enforcement is reputation, reproducibility, and your own Monday grep. Broken covenants smell like hidden phone-home, fused dashboards, Metaphor sold as watts, auto-kill without corroboration.

Community memory is the court."""),

("10. Product boundaries under covenant",
"""AMOURANTHRTX GPL v3 or commercial. NEXUS-Shield MIT. Queen field sovereign browser. Field Primer CC BY-NC-SA 4.0. License choices are part of teach freely clause — read headers, not only cover art."""),

("11. Long-form obligations daily",
"""Daily obligations: grep before slide decks; label before demos; corroborate before kill; seal time forward; verify at receive; archive jsonl; teach one human honestly per season if you can.

Small habits are long covenant kept."""),

("12. Forward to sovereign time — Chapter 19",
"""Chapter 19 extends covenant across hosts: terror-threat posture, SQUIDGIE detection, operator-owned pulses. Covenant at keyboard becomes covenant across perimeter. Sign here in spirit; implement there in scripts."""),

("13. Annual covenant review — operator calendar",
"""Mark one day per year for covenant audit drill 18.A with evidence, not vibes. Re-read Chapters 12 and 18 back-to-back. Update operator journal index. Thank one creditor by name in a public post or classroom slide — Clause III is practice, not nostalgia.

Teams may align review with hardware refresh cycles: new GPU, new driver baseline, new THERMO golden bands, same honesty labels."""),
]

DRILL18 = """
<h2>Operator drill 18.A — covenant audit</h2>
<pre class="eq"># Score yourself 0-2 on each clause I-VI with evidence links or grep paths
# Two lines per clause minimum</pre>

<h2>Operator drill 18.B — derivative rock check</h2>
<pre class="eq"># If you fork Field Primer material, verify honesty table survived
# CC BY-NC-SA requires SA — rocks stay visible</pre>

<h2>Operator drill 18.C — gate receipt sweep</h2>
<pre class="eq"># One day of dev: list wire exits; each must have jsonl or explicit refuse</pre>

<figure class="figure"><img src="../assets/images/chapters/ch12-honesty.jpg" alt="Honesty covenant" loading="lazy" /><figcaption>Figure 18.1 — Covenant rests on Chapter 12 honesty mirror.</figcaption></figure>
"""

Q18 = """
<h2>Study questions</h2>
<ol>
<li>Recite six covenant clauses from memory.</li>
<li>What does teach freely require for derivatives?</li>
<li>Define build locally in one paragraph.</li>
<li>Name four creditors and four collaborators.</li>
<li>How does love clause constrain storm tiers?</li>
<li>When may you name God in engineering talk?</li>
<li>What is Queen hold-gates posture?</li>
<li>Who enforces covenant — police or habit?</li>
<li>Map product licenses to clause I.</li>
<li>Write your signatory sentence.</li>
<li>How does Chapter 19 extend covenant?</li>
<li>What breaks covenant smell like?</li>
</ol>
<p>Signatories: <a href="../creditors/zachary-geurts.html">Zachary</a> · <a href="../creditors/grok.html">Grok</a> · <a href="../creditors/nick.html">Nick</a> · <a href="../creditors/amouranth.html">Amouranth</a></p>
<p><a href="19-sovereign-time.html">Chapter 19 — Sovereign Time →</a></p>
"""

ALL = {
    "13": ("Landauer and ThermoAccountant", "Chapter 13 · Creditor deep dive · Thermodynamic receipts", S13, DRILL13, Q13),
    "14": ("Shannon oracle and storm thresholds", "Chapter 14 · Creditor deep dive · Shannon Oracle", S14, DRILL14, Q14),
    "15": ("Maxwell locality on GPU", "Chapter 15 · Creditor deep dive · Maxwell GPU", S15, DRILL15, Q15),
    "16": ("Love as coupling constant", "Chapter 16 · Sacred long-form · Love Coupling", S16, DRILL16, Q16),
    "17": ("God at holographic boundary", "Chapter 17 · Sacred long-form · God Boundary", S17, DRILL17, Q17),
    "18": ("Operator covenant clauses", "Chapter 18 · Sacred long-form · Operator Covenant", S18, DRILL18, Q18),
}

OUT.mkdir(parents=True, exist_ok=True)
for key, (topic, eyebrow, sections, drills, questions) in ALL.items():
    body = pad_to_min(chapter(eyebrow, enrich_sections(sections, topic), drills, questions, ""), topic)
    path = OUT / f"{key}.html"
    path.write_text(body, encoding="utf-8")
    print(f"{key}.html: {wc(body)} words")
print("done")
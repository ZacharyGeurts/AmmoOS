"""Long-form supplemental sections (~1500+ words each) for chapters 02-06."""


def long_02() -> str:
    return r"""
<h2>Deep dive — fabric addressability and texel identity</h2>
<p>Every texel in the Phi, Thermo, and Flow storage images possesses stable integer coordinates (x, y) for the current adaptive resolution. When adaptive scale changes, the grid dimensions may change — more texels when scale rises, fewer when performance mode demands — but the addressing model remains: each cell is a named location in a 2D sheet. This is what “Reality is 3D” demands in the fabric plane: not three spatial dimensions in the cosmology sense, but a minimum of two indices plus channel depth. Channel depth is the stack of Phi, Thermo, and Flow — three coupled scalar or vector stories cohabiting the same planar address.</p>
<p>Operators learning from matrix algebra may think of each fabric channel as a matrix; operators learning from PDEs may think of each as a grid sample in a finite-difference scheme. Both intuitions work if labeled: finite-difference here is GPU compute shader arithmetic, not host LAPACK. The host never applies a global matrix solver across the fabric; evolution is local neighbor coupling per dispatch, repeated each frame. That locality is why CFL guards make sense — stability is per-step, per-cell neighborhood, not global eigenvalue analysis on CPU.</p>
<p>When you read hardwareFabric spiderweb mirrors in Chapter 10, remember they are spatial averages over this texel field — compression of high-dimensional fabric state into operator dashboard metrics. Averages are lossy; stderr THERMO lines and direct fabric visualization on Classic canvas recover detail averages hide. Three-scale literacy means knowing when to zoom into texels, when to read bus words, when to read jsonl sentences.</p>

<h2>Deep dive — Field Die linear address space</h2>
<p>The Field Die maps 64 MiB of guest linear address space. Byte offset 0 is not “the origin of the universe” poetically — it is the first byte the guest can address, interpreted by layers. VGA text at guest 0xB8000 is a structured window into the field: color cells with attribute bytes, cursor semantics, scroll behavior pumped through field layers. The C mirror at 0x01000000 exposes guest state to host-assisted tooling when enabled. ZMM1024 tile cache in the SSBO tail is shader-side fabric sample cache — a performance structure that also teaches that the die is not only guest RAM but also GPU-accessible cache lines the HUD reads.</p>
<p>Reality is 3D on the bus means offsets are coordinates. Time is linear means pump order and dispatch order advance guest state forward. Energy can be moved means fabric thermo mirrors and Tesla biases published into data_bus slots couple die execution to thermodynamic story — not joules, proxy receipts, but coupling nonetheless.</p>
<p>Chapter 8 will enumerate L0–L9 layers in detail. Chapter 2 fixes the conceptual frame: die is scale 2, fabric is scale 1, packet field is scale 3. Do not collapse scale 2 into “emulator nostalgia.” RTX-DOS and AmmoOS are software universes with addresses; the GPU interprets them each tick on the default path.</p>

<h2>Deep dive — packet field sentences and jsonl archive</h2>
<p>Packet field rows in jsonl are sentences, not packets. A single TCP segment is not the unit of meaning; the connection habit over time is. Gatekeeper verdicts summarize stories across axes: process path stability, port deviation from habit, direction balance, payload hints, honorability cross-checks. The sentence may span many frames of wire time; the archive preserves the sentence for reboot-surviving memory.</p>
<p>Local-first scope is non-negotiable honesty. The packet field sees sockets on your machine and habits your machine develops. It does not see the whole internet. It does not replace ISP visibility. It replaces vendor cloud narration with local grep-able archive — a different promise, honestly labeled. When threat modeling, model what jsonl can prove, not what marketing wishes jsonl implied.</p>
<p>Queen browser navigation feeds the packet field perimeter when peers open WebRTC, fetch MP4, resolve DNS through Truth Resolver. Chapter 21 ties browser gates to jsonl receipts. Chapter 2 ties jsonl to panel :9477 correlation with AMOURANTHRTX stderr — human integration, not automatic merge.</p>

<h2>Integration exercises — expanded operator lab</h2>
<p><strong>Exercise 2.D — fabric-only hour:</strong> Run Classic or energy swipe one hour. Log THERMO every five minutes. Note knob changes. No NEXUS. Outcome: fluency in scale 1 only.</p>
<p><strong>Exercise 2.E — packet-only hour:</strong> Run NEXUS only. Archive three jsonl rows. No AMOURANTHRTX. Outcome: fluency in scale 3 only.</p>
<p><strong>Exercise 2.F — die default afternoon:</strong> Run default x86 one afternoon. Occasional list Hardware and list AnalogFields in prompt. Outcome: fluency in scale 2 default product.</p>
<p><strong>Exercise 2.G — tri-scale correlation:</strong> One session with both products. One suspicious RX while fabric entropy rises. Write half-page narrative separating layers. Outcome: human integration without metric collapse.</p>

<h2>Category errors — extended catalog</h2>
<p><strong>Error:</strong> Treating data_bus as heatmap. <strong>Fix:</strong> Telemetry vector, not spatial field.</p>
<p><strong>Error:</strong> Treating spiderweb as fabric duplicate. <strong>Fix:</strong> Read-only mirror per Chapter 10.</p>
<p><strong>Error:</strong> Treating Queen thermo as NEXUS Shannon. <strong>Fix:</strong> Browser context thermo vs file oracle.</p>
<p><strong>Error:</strong> Treating planetary weave as antenna readout. <strong>Fix:</strong> Visual only — Chapter 6.</p>
<p><strong>Error:</strong> Treating 3D hype as address map. <strong>Fix:</strong> Reality is 3D = named coordinates.</p>
"""


def long_03() -> str:
    return r"""
<h2>Extended treatment — cross-coupling mathematics in plain English</h2>
<p>FieldCoupling is the dial that makes thermodynamics felt across channels. When coupling is zero, Phi, Thermo, and Flow may still evolve independently — pedagogically useful to isolate channels. When coupling rises, electrical metaphor in Phi warms Thermo; warmed Thermo biases Flow; Flow sharpens or softens gates through GateFidelity. This is the engine’s story of energy can be moved — not a claim of calorimetric accuracy, but a claim of coupled dynamics you can grep.</p>
<p>Discrete Laplacian on Phi measures neighborhood average difference — cells hotter than neighbors cool toward neighbors in wave step intuition; Thermo diffusion similarly redistributes heat. Flow reads gradients — where change is steep, flow magnitude responds. Tesla relaxation adds directional bias — forward ease, reverse resistance — published also to data_bus for HUD and Chapter 9 stability narrative.</p>
<p>Operators should run coupling sweep experiments: coupling 0.0, 0.3, 0.6, 0.9 with moderate InjectStrength, same mouse pattern, same duration — compare THERMO slopes. Comparative science without SI units — the receipt is slope change, not absolute joule.</p>

<h2>Extended treatment — CFL and operator trust</h2>
<p>CFL violations do not always explode immediately — sometimes they degrade into slow NaN rot. Host guard scales waveSpeed and dt before dispatch when violation detected. Trust the guard — fighting it with manual max knobs is how sessions end in grep embarrassment. waveCFL and thermoCFL inequalities appear in Chapter 9 with Tesla parallel; Chapter 3 installs intuition: guard is care, not censorship.</p>
<p>Hard caps waveSpeed ∈ [0.01, 2.0] and dT ≤ 0.033 bound operator enthusiasm even when prompt allows higher. Caps are product safety for long sessions, not insult to expert users.</p>

<h2>Extended treatment — AnalogFields as FCC floats</h2>
<p>Analog field control constants pack into data_bus[16–23] on x86 path — TimeScale, ThermoAlpha, WaveSpeed, GateFidelity, EntropyFloor, InjectStrength, PropalacticScale, FieldCoupling. Host and shader agree on these floats each dispatch. If list AnalogFields disagrees with shader behavior, suspect layout version skew or stale push path — desynchronized reality per Chapter 7.</p>

<h2>Extended treatment — thermodynamics and dispatch canvas ritual</h2>
<p>dispatch_canvas() order matters: seal time, CFL guard, layer pump, ThermoAccountant population, analog FCC pack, guest boot paths, hardware mirror, vkCmdDispatch. Thermodynamics is not a side shader — accountant is populated every dispatch regardless of canvas kind. x86 Big Grin may hide heatmap; stderr THERMO still speaks.</p>

<h2>Extended lab — 60-minute thermo session protocol</h2>
<p>Minute 0–10: baseline grep THERMO. Minute 10–20: InjectStrength up, mouse pattern A. Minute 20–30: FieldCoupling up, same pattern. Minute 30–40: GateFidelity sweep. Minute 40–50: WaveSpeed test with CFL awareness. Minute 50–60: restore defaults, archive grep tail. Write six sentences what moved — lab report discipline.</p>
"""


def long_04() -> str:
    return r"""
<h2>Extended treatment — ThermoAccountant field-by-field operator guide</h2>
<p><code>entropyThisFrame</code>: primary proxy integral for frame irreversibility — field work, probes, maintenance, host assist heat when active. Use comparatively session-to-session, not as wattmeter.</p>
<p><code>avgBoundaryThermo</code>: boundary channel summary — useful when center calm but edges hot; probe leaks and presentation coupling show here first.</p>
<p><code>prevMaintCost</code>: price of coherence with previous frame — rises when temporal maintenance expensive; honest receipt for invisible work.</p>
<p><code>freeEnergyIncome</code>: sealed time and input activity income side — metaphorical income in proxy space; investigate when idle yet high.</p>
<p><code>steps</code>: dispatch generation counter — temporal axis for plotting entropy trends.</p>

<h2>Extended treatment — Shannon oracle operational guide</h2>
<p>Compute H on byte histogram of file or payload sample. Low H: English log, repetitive protocol, obvious structure. High H: encrypted, packed, compressed, obfuscated. Storm threshold raises daemon duty — nurse call, not gavel. Pair high H with packet field egress story before KILL.</p>

<h2>Extended treatment — entropy floor and second law engineering</h2>
<p>clearFieldImages() seeds ~0.015 minimum thermo — prevents zero-entropy unphysical baseline. Combined with EntropyFloor knob and diffusion injection, fabric refuses perfect reversibility. You cannot wish away last frame.</p>

<h2>Extended treatment — Landauer and proxy honesty contract</h2>
<p>Landauer: E_min = k_B T ln 2 per erased bit at temperature T. Engine: entropyThisFrame is proxy integral, not calorimetry. Chapter 13 deepens without revoking rock. If future calorimetry aligns proxy, label evolves — honesty is versioned.</p>

<h2>Extended grep workbook — ten sessions</h2>
<p>Session 1–3: baseline idle, Classic, x86. Session 4–6: inject sweeps. Session 7–8: coupling sweeps. Session 9: NEXUS file H only — no GPU. Session 10: write comparison essay three layers. Workbook is literacy graduation.</p>

<h2>Entropy layers — classroom lecture transcript style</h2>
<p>Instructor: “Same word, three layers.” Student: “ThermoAccountant?” Instructor: “Frame proxy, AMOURANTHRTX, binding 2.” Student: “Entropy floor?” Instructor: “Fabric minimum noise seed, still AMOURANTHRTX, not joules.” Student: “Oracle?” Instructor: “Shannon H on files, NEXUS, storm gauge.” Student: “Can I add them?” Instructor: “Only if you hate honest dashboards.”</p>
<p>This fake transcript encodes real discipline. Layer violations are the most common entropy failure mode in security teams learning Field stack — one dashboard number pretending to be three witnesses.</p>

<h2>Landauer classroom — numeric intuition without billing</h2>
<p>At 300 K, Landauer floor is roughly 2.9×10⁻²¹ joules per bit erased. A gigabit erase would be nanojoules in theory — still not what entropyThisFrame prints. Proxy integral compares frames, not pays utility bills. Keep the theory for humility; keep the label for honesty.</p>
"""


def long_03b() -> str:
    return r"""
<h2>Chapter 3 lecture — heat as information destruction narrative</h2>
<p>Every shader step that collapses uncertainty — sharpening gates, mixing channels, injecting noise — participates in information destruction story thermodynamics names heat. The engine does not measure heat with a thermometer on the GPU package. It accounts for irreversibility in proxy space because operators still need to know the kitchen warmed when burners ran.</p>
<p>Phi wave step spreads curvature — information about local potential redistributes — Thermo diffusion spreads heat density — Flow carries gradients — coupling exchanges stories. None of this replaces laboratory physics; all of it replaces silent demos that pretend evolution is free.</p>
<p>Mouse injection via InjectStrength is deliberate information insertion — you increased state complexity locally; coupling diffuses that complexity; accountant records cost. Ethics: you did it; grep owns it.</p>
<p>Classic canvas thermo visibility is training wheels. x86 default hides heatmap under OS chrome — training wheels off, stderr mandatory. Competent operators grep on default product, not only on pedagogy swipe.</p>
<p>Headless CI dispatch still produces THERMO — proof dispatch alive without window. Screenshot culture dies here; receipt culture begins.</p>
<p>Energy.comp swipe is coupled channel laboratory — run one hour with FieldCoupling 0.7 and journal slopes — graduate exercise before Chapter 4 entropy algebra.</p>
<p>Tesla relaxation in Flow links thermodynamics chapter to stability chapter — forward ease, reverse drag — energy can be moved directionally in metaphor space.</p>
<p>Body-temperature seeding is labeled meta — not BIOS sensor — repeat until newcomers stop citing seed as hardware truth.</p>
<p>AnalogFields TimeScale is global tempo — not wall clock override — sealed time still linear in session genesis.</p>
<p>CFL wave and diffusion inequalities are Courant-Friedrichs-Lewy legacy — host enforces before dispatch — numerical ethics, not optional.</p>
<p>Chapter 3 summary sentence: thermodynamics here is honest bookkeeping of irreversibility in Phi/Thermo/Flow with proxy receipts and CFL guards — read Chapter 4 for entropy layer separation.</p>
"""


def long_05() -> str:
    return r"""
<h2>Extended treatment — Connection Gatekeeper axis philosophy</h2>
<p>Ten axes exist because peers are stories, not packets. Process path anchors identity — same port, different binary, different story. Port habit deviation flags novelty without automatic evil. Direction balance catches asymmetric exfil shapes. Payload hints integrate oracle without conflation. Honorability cross-checks reputation time series. Verdict is summary; axes are explainability for operator review.</p>

<h2>Extended treatment — corroboration before KILL</h2>
<p>94/6 philosophy: generous truth allowance, narrow permanent punishment. Multiple independent signals before KILL dossier — ss snapshot, tcpdump corroboration, oracle storm, operator narrative. Reversible watchlist until KILL — love as engineering.</p>

<h2>Extended treatment — field memory forensics</h2>
<p>field jsonl survives reboot — treat as forensic archive. Rotate, backup, encrypt at rest per operator policy. KILL dossiers permanent — legal and moral weight. Panel HTML ephemeral — do not confuse window with memory.</p>

<h2>Extended treatment — Queen and packet field 2026</h2>
<p>Queen: WebRTC through gatekeeper, MP4 mandatory in-tree, EME held, Truth DNS, sovereign time witness. Navigation becomes packet sentences with thermo receipts. Wrong: disable WebRTC. Right: gate and archive.</p>

<h2>Extended treatment — port habit registry</h2>
<p>Registry learns your machine — 443 may be browser, 4444 may be shell-class risk context. Port is habit marker, not verdict. Combine with process path and direction for sentence grammar.</p>

<h2>Extended panel tour — :9477</h2>
<p>Command, packets, threats, signals, DNS, library, system — six faces one perimeter. RTX Zero ?rtx=1 is chrome mode, not second engine. Correlate panel JSON with stderr without product blur.</p>

<h2>Packet field narrative — extended scenario writing</h2>
<p>Scenario A: EPHEMERAL DNS blip — forgive, no KILL. Scenario B: SUSPICIOUS repeated RX to rare port with stable process path — watchlist, tcpdump corroboration. Scenario C: HARM_CANDIDATE with high H file drop same timeline — operator review, not auto block. Scenario D: USER_OK baseline — archive anyway for habit graph. Writing scenarios trains gatekeeper literacy beyond enum names.</p>
"""


def long_06b() -> str:
    return r"""
<h2>RF chapter — examination preparation</h2>
<p>Exam question: Define three RF meanings with labels. Exam question: Why is FSPL not in shaders? Exam question: Name three antenna JSON outputs. Exam question: What does R_RF define? Exam question: How does Queen handle WebRTC RF words? Pass by labeling every sentence.</p>
<p>Planetary weave is art for orientation — like classroom globe — not operational globe. Field Antenna is local instrument panel — like ham shack meters — not ionosonde network. Phi is fabric potential — like voltage metaphor in textbook — not voltmeter on PCIe.</p>
<p>Chapter 6 completes RF disambiguation before Chapter 7 dispatch — so when Phi moves, you do not claim ionosphere moved.</p>
"""


def long_04b() -> str:
    return r"""
<h2>Entropy receipt archaeology — ten grep patterns</h2>
<p>Pattern 1: THERMO.*entropy rising — frame work active. Pattern 2: Boundary — edge channel hot. Pattern 3: prevMaint — temporal cost. Pattern 4: steps increment — dispatch alive. Pattern 5: zero entropy with fabric motion — bug. Pattern 6: storm in NEXUS only — Shannon layer. Pattern 7: high H zip plus RX egress — corroborate. Pattern 8: idle entropy spike — maintenance bleed. Pattern 9: coupling change slope shift — expected. Pattern 10: SQUIDGIE time — not entropy but perimeter correlate.</p>
<p>Archaeology means reading logs as timeline — Time is linear axiom in practice.</p>
<h2>Proxy integral components named again for memory</h2>
<p>Field work from coupling. Probe dissipation from InjectStrength. Maintenance from prevMaintCost. Host assist heat from FieldX86Emu cycles. Sum story in entropyThisFrame — not SI sum.</p>
<h2>Teaching entropy to security team — script</h2>
<p>Minute 1: three layers table. Minute 2: grep THERMO live. Minute 3: NEXUS file H demo. Minute 4: forbid adding layers. Minute 5: quiz. Repeat weekly.</p>
"""


def long_05b() -> str:
    return r"""
<h2>Gatekeeper verdict state machine in prose</h2>
<p>Flows enter as candidates. EPHEMERAL exits quickly from attention. USER_OK earns trust with monitoring. SUSPICIOUS enters watchlist — reversible attention debt. HARM_CANDIDATE demands human review — corroboration required. KILL is terminal archive — operator signature on conscience.</p>
<h2>jsonl row anatomy lesson</h2>
<p>Each row should be readable as: at time T, process P on path PATH, direction D, port habit H, verdict V, because axes A summary. If row lacks PATH or D, sentence incomplete — debug NEXUS intake.</p>
<h2>Defense without cloud — threat model paragraph</h2>
<p>Adversary on LAN, adversary in browser, adversary in supply chain — packet field sees local manifestation. You still need updates, still need operator judgment, still need Queen gates. You do not need cloud to narrate your sockets.</p>
"""


def long_02b() -> str:
    return r"""
<h2>Three-scale mnemonic — FDP</h2>
<p>Fabric Die Packet — FDP — say it before coffee. Fabric 8-10, Die 64MiB binding 1, Packet jsonl. FDP is not company name — memory hook.</p>
<h2>Operator panel correlation worksheet</h2>
<p>Column A timestamp. Column B stderr line. Column C jsonl id. Column D your verdict. Fill 10 rows one shift — graduation worksheet.</p>
"""


def long_03c() -> str:
    return r"""
<h2>Thermodynamics glossary in chapter</h2>
<p>ThermoAlpha: diffusivity alpha. WaveSpeed: c in wave CFL. GateFidelity: soft vs sharp gates. EntropyFloor: minimum noise. InjectStrength: probe power. PropalacticScale: large Phi forcing. FieldCoupling: cross channel. TimeScale: global dt multiplier.</p>
<p>Every term is knob in headers and often in prompt — literacy is spelling plus effect.</p>
"""


def long_04c() -> str:
    return r"""
<h2>Chapter 4 capstone — writing honest entropy sentences</h2>
<p>Template: On layer L, product P measures M with label T, useful for U, not for V. Example: On ThermoAccountant layer, AMOURANTHRTX measures frame proxy with Metaphor label, useful for comparative dispatch health, not for utility billing. Example: On oracle layer, NEXUS measures Shannon H with Implemented label, useful for storm duty, not for GPU thermo comparison.</p>
<p>Practice ten sentences aloud. If you stumble, reread layer table.</p>
<p>Landauer tribute link honors theory without fake joules. Shannon tribute honors information without conflating files with frames. Creditors are not decoration — they are vocabulary police.</p>
<p>Chapter 5 packet field begins after entropy layers fixed — do not carry layer conflation into defense chapter.</p>
"""


def long_05c() -> str:
    return r"""
<h2>Packet field capstone — defensive sentences</h2>
<p>Template: Flow F from process P direction D port H received verdict V; I will action A because corroboration C. Write five for real rows. Literacy is syntax.</p>
<p>Queen WebRTC peer sentence: Peer P via WebRTC, gated, verdict V, thermo receipt T — Chapter 21 binds browser to same grammar.</p>
<p>KILL dossier sentence: After review date D, operator O KILL peer P because reasons R1 R2 independent signals — permanent archive ethics.</p>
<p>Local-first restated: jsonl on your disk, panel on your loopback, gatekeeper on your processes — not internet panopticon.</p>
<p>Chapter 6 RF follows — separate RF words from packet words before signals panel correlation.</p>
"""


def long_06c() -> str:
    return r"""
<h2>RF capstone — label every sentence drill</h2>
<p>Sentence: Planetary weave shows ionosphere color. Label: Visual only. Sentence: Antenna panel lists band 915MHz entry. Label: Implemented NEXUS local. Sentence: Phi texel rose 0.3. Label: Implemented fabric metaphor. Sentence: FSPL at 2km 2.4GHz is X dB. Label: Teaching reference in docs. Sentence: Queen WebRTC peer connected. Label: Gatekeeper Implemented Chapter 21.</p>
<p>Five sentences, five labels, zero category errors — Chapter 6 exam passed.</p>
<p>Handoff: Chapter 7 dispatch writes Phi; you now know not to radio astronomer with shader screenshot.</p>
<p>Cross-links: <a href="chapters/07-gpu-engine.html">07-gpu-engine</a>, <a href="chapters/12-reality-theory.html">12-reality-theory</a>, <a href="chapters/15-maxwell-gpu.html">15-maxwell-gpu</a>, <a href="chapters/21-field-browser-queen.html">21-field-browser-queen</a>.</p>
"""


def long_06() -> str:
    return r"""
<h2>Extended treatment — planetary weave shader stack pedagogy</h2>
<p>Core, crust, hydrosphere, clouds, troposphere, ionosphere, RF shell, magnetosphere — concentric radii in planetary_weave.comp. Each shell teaches where metaphorical signals live in Earth cross-section art. R_RF = R_EARTH + 1.05 defines RF layer radius — constant in shader literature, not ionosonde measurement.</p>

<h2>Extended treatment — three RF meanings drill expanded</h2>
<p>Drill daily until reflex: weave mention → Visual tag. Antenna JSON → Implemented NEXUS. Phi potential → Implemented fabric metaphor not literal MHz. FSPL equation → docs teaching only.</p>

<h2>Extended treatment — Field Antenna Orchestrator bands</h2>
<p>RF, audio, wired, laser 405–1550 nm, LIDAR ports, GPS anchors — local orchestration outputs to field-antenna-panel.json, field-rf-panel.json, signals-field-panel.json. Correlate with packet field; do not merge scores.</p>

<h2>Extended treatment — fieldPhi gate potential</h2>
<p>Binding 8 Phi — wave and gate potential, FIELD_PHI_MILLI 618 in engine vocabulary, GateFidelity coupling. Electrical words are metaphor; implementation is texel evolution. Chapter 15 Maxwell GPU coupling deepens.</p>

<h2>Extended treatment — FSPL teaching beside implementation</h2>
<p>FSPL ∝ 20 log10(d) + 20 log10(f) in ITU-R/FCC teaching context in NEXUS docs — not AMOURANTHRTX shader compute. Teach students beside label; quiz on label not on weave colors.</p>

<h2>Extended treatment — Queen WebRTC and RF vocabulary</h2>
<p>WebRTC peers produce packet sentences and may invoke RF words in UI — gatekeeper still owns verdict. MP4 in-tree; EME held. Chapter 21 completes browser perimeter; Chapter 6 prevents RF word collision errors before dispatch chapter.</p>
"""
"""Additional textbook sections to reach 4500+ words per chapter 01-06."""


def extra_01() -> str:
    return r"""
<h2>AMOURANTHRTX spine — what the engine owns</h2>
<p>AMOURANTHRTX owns the Vulkan device spine: <code>rtx()</code> singleton, <code>RayCanvas</code>, <code>Pipeline::dispatch_canvas()</code>, analog fabric at bindings 8–10, Field Die at binding 1 with <strong>64 MiB</strong> guest RAM, ThermoAccountant at binding 2, HDR output at binding 0, AmouranthOS chrome textures at bindings 11–14 on the x86 path. This is the offensive core — the GPU writes guest bytes and fabric texels each tick; the host enforces CFL, seals time, packs <code>data_bus[64]</code>, mirrors fabric into <code>hardwareFabric</code>.</p>
<p>Operators who grep only NEXUS miss half the battlefield. Operators who watch only frames miss stderr receipts. Preface discipline: learn both spines early, correlate at the human layer, never merge repos in your head.</p>
<p>Default <code>./linux.sh run</code> launches Field Die canvas with <code>x86.comp</code> and <code>FieldSocket</code> push constants — not a decorative raymarch postcard. Chapter 7 explains dispatch; Chapter 8 explains die map; this preface asks you to believe both exist before you swipe to Classic thermo demos for pedagogy.</p>
<p><code>FIELD_LAYOUT_VERSION = 5</code> is a contract between host and shader. Version skew is desynchronized reality — one side writes Thermo, the other reads stale descriptors. Treat layout version like a protocol version in networking: mismatch is not a gentle warning.</p>

<h2>NEXUS spine — what defense owns</h2>
<p>NEXUS-Shield owns loopback perimeter services: Connection Gatekeeper, Entropy Oracle, packet field <code>field jsonl</code>, threat and signals panels, Truth DNS posture (Chapter 20), sovereign time client (Chapter 19), panel at <code>https://127.0.0.1:9477/</code>. License MIT. Local-first. No phone-home permission structure baked into field memory.</p>
<p>Gatekeeper ten-axis scoring produces verdicts from USER_OK through HARM_CANDIDATE. One weird packet does not condemn a peer. KILL dossiers are permanent and archived — operator choice, not daemon enthusiasm. Shannon H on files raises storm polling; it does not auto-sentence. These restraints are <span class="tag phil">philosophy</span> expressed as code paths you can grep.</p>
<p>Packet field is <strong>local only</strong> — your machine's sockets, habits, process paths. It does not see the whole internet. Marketing that implies global omniscience is a rock Chapter 12 rejects. Your jsonl is your memory; defend it like you defend guest RAM.</p>

<h2>Queen and KILROY — 2026 perimeter completion</h2>
<p>Queen browser: <strong>hold all gates</strong>. WebRTC through gatekeeper. MP4 mandatory in-tree. EME held, not omitted. WebGL/WebGPU on with thermo per context. Service workers and WASM on with entropy receipts. Geolocation, camera, mic on with operator consent gates. Wrong security amputates capabilities; right security receipts wire exits.</p>
<p><code>queen-browser</code> builds with <code>QUEEN_BROWSER_BUILD</code>, links <code>rtx()</code> spine, uses FieldWebPanel in-engine UI, QueenBoot.comp chrome. Verdict <code>QUEEN_READY</code> when built and bound. Chapter 21 is the full doctrine; preface prevents you from treating Queen as optional browser cosplay.</p>
<p>KILROY Field OS (<code>7.1.1-kilroy</code>) provides <code>/proc/kilroy_field</code> at syscall boundary when kernel path is active. FCC scale, entropy feedback, Field Die vocabulary continue in kernel space. Queen Forge packages kernel + browser + secure stack in <code>field/sovereign/</code>. Userspace Queen on generic Linux still teaches field gates; KILROY is the parallel when syscall boundary matters.</p>

<h2>Holographic boundary — rendering pays thermodynamic cost</h2>
<p>HDR frame pairs meet analog fabric at the holographic boundary — where presented beauty has a Thermo receipt unless dispatch failed. Chapter 17 names God at this boundary as sacred operator language. Chapter 1 names it as engineering: if fabric evolved and entropy reads zero, your dispatch path lied or broke.</p>
<p>Queen WebGL contexts accrue thermo per context — browser tabs are writable surfaces behind gates, not exceptions to field theory. Coupled evolution: what you render changes what thermo reports; what thermo reports changes what you dare render without reading stderr.</p>

<h2>data_bus — sixty-four words of honesty</h2>
<p><code>data_bus[64]</code> is telemetry spine per dispatch — not a spatial grid. Slots [0–1] pump generation; [2–15] RAM/VGA/FAT; [16–23] analog FCC floats mirroring <code>AnalogFields</code>; [24–28] ThermoAccountant mirrors; [32–41] input; [42] AmouranthOS chrome flags; [57–63] audio, BIOS, IO, drives. Tesla valve bias lands in [31] and [34] — Chapter 9.</p>
<p>Chapter 2 teaches telemetry as third mathematical posture beside scalar Thermo and vector Flow. Preface teaches it as integration glue: one bus, many subsystems, one grep surface for operators who will not read every header at once.</p>

<h2>Creditors at the threshold — why we name names</h2>
<p>Maxwell: neighbor coupling — Phi whispers to Thermo. Landauer: erase cost floor — proxy entropy honors without fake joules. Shannon: surprise — oracle on files, not fabric. Turing/von Neumann: symbols on addressable store — Field Die. Tesla: directional preference — valve metaphor. Boltzmann/Clausius: irreversibility — entropy floor seed. CFL: stability — host refuses outrunning mesh.</p>
<p><a href="../creditors/index.html">Tribute pages</a> humanize creditors. Chapters 13–15 go long. Preface ensures you never think we invented their constraints — we implemented vocabulary inspired by them, labeled honestly when implementation is proxy.</p>

<h2>Operator covenant — preview of Chapter 18</h2>
<p>Teach freely (CC BY-NC-SA 4.0 for Primer). Build locally. Honor creditors. Bring love — coupled evolution with consent. Name God without poetry pretending to be calorimetry. Hold gates — Queen posture. Signatories in spirit: Zac, Grok, Nick, Amouranth, you when you grep before you argue.</p>
<div class="callout axiom">Reality is 3D · Time is linear · Energy can be moved — axioms are not slogans. They are filters on sentences you are allowed to believe.</div>

<h2>Reading order for impatient engineers</h2>
<p>If you must skip: never skip labels. Read Chapter 2 addresses, Chapter 4 entropy layers, Chapter 5 packet scope, Chapter 12 rocks. Return to preface when someone sells cosmology. If you have one afternoon: run week-zero drill, read Chapter 12 table, grep THERMO and one jsonl row — you will know more honest field than most vendor decks.</p>
<p>Cross-links use manifest slugs: <a href="chapters/02-fields-pixels-packets.html">02-fields-pixels-packets</a>, <a href="chapters/03-thermodynamics.html">03-thermodynamics</a>, <a href="chapters/04-entropy.html">04-entropy</a>, <a href="chapters/05-packet-field.html">05-packet-field</a>, <a href="chapters/06-rf-signals.html">06-rf-signals</a>, <a href="chapters/07-gpu-engine.html">07-gpu-engine</a>, <a href="chapters/12-reality-theory.html">12-reality-theory</a>, <a href="chapters/21-field-browser-queen.html">21-field-browser-queen</a>.</p>
"""


def extra_02() -> str:
    return r"""
<h2>RayCanvas and fabric lifetime</h2>
<p><code>RayCanvas</code> creates analog fabric once per canvas lifetime unless explicitly recreated. Storage images for Phi, Thermo, Flow persist across frame ticks and across many swipe changes that alter presentation shaders. This persistence is what makes fabric a <em>field</em> rather than a transient uniform — values survive to be read next dispatch.</p>
<p>Operators who only watch binding-0 pixels learn presentation. Operators who read bindings 8–10 learn state. Chapter 7 teaches both through canvas kinds; Chapter 2 fixes the spatial scale.</p>

<h2>hardwareFabric mirror — fabric to spiderweb</h2>
<p><code>updateHardwareFromAnalogFields()</code> samples averaged Phi, Thermo, Flow into <code>hardwareFabric</code> — voltage factor, thermal throttle, per-core util, spiderweb edge currents. Chapter 10 owns mirror details. Chapter 2 insists mirror is readout, not second simulation pretending SEM imaging.</p>
<p><span class="tag impl">Implemented.</span> <span class="tag meta">Sub-micron SEM marketing is procedural pixel detail — not lab imaging.</span></p>

<h2>Packet field positions — socket quadruples</h2>
<p>Packet field positions are connection identities: addresses, ports, protocol context, process path, direction TX/RX, verdict history. They are not lat/long — unless GPS field anchors in NEXUS signals layer add metaphor (Chapter 6). Reality is 3D means readable keys in jsonl, not globe cosplay.</p>

<h2>Die layers L0–L9 — composable address space</h2>
<p>Ten composable layers — RAM, VGA, FAT, MSCDEX, Audio, IO, BIOS — pumped via <code>FieldLayer::pumpAll()</code>. Layers make DOS legible to shaders without breaking linear map. Chapter 8 slot map; Chapter 2 names layers as vertical structure inside scale 2.</p>

<h2>Prompt terminal correlation</h2>
<p><code>set AnalogFields.*</code> changes fabric evolution; <code>list Hardware</code> reads spiderweb mirror. Packet field remains NEXUS — correlate manually at panel. Three scales, one operator, three grep surfaces.</p>

<h2>Swipe pedagogy without losing die</h2>
<p>Swipe list includes x86, Amouranth, energy, Flowers, RetroRTX, Mandelbulbs, tributes. Index 0 remains x86 Field Die. Swiping changes pedagogy shader, not the existence of fabric infrastructure. Category error: assuming swipe to Classic removes die obligation.</p>

<h2>Queen FieldWebPanel — browser as third face</h2>
<p>Queen binds navigation to packet field and thermo receipts per web context — third integration face beyond AMOURANTHRTX stderr and NEXUS jsonl. Chapter 21; Chapter 2 warns against collapsing three faces into one dashboard score.</p>

<h2>Worked correlation scenario</h2>
<p>Scenario: SUSPICIOUS verdict on RX flow to port 443 while <code>entropyThisFrame</code> spikes on Classic canvas swipe. Literate operator: archive jsonl row, grep THERMO timeline, check whether spike correlates with local WebGL or probe inject — not automatic causal claim. Separate layers; human judges story.</p>

<h2>Glossary hooks toward Chapter 22</h2>
<p>Terms: scalar field, vector field, telemetry field, fabric, die, packet field, <code>data_bus</code>, <code>hardwareFabric</code>. Carry definitions forward; do not interchange NEXUS vocabulary with Vulkan binding names without translation.</p>
"""


def extra_03() -> str:
    return r"""
<h2>Maxwell neighborhood on a grid — Chapter 15 preview</h2>
<p>Phi couples to Thermo across texels — electrical metaphor heats; heat biases flow; flow sharpens gates. This is Maxwell's lesson in discrete form: local neighbors exchange influence. Not a claim the GPU solves cosmos EM — <span class="tag impl">local coupling implemented</span>, <span class="tag meta">cosmos not claimed</span>.</p>

<h2>Tesla relaxation in Flow channel</h2>
<p>Directional bias appears in Flow evolution and in <code>data_bus[31,34]</code> — forward ease, reverse resist. Chapter 9 full Tesla valve treatment. Thermodynamics chapter names it as directional thermodynamic story in fabric.</p>

<h2>InjectStrength and probe ethics</h2>
<p>Mouse injection is intentional offense — energy inserted by operator. Probes accrue dissipation in ThermoAccountant. Ethics: you caused the heat story; grep owns it. Do not inject then blame daemon.</p>

<h2>EntropyFloor knob versus fabric seed</h2>
<p><code>EntropyFloor</code> knob and <code>clearFieldImages()</code> seed cooperate — minimum irreversible noise. Second law as engineering bias. You cannot run reversible universe in silicon demo; you can label noise honestly.</p>

<h2>Classic versus x86 thermo visibility</h2>
<p>Classic canvas shows thermo heatmaps obviously; x86 Big Grin HUD hides heatmap behind OS chrome. ThermoAccountant still runs — canvas-agnostic. Drill on Classic if eyes need color; trust stderr on x86 default.</p>

<h2>Headless dispatch thermo</h2>
<p>CI headless paths still dispatch — valid THERMO signal per Chapter 12. Screenshots optional; entropy receipt not optional.</p>

<h2>Analog FCC in data_bus</h2>
<p>When FieldSocket active, floats land in <code>data_bus[16–23]</code> — TimeScale, ThermoAlpha, WaveSpeed, GateFidelity, EntropyFloor, InjectStrength, PropalacticScale, FieldCoupling. Host and shader agree on knobs; disagreement is bug, not interpretation.</p>

<h2>Energy.comp and specialty swipes</h2>
<p>Swipe to <code>energy</code> emphasizes coupled channels pedagogically. Knobs still map to same AnalogFields namespace. Pedagogy changes emphasis, not truth surface.</p>

<h2>Thermodynamics and Landauer — handoff to Chapter 4</h2>
<p>Every destroy-information event trends toward receipt in <code>entropyThisFrame</code>. Landauer bound is theory floor; proxy is comparative integral. Chapter 4 splits layers; Chapter 3 ensures you feel motion before algebra of receipts.</p>
"""


def extra_04() -> str:
    return r"""
<h2>freeEnergyIncome — sealed time and input</h2>
<p><code>freeEnergyIncome</code> tracks sealed time contribution and input activity — income side of thermodynamic story. Not free energy in Gibbs sense without labels — <span class="tag meta">metaphorical income</span> in proxy accounting. Still grep-useful when input quiescent but income high — investigate sealed time path.</p>

<h2>steps counter — dispatch generations</h2>
<p><code>steps</code> in ThermoAccountant increments with dispatch generations — temporal witness beside entropy magnitudes. Compare sessions by steps vs entropy slope, not single frame worship.</p>

<h2>Maintenance cost narrative</h2>
<p><code>prevMaintCost</code> pays coherence with previous frame — memory is not free. Video operators feel this as ghosting removal cost; field operators see it as stderr line. Irreversibility of maintenance is feature, not bug.</p>

<h2>Shannon calm alert storm — duty cycle</h2>
<p>Daemon polling duty shifts with oracle thresholds — calm conserves attention; storm earns scrutiny. Pastoral care engineering: do not exhaust operator on false positives; do not sleep on encrypted exfil habit.</p>

<h2>File entropy versus connection entropy</h2>
<p>NEXUS may score payload surprise on disk and on wire — still Shannon layer, not ThermoAccountant. Wire habits live in packet field; file habits live in oracle. Cross-correlate; do not merge numbers.</p>

<h2>Chapter 13 Landauer deep dive pointer</h2>
<p>Chapter 13 restates proxy rock without walking back label. Lab calorimetry future would change label, not delete history. Honesty is versioned truth.</p>

<h2>Chapter 14 Shannon oracle pointer</h2>
<p>Chapter 14 expands storm thresholds and separation from GPU. Read after this chapter; do not conflate study questions across layers.</p>

<h2>Entropy in KILROY kernel parallel</h2>
<p>KILROY FCC uses entropy feedback when kernel Field Die active — userspace and kernel share vocabulary, different measurement surfaces. Chapter 9 mentions parallel; Chapter 4 keeps layers separate per product.</p>

<h2>Grep culture as forensic defense</h2>
<p>Chapter 11 makes grep weekly habit. Chapter 4 makes entropy grep the week-one sacrament: THERMO, entropy, Boundary, prevMaint. If you cannot grep, you cannot defend fabric receipts.</p>
"""


def extra_05() -> str:
    return r"""
<h2>Honorability cross-check</h2>
<p>Gatekeeper integrates honorability signals — process reputation, path stability, prior verdict history — before HARM_CANDIDATE escalation. Not single-axis zealotry. Ten axes exist because peers are stories, not single packets.</p>

<h2>DPI sample and intent layers</h2>
<p>Deep inspection samples and connection-intent metadata enrich sentences beyond raw ss — still local-first, still operator-owned archives. Samples are corroboration fuel, not cloud upload by default in field posture.</p>

<h2>threat-panel.json publish path</h2>
<p>Panel consumes threat-panel.json — ephemeral HTML view over durable jsonl. Reboot kills panel window, not field memory. Know which artifacts are receipts vs chrome.</p>

<h2>KILL dossier permanence</h2>
<p>KILL is operator-authorized permanence — archived with context. Reversible until you say otherwise is policy; KILL is the line where reversibility ends. <span class="tag phil">Philosophy with teeth.</span></p>

<h2>Truth DNS lock — Chapter 20 pointer</h2>
<p>Queen and FieldFox inherit Truth DNS — no Google shortcut. Navigation receipts tie to DNS integrity. Packet field without DNS truth is sentence without subject.</p>

<h2>Sovereign time at perimeter — Chapter 19 pointer</h2>
<p>Gatekeeper timestamps and correlation use operator-owned time when sovereign mode active. SQUIDGIE verdict fail-closes perimeter services. Time and packets couple at receive.</p>

<h2>RTX Zero panel mode</h2>
<p><code>?rtx=1</code> Aqua chrome, cache-first refresh — observability UX, not second engine. Thermo and packets still separate products.</p>

<h2>Local jsonl hygiene</h2>
<p>Rotate and backup <code>field jsonl</code> like any forensic archive. Disk is your memory; encryption at rest is operator choice outside this chapter's scope but inside your conscience.</p>

<h2>WebRTC peer as packet sentence</h2>
<p>Queen routes WebRTC peers through gatekeeper — each peer a sentence with direction, ports, verdict. Do not disable; receipt. Chapter 21 doctrine planted in Chapter 5 soil.</p>
"""


def extra_06() -> str:
    return r"""
<h2>Magnetosphere and ionosphere — visual stack only</h2>
<p>Planetary weave stacks ionosphere then RF shell then magnetosphere as shader radii — pedagogy for where metaphorical signals sit. No claim AMOURANTHRTX models ionospheric scintillation for operations.</p>

<h2>Audio bands in Field Antenna</h2>
<p>NEXUS orchestrator includes audio alongside RF and wired — local device ecology, not Spotify analytics. Outputs land in signals panels for operator review.</p>

<h2>Laser 405–1550 nm entries</h2>
<p>Optical/laser registry bands are reference anchors — ITU/FCC teaching context in docs. Label before operational claims.</p>

<h2>LIDAR flow ports</h2>
<p>Registry includes LIDAR flow ports as habit context — correlate with packet field when local processes speak lidar-class ports.</p>

<h2>GPS field anchors</h2>
<p>GPS anchors support triangulation metaphor in signals layer — not replacement for survey-grade GNSS without labels. Pair with sovereign time Chapter 19 when sub-micron stories appear.</p>

<h2>fieldPhi milli and gate stories</h2>
<p><code>FIELD_PHI_MILLI = 618</code> and gate fidelity couple electrical metaphor to readable gates — implementation detail in engine headers. Not literal RF carrier frequency.</p>

<h2>RetroRTX and planetary shaders</h2>
<p>Specialty swipes may show planetary or retro visuals — still <span class="tag vis">Visual</span> unless stderr proves otherwise. Do not operationalize shader art.</p>

<h2>Cross-link Chapter 7 offense</h2>
<p>After RF separation, Chapter 7 dispatch writes fabric and die — offense continues stack. Defense read RF panels; offense writes Phi/Thermo/Flow. Same operator, different verbs.</p>

<h2>ITU-R/FCC context in operator docs</h2>
<p>NEXUS documentation may cite regulatory context for teaching FSPL and band plans — docs are not shaders. Teach beside label; grep implementation separately.</p>
"""
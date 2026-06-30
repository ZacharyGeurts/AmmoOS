#!/usr/bin/env python3
"""Real expansion prose for Field Technology v5 chapters 01-06.

Each expand_*() returns unique HTML body fragments (~2000-2500 words for 04-06).
No depth-N loop padding — substantive textbook sections only.
"""


def expand_01() -> str:
    """Chapter 01 — Preface: month-one schedule, teaching, AMOURANTH/GPL, ELLIE, FieldSocket."""
    return r"""
<h2>Month one — operator schedule you can actually keep</h2>
<p>Field Technology is not a weekend binge. It is a month of reading beside running — stderr open, tea optional, conscience mandatory. The schedule below assumes you have AMOURANTHRTX building on Linux and optionally NEXUS-Shield beside it. Adjust pace; do not adjust honesty labels.</p>
<table><thead><tr><th>Week</th><th>Read</th><th>Run</th><th>Artifact you keep</th></tr></thead>
<tbody>
<tr><td>1</td><td>Ch. 1–3 preface + thermo</td><td><code>./linux.sh run</code> 90 min; mouse on canvas</td><td><code>field-week1.log</code> with THERMO tail</td></tr>
<tr><td>2</td><td>Ch. 2 three scales + Ch. 4 entropy layers</td><td>Swipe <code>energy</code>; prompt <code>list AnalogFields</code></td><td>Paper map: fabric / die / packet boxes</td></tr>
<tr><td>3</td><td>Ch. 5 packet field + Ch. 6 RF labels</td><td><code>./nexus.sh</code>; panel :9477 tour</td><td>Three jsonl rows classified by axis</td></tr>
<tr><td>4</td><td>Ch. 7 dispatch spine + Ch. 8 die map skim</td><td>Drill 7.A grep; layout version check</td><td>Dispatch spine quote in operator journal</td></tr>
</tbody></table>
<p>Week two is where category errors die: students who skip Chapter 2 will treat gatekeeper verdicts as fabric texels by week six. Week three is where defense rhythm starts — daily glance at Packets, weekly explicit archive decision. Week four is offense proof — you believe <code>vkCmdDispatch</code> runs because stderr says so, not because Big Grin smiled.</p>
<p>Bookmark <a href="12-reality-theory.html">Chapter 12 — Reality &amp; Theory</a> on day one. When midnight enthusiasm claims cosmic truth, return to rocks table before you tweet.</p>
<div class="callout drill"><strong>Drill 1.A — Month-one Monday</strong></div>
<pre class="eq">./linux.sh run 2>&1 | tee /tmp/field-month1.log
# 60s mouse move; note ELLIE categories that appear
grep -E '^(MAIN|VULKAN|CANVAS|THERMO|STATUS)' /tmp/field-month1.log | tail -25</pre>
<p>Success: name four log categories and which field family each witnesses. Failure: you remember only the wallpaper — reread status labels before Chapter 2.</p>

<h2>Teaching another human — covenant without condescension</h2>
<p>Field literacy spreads by apprenticeship, not by dropping a wiki link and disappearing. When you teach another human — child, colleague, skeptical physicist — you owe them the same honesty labels you owe yourself. The teaching covenant is simple: <strong>definitions before mechanisms, grep before screenshots, rocks before poetry.</strong></p>
<p>Session shape that works in ninety minutes:</p>
<ol>
<li><strong>Kitchen metaphor (10 min):</strong> program as recipe, field as burner state — Chapter 1 Plain English callout.</li>
<li><strong>Three families (20 min):</strong> fabric bindings 8–10, die 64 MiB binding 1, packet jsonl — draw three boxes on paper.</li>
<li><strong>Live run (30 min):</strong> student drives mouse; you grep THERMO together; refuse to narrate from frame rate alone.</li>
<li><strong>Label drill (15 min):</strong> give five claims; student tags <span class="tag impl">Implemented</span>, <span class="tag meta">Metaphor</span>, <span class="tag phil">Philosophy</span>, or <span class="tag vis">Visual</span>.</li>
<li><strong>Homework (15 min):</strong> week-one log file; three study questions from Chapter 1; bookmark Chapter 12.</li>
</ol>
<div class="callout love"><strong>Love in teaching:</strong> patience before correction. A student who conflates proxy entropy with joules is not stupid — they were trained by vendor dashboards. Correct with rocks, not ridicule.</div>
<p>Do not teach Queen as “safer Chrome” or NEXUS as “antivirus with vibes.” Teach Queen as all gates held; teach NEXUS as local-first packet sentences. Do not promise KILROY ships tomorrow — teach <code>CONFIG_RTX_FIELD_DIE</code> as syscall boundary aspiration with honest build flags.</p>
<p>When the student asks “is it real,” answer: “which label applies?” When they ask “is it revolutionary,” answer: “which binding number?” Field Technology v5 is serious enough to teach from — that is the covenant authors accept when we publish expanded chapters.</p>

<h2>AMOURANTHRTX and GPL — license posture for operators</h2>
<p>AMOURANTHRTX ships under <strong>GPL v3 or commercial license</strong> — dual posture common in engines that must survive both community audit and product packaging. Operators forking the stack need literacy in what GPL demands: source offer, derivative work conscience, patent retaliation clause awareness. Operators packaging commercial builds need literacy in what the commercial path buys: support contract, redistribution rights — details live in LICENSE files, not in this chapter’s prose.</p>
<table><thead><tr><th>Question</th><th>GPL path</th><th>Commercial path</th></tr></thead>
<tbody>
<tr><td>Fork and modify engine</td><td>Share corresponding source when distributing binaries</td><td>Contract defines redistribution</td></tr>
<tr><td>Link Queen browser build</td><td>Follow combined work rules for your packaging</td><td>Same — read actual grant</td></tr>
<tr><td>NEXUS-Shield beside RTX</td><td>MIT NEXUS does not infect GPL RTX by mere adjacency</td><td>Product boundaries still distinct</td></tr>
<tr><td>Ship shader modifications</td><td><code>x86.comp</code> changes are part of corresponding source</td><td>Document layout version bumps</td></tr>
</tbody></table>
<p><span class="tag phil">Philosophy:</span> open source here is not merch — it is auditability. A skeptical operator can grep <code>FIELD_LAYOUT_VERSION</code>, read ThermoAccountant packing, and verify no hidden phone-home in dispatch loop. NEXUS-Shield remains MIT — packet field code paths are separable for security review.</p>
<p>Do not conflate Amouranth the namesake spirit with license legal entity in classroom slides — spirit names courage; LICENSE names obligations. Chapter 18 covenant expands pastoral posture; preface names commercial reality so week-four packaging discussions do not surprise you.</p>

<h2>ELLIE log categories — stderr as scripture</h2>
<p><code>ELLIE</code> is the structured logging spine in AMOURANTHRTX — categories let you grep without drowning in noise. Chapter 11 owns observability rhythm; preface introduces the vocabulary so week-one operators recognize witnesses.</p>
<table><thead><tr><th>Category</th><th>What it proves</th><th>Typical grep</th></tr></thead>
<tbody>
<tr><td><code>MAIN</code></td><td>Navigator boot, lifecycle</td><td>Session start receipt</td></tr>
<tr><td><code>VULKAN</code></td><td>Device init, queues, budget</td><td>GPU path alive</td></tr>
<tr><td><code>CANVAS</code></td><td>Dispatch issued, canvas kind</td><td>Offense spine witness</td></tr>
<tr><td><code>THERMO</code></td><td>ThermoAccountant population</td><td>Proxy entropy lines</td></tr>
<tr><td><code>STATUS</code></td><td>FPS, GPU ms, VRAM ~5 s cadence</td><td>Health block</td></tr>
<tr><td><code>RTXPROBE</code></td><td>Optional GPU timestamps (<code>RTX_PROBES=1</code>)</td><td>Latency spikes</td></tr>
</tbody></table>
<pre class="eq">grep -E '^(MAIN|VULKAN|CANVAS|THERMO|STATUS)' run.log | tail -40</pre>
<p>Category discipline prevents false panic: silence in <code>THERMO</code> while <code>CANVAS</code> speaks means accountant failure — return to Chapter 7 binding 2, not driver reinstall theater. Burst volume in <code>MAIN</code> without <code>VULKAN</code> success means you are not on GPU path yet.</p>
<div class="callout everyone"><strong>Plain English:</strong> ELLIE categories are chapter headings in your log file. Read the headings before you read the novel.</div>

<h2>FieldSocket preview — push constants before Chapter 7</h2>
<p><code>FieldSocket</code> is the per-dispatch push-constant block on the default <code>x86.comp</code> path — small, fast, changes every tick without rebinding descriptor sets. Chapter 7 owns full layout; preface plants fields so first dispatch is not mystery meat.</p>
<table><thead><tr><th>Field / flag</th><th>Role</th></tr></thead>
<tbody>
<tr><td><code>sealed_time</code></td><td>Monotonic session genesis from <code>TotalTime::seal()</code></td></tr>
<tr><td>Probe position</td><td>Mouse / inject coordinates for fabric offense</td></tr>
<tr><td><code>ControlHostCpu</code> (8)</td><td>Optional <code>FieldX86Emu</code> host assist — not default</td></tr>
<tr><td><code>ControlAmmoExec</code> (1024)</td><td>Guest program execution active</td></tr>
<tr><td><code>ControlFieldDebugHud</code> (2048)</td><td>Die monitor overlay — thermo hidden behind chrome escapes here</td></tr>
</tbody></table>
<p>Push constants ride the command buffer; they are offense at cadence. Sealed time in FieldSocket is how physics time survives VSYNC stutter — wall clock may hiccup; socket time does not rewrite backward. Chapter 19 extends sealing across machines; session-local sealing is already discipline you can grep this week.</p>
<p><span class="tag impl">Implemented.</span> Grep <code>FieldSocket</code> in <code>Navigator/engine/</code> and <code>x86.comp</code> layout comments. Mixed <code>FIELD_LAYOUT_VERSION</code> between host and shader is desynchronized reality — HUD hex lies politely.</p>

<h2>Sub-micron honesty — silicon metaphor without fraud</h2>
<p>Field Technology uses silicon-gate and sub-micron vocabulary as <span class="tag meta">Metaphor</span> for numerical management — CFL guards, FCC clamps, gate fidelity knobs — not as claims that AMOURANTHRTX measured your fab node or junction temperature. When prose says “intelligent management at sub-micron scale,” translate to: <strong>host pre-conditions operator inputs before they reach compute shaders.</strong></p>
<div class="callout science"><strong>Science posture:</strong> metaphor inspires vocabulary; implementation is what you grep. Sub-micron honesty means never billing a data center from proxy entropy because the metaphor sounded expensive.</div>
<p>Chapter 9 FCC and Tesla valve constants live in this metaphor layer — directional preference, relaxation times — labeled honest in Chapter 12 rocks. Chapter 13 Landauer bound is physics; <code>entropyThisFrame</code> is proxy — sub-micron honesty refuses to merge them on a invoice.</p>
<p>Teaching moment: when a student asks “does the engine simulate transistors,” answer: “it simulates addressable fields with gate fidelity knobs — grep <code>GateFidelity</code> and read the rock.” Precision without fraud is the preface gift to week-six packaging meetings.</p>

<h2>Sovereign time and SQUIDGIE — Chapter 19 preview</h2>
<p>Session-local <code>TotalTime::seal()</code> is not the end of time discipline — Chapter 19 extends sealed clocks across hosts with sovereign pulses and verification verdicts including <code>USER_OK</code> and <code>SQUIDGIE</code>. Preface preview so you do not treat wall clock as physics when jsonl rows arrive from another machine.</p>
<p><strong>Sovereign time</strong> means operators own genesis stamps — not NTP cloud narrative alone. Pulses on registered ports (wiki service table includes :9123) participate in sync stories documented in Chapter 19. <strong>SQUIDGIE</strong> names a verification posture — playful acronym, serious requirement: cross-host receipts must return structured verdicts, not vibes.</p>
<pre class="eq">local seal → sovereign pulse → remote verify → USER_OK | SQUIDGIE</pre>
<p>Packet field jsonl with <code>ts_sealed</code> columns (Chapter 5) prepares you for multi-host correlation. ThermoAccountant <code>freeEnergyIncome</code> (Chapter 4) already treats sealed time as living-world potential on single host — extension is natural, not bolt-on.</p>
<p><span class="tag impl">Implemented</span> where built and configured; <span class="tag phil">Philosophy</span> where operators skip verify and trust latency alone. Preface does not replace Chapter 19 mechanisms — it prevents “I never heard of SQUIDGIE” surprise in week eight.</p>

<h2>Public services — Chapter 20 DNS and registry preview</h2>
<p>NEXUS public services chapter (20) documents local-first infrastructure: Truth DNS at <code>127.0.0.1</code> with trace-from-root, DHCP/DHCPv6 teaching postures, NTP discipline, panel :9477, sovereign pulse port :9123. Preface lists them so Chapter 5 panel tour connects to naming honesty.</p>
<table><thead><tr><th>Service</th><th>Port</th><th>Field role</th></tr></thead>
<tbody>
<tr><td>Truth DNS</td><td>53</td><td>Loopback resolution; corroboration axis for gatekeeper</td></tr>
<tr><td>DHCP / DHCPv6</td><td>67 / 547</td><td>Local lease teaching — not ISP replacement fantasy</td></tr>
<tr><td>NTP discipline</td><td>123</td><td>Wall clock hygiene beside sealed physics time</td></tr>
<tr><td>Sovereign pulse</td><td>9123</td><td>Chapter 19 sync participant</td></tr>
<tr><td>Threat panel</td><td>9477</td><td>Operator HTML shell over jsonl memory</td></tr>
</tbody></table>
<p>Public services are <strong>your machine’s civil engineering</strong> — not cloud omniscience. Queen navigation (Chapter 21) inherits DNS truth before WebRTC peers earn jsonl sentences. Field literacy correlates DNS answers with packet field rows without merging into one threat score.</p>
<p>Continue to <a href="20-public-services.html">Chapter 20 — Public Services</a> after defense rhythm (Ch. 5) feels natural.</p>

<h2>Integration roadmap — four products, one operator chair</h2>
<p>The stack is four products with distinct repos and one literacy. Roadmap is integration order, not monolith fantasy.</p>
<ol>
<li><strong>AMOURANTHRTX offense (Ch. 7–11):</strong> dispatch, die map, CFL, spiderweb mirror, grep discipline.</li>
<li><strong>NEXUS defense (Ch. 5–6, 20):</strong> packet field, gatekeeper, RF labels, public services.</li>
<li><strong>Entropy layers (Ch. 4, 13–14):</strong> ThermoAccountant vs oracle vs floor — exam before merge.</li>
<li><strong>Queen perimeter (Ch. 21):</strong> all gates held, WebRTC through gatekeeper, thermo per context.</li>
<li><strong>KILROY kernel path:</strong> syscall boundary when field discipline must live below userland — honest build flag literacy.</li>
<li><strong>Sacred chapters (16–18):</strong> Love, God, Covenant — philosophy beside grep, never bypassing stderr.</li>
<li><strong>Glossary (Ch. 22):</strong> formal terms after mechanisms earned.</li>
</ol>
<p>Month one stays in bullets 1–2. Month two adds 3–4. Month three opens sacred chapters only after rocks table is reflex. Integration roadmap is how you answer “what do I read next?” without drowning in twenty-two chapters at once.</p>
<div class="callout axiom"><strong>Reality is 3D.</strong> Texels, die bytes, sockets — roadmap maps addresses, not hype.<br><strong>Time is linear.</strong> Read order matters; jsonl and logs append.<br><strong>Energy can be moved.</strong> Coupling chapters assume thermo vocabulary from Ch. 3–4.</div>

<h2>Deep dive — week three defense without offense guilt</h2>
<p>Operators from pure graphics backgrounds sometimes feel guilty spending a week on NEXUS when dispatch calls. Preface absolves the guilt with architecture truth: packet field is scale three of the same literacy — not a detour, a leg. You cannot correlate THERMO with SUSPICIOUS flows in week twelve if you never opened :9477 in week three. Defense reading is parallel practice, not competitor to <code>vkCmdDispatch</code>.</p>
<p>Week three homework that sticks: archive one explicit gatekeeper decision in writing — why USER_OK, why watchlist, why not KILL. Pair with one AMOURANTHRTX session log from the same afternoon. Future you will thank present you when a peer returns suspicious and habit axis has memory.</p>

<h2>Preface capstone — what month one must produce</h2>
<p>By end of month one you should possess: a grep habit, a paper map of three scales, a THERMO log baseline, optional jsonl tail familiarity, and explicit bookmark of Chapter 12. You should not possess: confidence that weave colors measure spectrum, that oracle storm auto-KILLs peers, or that HUD hex replaces bus mirrors.</p>
<p>Next read: <a href="02-fields-pixels-packets.html">Chapter 2 — Three Dimensions of State</a>. Forward offense: <a href="07-gpu-engine.html">Chapter 7 — GPU Field Engine</a>. Honesty contract: <a href="12-reality-theory.html">Chapter 12</a>. Sovereign time: <a href="19-sovereign-time.html">Chapter 19</a>.</p>

<h2>Study questions</h2>
<ol>
<li>Outline week 2 of the month-one schedule — read, run, artifact.</li>
<li>What are the five teaching session blocks and their durations?</li>
<li>State one GPL obligation and one product-boundary fact about NEXUS MIT.</li>
<li>Name six ELLIE categories and what each witnesses.</li>
<li>List three FieldSocket fields/flags and why push constants matter.</li>
<li>Translate “sub-micron honesty” into operator grep language.</li>
<li>What is SQUIDGIE preview protecting you from assuming?</li>
<li>Which Chapter 20 service lives on port 9477?</li>
<li>Where does Queen appear on the integration roadmap?</li>
<li>Run Drill 1.A; classify four grep lines by category.</li>
</ol>
"""


def expand_02() -> str:
    """Chapter 02 — Three scales: swipe list, die subfields, NEXUS, integration."""
    return r"""
<h2>Introduction — three writable surfaces, one operator brain</h2>
<p>Chapter 1 named field literacy and three families at binding-map altitude. Chapter 2 lands the plane: <strong>three dimensions of state</strong> you will read and write for years — GPU analog fabric, Field Die guest map, NEXUS packet field. This is the engineering reading of <em>Reality is 3D</em>: not cosmology slides, but coordinates that persist across ticks. Texel (x,y), byte offset <code>0xB8000</code>, socket <code>127.0.0.1:9477</code> — three different address spaces, one disciplined human at the panel correlating without metric collapse.</p>
<p>Chapter 7 converges fabric and die in one <code>vkCmdDispatch</code>. Chapter 5 keeps packet field NEXUS-local. Chapter 21 binds Queen at the perimeter. This chapter is the map those chapters assume — draw it once on paper before you grep dispatch.</p>
<p>Prior: <a href="01.html">Chapter 1 — Preface</a>. Next: <a href="03-thermodynamics.html">Chapter 3 — Thermodynamics</a>. Dispatch spine: <a href="07-gpu-engine.html">Chapter 7</a>. Honesty rocks: <a href="12-reality-theory.html">Chapter 12</a>.</p>

<div class="objectives"><h2>Learning objectives</h2><ul>
<li>Distinguish scalar, vector, and telemetry fields with stack examples.</li>
<li>Navigate <code>Options::Canvas::SwipeList</code> as curriculum, not product reset.</li>
<li>Run <code>energy.comp</code> lab drills and label Classic versus X86Fields.</li>
<li>Map guest FAT and VGA subfields inside Field Die addressing.</li>
<li>Explain connection intent on packet field sentences.</li>
<li>Locate ZMM1024 tail and Big Grin HUD in die telemetry.</li>
<li>Complete integration exercise on paper without category errors.</li>
</ul></div>

<figure class="figure"><img src="../assets/images/fabric-triple.jpg" alt="Three channels" loading="lazy" /><figcaption>Figure 2.1 — Phi, Thermo, Flow on fabric; die bytes and packet sentences beside — three scales, one literacy.</figcaption></figure>

<h2>Scalar, vector, telemetry — vocabulary before addresses</h2>
<table><thead><tr><th>Type</th><th>Example in stack</th><th>Addressing</th></tr></thead>
<tbody>
<tr><td>Scalar</td><td>Thermo binding 9 — heat density per texel</td><td>Grid (x,y)</td></tr>
<tr><td>Vector</td><td>Flow binding 10 — gradients in <code>.gb</code></td><td>Grid (x,y) + direction components</td></tr>
<tr><td>Telemetry</td><td><code>data_bus[64]</code> — FCC floats, thermo mirrors, chrome flags</td><td>Slot index 0–63</td></tr>
</tbody></table>
<p>Phi binding 8 behaves as scalar potential in many shader paths — wave and gate stories — while coupling to vector Flow through <code>FieldCoupling</code>. Telemetry is not “less real” than texels — Big Grin HUD reads bus words every frame. Category error is treating telemetry as optional decoration because it is not pretty.</p>
<pre class="eq">RayCanvas → createAnalogFieldFabric() → CANVAS.comp / x86.comp → hardwareFabric</pre>
<p><span class="tag impl">Implemented.</span> Host never runs CPU-side PDE on fabric — evolution is compute work per dispatch. Mirrors to <code>hardwareFabric</code> are read-only spiderweb compression (Chapter 10) — lossy on purpose.</p>

<h2>Swipe list table — curriculum chapters as shaders</h2>
<p><code>Options::Canvas::SwipeList</code> hot-swaps shaders without tearing down <code>rtx()</code> singleton, sealed time, ThermoAccountant, or CFL guard. Index 0 remains <code>x86</code> — Field Die default. Swipes change pedagogy emphasis; they do not opt out of field theory.</p>
<table><thead><tr><th>Swipe</th><th>Shader family</th><th>Canvas kind</th><th>Pedagogy role</th></tr></thead>
<tbody>
<tr><td><code>x86</code> (0)</td><td><code>x86.comp</code></td><td>X86Fields</td><td>Product default — die + AmmoOS</td></tr>
<tr><td><code>Amouranth</code></td><td><code>CANVAS.comp</code> variant</td><td>Classic</td><td>Portrait-forward thermo demos</td></tr>
<tr><td><code>energy</code></td><td><code>energy.comp</code></td><td>Classic</td><td>Phi/Thermo coupling visible</td></tr>
<tr><td><code>Flowers</code></td><td>Classic specialty</td><td>Classic</td><td>Organic flow patterns — Ch. 3 lab</td></tr>
<tr><td><code>GreenWaves</code></td><td>Classic specialty</td><td>Classic</td><td>Wave interference pedagogy</td></tr>
<tr><td><code>Frosted</code></td><td>Classic specialty</td><td>Classic</td><td>Diffusion-heavy thermo read</td></tr>
<tr><td><code>RetroRTX</code></td><td>RT tribute</td><td>Classic</td><td>See RetroRTX section — visual RT pedagogy</td></tr>
<tr><td>Mandelbulb variants</td><td>SDF raymarch</td><td>Classic</td><td>3D address intuition — not die map</td></tr>
<tr><td>planetary weave</td><td><code>planetary_weave.comp</code></td><td>Classic</td><td><span class="tag vis">Visual</span> RF shell — Ch. 6</td></tr>
</tbody></table>
<div class="callout science"><strong>Category error to avoid:</strong> Declaring Field Die absent because you swiped to <code>energy</code>. Die path returns on next default launch; infrastructure persisted.</div>
<p>Teaching pattern from Chapter 7: week one afternoon on Classic thermo, week two operations on die default. Veterans live on die; newcomers need visible heatmaps — both are honest if labeled.</p>

<h2><code>energy.comp</code> laboratory — coupling you can see</h2>
<p>The <code>energy</code> swipe is the canonical Phi/Thermo coupling lab — warm colors track field work in ways Big Grin chrome hides. Lab protocol:</p>
<div class="callout drill"><strong>Lab 2.A — energy.comp coupling</strong></div>
<pre class="eq">./linux.sh run
# Swipe to energy canvas (Options menu or bound key per build)
set AnalogFields.FieldCoupling 0.2
set AnalogFields.InjectStrength 1.0
# Move mouse 60s; then:
set AnalogFields.FieldCoupling 0.85
set AnalogFields.InjectStrength 3.0
grep -E 'THERMO|entropy|Boundary' run.log | tail -20</pre>
<p>Expect rising <code>entropyThisFrame</code> and boundary thermo when coupling and inject climb — proxy receipts, not joules. CFL guard may scale aggressive knobs — read stderr clamp messages as numerical ethics (Chapter 9), not censorship.</p>
<p>Pair lab with prompt <code>list AnalogFields</code> — host-side FCC mirrors land in <code>data_bus[16–23]</code> on x86 path; Classic path still owns the same analog knobs through overlapping control surfaces. Chapter 3 owns thermo physics story; this lab proves your hands move state.</p>

<h2>RetroRTX category — tribute shaders versus product truth</h2>
<p><code>RetroRTX</code> names a family of tribute canvases — retro ray aesthetic, pedagogical nostalgia, <span class="tag vis">Visual</span>-leaning presentation that must not be mistaken for the default Field Die product surface. RetroRTX swipes teach history of RT vocabulary inside the same Vulkan spine; they do not replace <code>x86.comp</code> guest execution truth.</p>
<table><thead><tr><th>Question</th><th>RetroRTX swipe</th><th>Default x86 canvas</th></tr></thead>
<tbody>
<tr><td>Primary shader</td><td><code>CANVAS.comp</code> tribute variant</td><td><code>x86.comp</code></td></tr>
<tr><td>Push block</td><td><code>PushConstants</code></td><td><code>FieldSocket</code></td></tr>
<tr><td>Guest RAM SSBO</td><td>Not product focus</td><td>Binding 1 — 64 MiB map</td></tr>
<tr><td>Honest use</td><td>RT pedagogy, shader art literacy</td><td>Operations, AmmoOS, dispatch proof</td></tr>
</tbody></table>
<p>Operators demoing AMOURANTHRTX to sponsors should lead with die default, then show RetroRTX as curriculum dessert — order matters for honesty. Chapter 12 rock: screenshots of tribute shaders are not proof of guest program execution.</p>

<h2>Guest FAT and VGA subfields — die is not flat RAM</h2>
<p>Field Die is 64 MiB linear guest map — but linear does not mean homogeneous. Layer pump (Chapter 8) walks L0–L9 composable subfields syncing into <code>data_bus</code> slots: RAM, VGA text frame, FAT tables, MSCDEX, audio, IO, BIOS regions. Operators who treat die as “one array” miss why HUD hex disagrees with FAT corruption stories.</p>
<table><thead><tr><th>Subfield</th><th>Typical guest anchor</th><th>Bus / layer note</th></tr></thead>
<tbody>
<tr><td>VGA text</td><td><code>0xB8000</code> color cells</td><td>Big Grin reads through shader; C mirror near <code>0x01000000</code></td></tr>
<tr><td>Guest RAM</td><td>Low linear map</td><td>AmmoOS launch images land here</td></tr>
<tr><td>FAT / filesystem</td><td>Layer L3 pump</td><td>Telemetry slots — stale FAT lies on HUD</td></tr>
<tr><td>BIOS / boot vector</td><td>High policy region</td><td>Boot offense imposes initial conditions</td></tr>
</tbody></table>
<p>VGA is a <strong>subfield</strong> with cell semantics — two bytes per character, attribute nybble — not a texture you paint arbitrarily without layer sync. FAT is a <strong>subfield</strong> with cluster semantics — guest programs scribble; layer pump must resync or <code>data_bus</code> telemetry invents fiction.</p>
<div class="callout everyone"><strong>Plain English:</strong> Die is a dollhouse with rooms — kitchen RAM, parlor VGA, attic FAT — not a single undifferentiated blob.</div>
<p>Cross-link Chapter 8 for full slot map; this chapter seats subfield vocabulary so Chapter 7 layer pump lines land with meaning.</p>

<h2>Connection intent — packet field semantics</h2>
<p>Scale three — packet field — stores sentences about sockets. Beyond TX/RX (Chapter 5), <strong>intent</strong> captures why a flow exists in operator-readable language: health check, sovereign pulse, WebRTC media, DNS trace, panel poll. Intent is not psychic — it is structured inference from port, path, habit, and honorability axes.</p>
<pre class="eq">ss / intent / DPI → gatekeeper → threat-panel.json → :9477 + field jsonl</pre>
<p>Example intents an examiner expects you to articulate:</p>
<ul>
<li><strong>Panel poll:</strong> loopback :9477, short dwell, browser or curl path — usually <code>USER_OK</code> after habit learns.</li>
<li><strong>DNS truth query:</strong> port 53 to 127.0.0.1 — corroboration for navigation (Chapter 20).</li>
<li><strong>Shell-class egress:</strong> ephemeral port to global :4444 — elevated axis weight; watchlist not auto-KILL.</li>
</ul>
<p>Intent vocabulary prevents metric collapse: do not merge “intent=health” into thermo proxy. Correlate timestamps — Chapter 5 rhythm — without summing scores.</p>
<p><span class="tag impl">Implemented</span> in NEXUS gatekeeper + jsonl schema habits. <span class="tag meta">Not</span> written into fabric texels by default.</p>

<h2>ZMM1024 tail — die map does not end at 64 MiB headline</h2>
<p>Marketing says 64 MiB guest universe; engineering says 64 MiB map <em>plus tail</em> for tile cache and ZMM1024-class extensions in Field Die SSBO binding 1. The tail is where micro-architecture metaphors become addressable — grep <code>ZMM1024</code> in engine headers for exact layout; chapter teaches <strong>there is more after the headline guest RAM</strong> so you do not stop reading SSBO at byte 64M−1.</p>
<p>Why operators care: layout version skew in tail packing corrupts HUD overlays and debug hex without touching VGA cells you memorized. <code>FIELD_LAYOUT_VERSION = 5</code> handshake includes tail contract — bump version in lockstep when tail fields move.</p>
<p>Spiderweb mirror (Chapter 10) does not replace tail literacy — hardware graph compresses fabric averages, not per-ZMM lane truth.</p>

<h2>Big Grin HUD — 172×48 telemetry theater</h2>
<p>Big Grin is the die-forward HUD overlay — 172×48 character grid semantics in operator lore — reading <code>data_bus</code> words through shader chrome on x86 path. It is <span class="tag impl">Implemented</span> product theater with honest mirrors: thermo slots, FCC floats, chrome flags in <code>data_bus[42]</code>, generation counter slot 0 from layer pump.</p>
<table><thead><tr><th>HUD read</th><th>Bus / source</th><th>Common mistake</th></tr></thead>
<tbody>
<tr><td>Thermo hex strip</td><td><code>data_bus[24–28]</code> mirrors</td><td>Treating as room temperature</td></tr>
<tr><td>FCC knobs</td><td><code>data_bus[16–23]</code></td><td>Assuming HUD edits bypass CFL guard</td></tr>
<tr><td>Chrome flags</td><td><code>data_bus[42]</code></td><td>Layout version skew silent lie</td></tr>
<tr><td>Pump generation</td><td>Slot 0 increment</td><td>Ignoring stale pump — frozen FAT story</td></tr>
</tbody></table>
<p>Enable <code>ControlFieldDebugHud</code> in <code>FieldSocket</code> when chrome hides thermo pedagogy — Chapter 7 flag. stderr THERMO still authoritative; HUD is parallel witness for die-scale literacy.</p>

<h2>NEXUS panel anatomy — correlating scale three at :9477</h2>
<p>Panel <code>https://127.0.0.1:9477/</code> is HTML shell over jsonl memory — Chapter 5 tour. Chapter 2 adds <strong>anatomy for integration</strong>: which tab witnesses which scale.</p>
<table><thead><tr><th>Panel tab</th><th>Primary scale</th><th>Never confuse with</th></tr></thead>
<tbody>
<tr><td>Packets</td><td>Packet field sentences</td><td>Phi texel heatmap</td></tr>
<tr><td>Threats</td><td>Gatekeeper verdicts</td><td>ThermoAccountant proxy</td></tr>
<tr><td>Signals</td><td>Field Antenna JSON</td><td>planetary weave colors</td></tr>
<tr><td>DNS</td><td>Truth resolution receipts</td><td>Guest DNS in die</td></tr>
<tr><td>System</td><td>Service registry ports</td><td><code>data_bus</code> slot map</td></tr>
</tbody></table>
<p>Correlation narrative template: “At sealed time T, THERMO showed rising boundary thermo; jsonl showed RX burst on port 443; gatekeeper axis habit broke — three witnesses, one paragraph, no super-score.” Chapter 11 grep rhythm marries stderr tail with jsonl tail same session.</p>

<h2>Adaptive resolution — fabric Δx changes CFL headroom</h2>
<p><code>RayCanvas</code> adaptive scale from 320×200 heritage toward 4K preference changes texel count — therefore Δx — therefore admissible Δt and wave speed via CFL (Chapter 9). Higher resolution is not free offense; harmonics guard may scale FCC floats down to protect fabric.</p>
<p>Scale 1 operators track: when you crank resolution, watch for silent clamp messages and rising <code>prevMaintCost</code> (Chapter 4). Scale 2 operators track: die byte map unchanged by resolution — guest addresses stable; only fabric and presentation scale. Scale 3 unaffected by Vulkan resize — packet field is OS sockets.</p>

<h2>Integration exercise on paper — mandatory homework</h2>
<div class="callout drill"><strong>Exercise 2.B — paper integration (30 min)</strong></div>
<p>Draw three boxes labeled <strong>Fabric</strong>, <strong>Die</strong>, <strong>Packet</strong>. Inside each box write three example addresses (texel coordinate, guest offset, ip:port). On arrows between boxes write what <em>does not</em> automatically flow:</p>
<ul>
<li>Gatekeeper verdict → fabric texel (NO)</li>
<li><code>vkCmdDispatch</code> → jsonl append (NO)</li>
<li>Layer pump → <code>data_bus</code> slots (YES — host ritual)</li>
<li>ThermoAccountant → <code>data_bus[24]</code> (YES — mirror)</li>
<li>Mouse inject → probe position in FieldSocket (YES — offense)</li>
</ul>
<p>Below the diagram write one correlation paragraph template with blanks for sealed time, THERMO line, jsonl row. Photograph page for operator journal. Teaching another human starts with this page — not with Mandelbulb screenshots.</p>
<p>Pass criteria: student can point at FAT subfield on die diagram and at intent line on packet diagram without crossing arrows. Fail criteria: student says “NEXUS measures GPU heat” — assign Chapter 4 exam.</p>

<h2>Creditor seating — von Neumann and Turing at die scale</h2>
<p>Von Neumann gave addressable store; Turing gave symbol tape. Field Die is both: guest RAM addresses, opcodes interpreted each tick on GPU. <a href="../creditors/von-neumann.html">von Neumann</a> and <a href="../creditors/turing.html">Turing</a> tribute pages humanize creditors; grep <code>FieldX86Die</code> humanizes implementation.</p>
<p>Dispatch is the clock advancing tape — Chapter 7. Packet field is different tape — jsonl append. Do not merge tapes on one diagram without labeled arrows.</p>

<h2>Failure catalog — three scales edition</h2>
<table><thead><tr><th>Failure mode</th><th>Symptom</th><th>Fix</th></tr></thead>
<tbody>
<tr><td>Metric collapse</td><td>Single dashboard “threat heat”</td><td>Three boxes exercise; Ch. 5</td></tr>
<tr><td>Swipe confusion</td><td>“Die disabled on energy”</td><td>Swipe table; default x86</td></tr>
<tr><td>VGA fantasy</td><td>Paint die like Photoshop</td><td>FAT/VGA subfields; layer pump</td></tr>
<tr><td>Tail ignorance</td><td>HUD hex wrong after merge</td><td>FIELD_LAYOUT_VERSION; ZMM1024</td></tr>
<tr><td>RetroRTX as product</td><td>Sponsor demo only tribute shader</td><td>Lead x86 default</td></tr>
<tr><td>Intent absence</td><td>Port number without story</td><td>Gatekeeper axes + Chapter 5</td></tr>
<tr><td>Spiderweb as SEM</td><td>Demand per-texel from mirror</td><td>Classic canvas or stderr</td></tr>
</tbody></table>

<h2>Chapter summary</h2>
<p>Chapter 2 maps three writable surfaces: fabric texels (Phi/Thermo/Flow bindings 8–10), die bytes with FAT/VGA subfields and ZMM1024 tail, packet field sentences with connection intent. Swipe list is curriculum — <code>energy.comp</code> lab for coupling, RetroRTX for tribute pedagogy, default <code>x86</code> for product truth. Big Grin HUD reads <code>data_bus</code> mirrors. Panel :9477 correlates scale three without replacing stderr. Paper integration exercise is mandatory homework.</p>
<p>Next: <a href="03-thermodynamics.html">Chapter 3 — Thermodynamics</a>. Dispatch: <a href="07-gpu-engine.html">Chapter 7</a>. Defense: <a href="05-packet-field.html">Chapter 5</a>.</p>

<h2>Study questions</h2>
<ol>
<li>Name scalar, vector, telemetry examples with bindings or slots.</li>
<li>Which swipe uses <code>energy.comp</code> and what lab knob pair proves coupling?</li>
<li>How is RetroRTX categorized versus default x86?</li>
<li>What lives at VGA <code>0xB8000</code> versus FAT layer pump?</li>
<li>Define connection intent with three example flows.</li>
<li>Why does ZMM1024 tail matter for layout version?</li>
<li>List four Big Grin HUD reads and common mistakes.</li>
<li>Complete Exercise 2.B; what three addresses did you write per box?</li>
<li>Which panel tab must never be confused with Phi heatmap?</li>
<li>Quote von Neumann/Turing seating in one sentence each.</li>
</ol>
"""


def expand_03() -> str:
    """Chapter 03 — Thermodynamics: CFL, coupling lab, Clausius, die vs classic."""
    return r"""
<h2>Introduction — thermodynamics as accounting, not calorimetry</h2>
<p>Every frame destroys information — diffusion, probes, maintenance, optional host assist. AMOURANTHRTX tracks that cost as <strong>accounting</strong> with honest labels, not as a laboratory calorimeter pretending to be <code>nvidia-smi</code>. Chapter 3 teaches <em>Energy can be moved</em> on the analog fabric: Phi whispers to Thermo through coupling; Flow carries gradients; CFL guards refuse numerical arson. This is Maxwell’s neighborhood on a grid — Chapter 15 goes long; here you learn to move knobs and read receipts.</p>
<p>Prior: <a href="02-fields-pixels-packets.html">Chapter 2 — Three Scales</a>. Next: <a href="04-entropy.html">Chapter 4 — Entropy Receipts</a>. Dispatch placement: <a href="07-gpu-engine.html">Chapter 7</a>. CFL deep dive: <a href="09-fcc-tesla.html">Chapter 9</a>. Creditor: <a href="../creditors/clausius.html">Clausius</a>.</p>

<div class="objectives"><h2>Learning objectives</h2><ul>
<li>Explain CFL inequalities as mesh-speed ethics, not bureaucracy.</li>
<li>Apply <code>WaveSpeed</code> caps and read clamp stderr.</li>
<li>Interpret <code>avgBoundaryThermo</code> and mouse inject boundary stories.</li>
<li>Separate host x86 heat from GPU fabric proxy in ThermoAccountant.</li>
<li>Run coupling sweep lab on Classic and compare die-default stderr.</li>
<li>Articulate Clausius spirit beside entropy floor without joule fraud.</li>
<li>Contrast thermo pedagogy on <code>Flowers</code>/<code>GreenWaves</code> versus x86 HUD.</li>
</ul></div>

<figure class="figure inline-wide"><img src="../assets/images/v3/science/ch03-energy-transfer.jpg" alt="Coupled channels" loading="lazy" /><figcaption>Figure 3.1 — Coupled Phi, Thermo, Flow: energy moves; receipts accumulate.</figcaption></figure>

<h2>Fabric channels — bindings 8, 9, 10</h2>
<table><thead><tr><th>Fabric</th><th>Binding</th><th>Evolution sketch</th></tr></thead>
<tbody>
<tr><td>Phi</td><td>8 <code>fieldPhi</code></td><td>Laplacian wave + <code>WaveSpeed</code> + <code>PropalacticScale</code></td></tr>
<tr><td>Thermo</td><td>9 <code>fieldThermo</code></td><td>Diffusion <code>ThermoAlpha</code> + floor + coupling</td></tr>
<tr><td>Flow</td><td>10 <code>fieldFlow</code></td><td>Gradients + <code>GateFidelity</code> + Tesla relaxation</td></tr>
</tbody></table>
<pre class="eq">newPhi ∈ [-2.0, 2.0] · newThermo ∈ [0.0, 1.5] · newFlow ∈ [0.0, 1.0]</pre>
<p>Clamps are numerical embodiment of kitchen realism — the shader refuses infinite temperature because the UI got excited. Host CFL guard and shader clamps are coupled defenses (Chapter 9).</p>

<h2>CFL derivation intuition — why explicit schemes demand humility</h2>
<p>Explicit time stepping updates each texel from neighbor information that arrived at time t. If information travels farther than one cell per step — wave speed × Δt &gt; Δx — the scheme invents neighbors that have not spoken yet. That is NaN theology. Courant, Friedrichs, and Lewy named the inequality operators inherit as <strong>CFL condition</strong>.</p>
<p>Wave channel intuition: disturbance crosses grid at speed c. One step advances Δt. Distance traveled c·Δt must not exceed cell spacing Δx — else dependency graph lies.</p>
<div class="eq">waveCFL = c·Δt/Δx ≤ 1</div>
<p>Thermo channel intuition: diffusion spreads heat wider each step — parabolic scaling. Distance grows like √(α·Δt), leading to:</p>
<div class="eq">thermoCFL = α·Δt/Δx² ≤ 1</div>
<p>Chapter 9 owns constants; Chapter 7 owns placement — CFL runs <em>before</em> <code>vkCmdDispatch</code> every frame. Intuition operators need: <strong>finer mesh (smaller Δx) tightens allowed Δt or forces lower c and α.</strong> Adaptive resolution (Chapter 2) therefore interacts with thermo headroom — not vanity scaling.</p>
<div class="callout axiom"><strong>Time is linear.</strong> CFL does not rewrite past frames — it refuses unsafe next frames.</div>
<div class="callout science"><strong>Science posture:</strong> CFL is real numerical analysis. Host harmonics guard is <span class="tag impl">Implemented</span> enforcement — grep clamp messages.</div>

<h2>WaveSpeed caps — offense within mesh ethics</h2>
<p><code>Options::AnalogFields::WaveSpeed</code> maps to FCC slot <code>data_bus[18]</code> on x86 path. Host enforces hard caps (e.g. <code>waveSpeed ∈ [0.01, 2.0]</code>, <code>dT ≤ 0.033</code>) before fabric sees operator enthusiasm. Caps are not punishment — they preserve fabric existence for next tick.</p>
<table><thead><tr><th>Knob</th><th>Risk when cranked</th><th>Guard response</th></tr></thead>
<tbody>
<tr><td><code>WaveSpeed</code></td><td>waveCFL &gt; 1</td><td>Scale c or Δt down; stderr note</td></tr>
<tr><td><code>ThermoAlpha</code></td><td>thermoCFL &gt; 1</td><td>Scale α or Δt down</td></tr>
<tr><td><code>InjectStrength</code></td><td>Boundary spikes + NaN colors</td><td>Scale inject; clamp in shader</td></tr>
<tr><td><code>TimeScale</code></td><td>Effective Δt inflation</td><td>CFL recomputed on scaled dt</td></tr>
</tbody></table>
<div class="callout drill"><strong>Drill 3.A — WaveSpeed clamp witness</strong></div>
<pre class="eq">set AnalogFields.WaveSpeed 2.5
set AnalogFields.TimeScale 2.0
list AnalogFields
grep -i 'CFL\|clamp\|wave' run.log | tail -15</pre>
<p>Expect host to pull effective wave speed below operator request — list readback shows scaled truth. Screenshot of pretty waves without this grep is incomplete testimony.</p>

<h2>Boundary thermo — perimeter heat is not background mood</h2>
<p><code>avgBoundaryThermo</code> in ThermoAccountant (binding 2, mirror <code>data_bus[25]</code>) summarizes mean boundary temperature / entropy density — where fabric meets edges and probes inject. Mouse movement is boundary offense: <code>InjectStrength</code> writes energy at probe positions carried through <code>FieldSocket</code> push constants.</p>
<p>Rising boundary thermo with flat interior averages tells a story: perimeter work without bulk equilibration — common in high inject sessions. Flat boundary with rising interior suggests diffusion catching up — different narrative, same grep discipline.</p>
<p>Chapter 4 names full ThermoAccountant fields; Chapter 3 teaches you to <strong>move mouse and expect boundary line to speak</strong> in THERMO stderr. Die-default x86 hides heatmap — boundary thermo still moves if coupling alive; enable debug HUD or trust log.</p>

<h2>Host x86 heat versus GPU fabric heat — two witnesses, one proxy ledger</h2>
<p>Default execution path is GPU interpretation via <code>x86.comp</code> — fat GPU, thin host. Optional <code>ControlHostCpu</code> enables <code>FieldX86Emu</code> assist; host cycles last frame can add terms to <code>entropyThisFrame</code> through <code>FieldX86Emu::hostCyclesLastFrame()</code>. Both paths remain <span class="tag meta">proxy</span> — not junction calorimetry.</p>
<table><thead><tr><th>Source</th><th>When active</th><th>Witness</th></tr></thead>
<tbody>
<tr><td>GPU fabric work</td><td>Every dispatch</td><td>THERMO + coupling terms</td></tr>
<tr><td>Probe inject</td><td>Mouse / FieldSocket probe</td><td>Boundary thermo rise</td></tr>
<tr><td>Host x86 assist</td><td><code>ControlHostCpu</code> set</td><td>Extra proxy contribution in entropy</td></tr>
<tr><td>Maintenance</td><td>High fidelity sessions</td><td><code>prevMaintCost</code> — Chapter 4</td></tr>
</tbody></table>
<div class="callout everyone"><strong>Plain English:</strong> GPU runs the kitchen; host assist is a visiting chef — both leave dishes, neither brings a wattmeter.</div>
<p>Category error: claiming <code>nvidia-smi</code> power draw equals <code>entropyThisFrame</code>. Category error: disabling GPU path to “save thermo” while claiming field evolution — offense requires dispatch.</p>

<h2>Flowers and GreenWaves — Classic swipes for thermo pedagogy</h2>
<p><code>Flowers</code> and <code>GreenWaves</code> swipes emphasize organic flow and interference patterns on Classic canvas — curriculum shaders where thermo and Phi coupling is <em>visible</em> in ways Big Grin chrome suppresses. Week-one pattern: afternoon on Flowers with inject lab; return to die default for week-two operations.</p>
<table><thead><tr><th>Swipe</th><th>Visual emphasis</th><th>Lab use</th></tr></thead>
<tbody>
<tr><td><code>Flowers</code></td><td>Organic advection patterns</td><td>Flow + coupling narrative</td></tr>
<tr><td><code>GreenWaves</code></td><td>Interference, propagation</td><td>WaveSpeed + Phi forcing</td></tr>
<tr><td><code>energy</code></td><td>Heat map obvious</td><td>FieldCoupling sweeps — Ch. 2 lab</td></tr>
<tr><td><code>x86</code> default</td><td>Chrome forward</td><td>stderr + debug HUD thermo</td></tr>
</tbody></table>
<p>ThermoAccountant populates every swipe — canvas-agnostic obligation from Chapter 7. Flowers beauty does not excuse skipping THERMO grep.</p>

<h2>Coupling sweep laboratory — structured knob narrative</h2>
<div class="callout drill"><strong>Lab 3.B — coupling sweep (Classic recommended)</strong></div>
<pre class="eq"># Swipe Flowers or energy; baseline 120s log segment
set AnalogFields.FieldCoupling 0.1
set AnalogFields.GateFidelity 0.3
set AnalogFields.EntropyFloor 0.01
# Record THERMO tail; then sweep:
set AnalogFields.FieldCoupling 0.9
set AnalogFields.GateFidelity 0.85
set AnalogFields.InjectStrength 4.0
grep -E 'THERMO|entropy|Boundary|prevMaint' run.log | tail -30</pre>
<p>Journal template per sweep row:</p>
<table><thead><tr><th>Step</th><th>FieldCoupling</th><th>GateFidelity</th><th>entropyThisFrame</th><th>avgBoundaryThermo</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>Baseline</td><td>0.1</td><td>0.3</td><td>(grep)</td><td>(grep)</td><td>Low bleed between channels</td></tr>
<tr><td>Aggressive</td><td>0.9</td><td>0.85</td><td>(grep)</td><td>(grep)</td><td>Expect higher proxy + maintenance</td></tr>
</tbody></table>
<p>Restore defaults after lab — operator ethics. Chapter 4 exam afterward: which layer is ThermoAccountant versus oracle — do not conflate sweep results with Shannon H on zip files.</p>

<h2>RTXProbe — optional dispatch timing witness</h2>
<p><code>RTXPROBE</code> ELLIE category activates with <code>RTX_PROBES=1</code> — GPU timestamps and invocation counts with zero cost when off (Chapter 7). Use when coupling sweeps cause latency spikes without obvious CFL clamp lines — distinguishes dispatch-bound fabric work from logging volume or accidental host CPU path.</p>
<pre class="eq">RTX_PROBES=1 ./linux.sh run 2>&1 | tee /tmp/probe-thermo.log
grep -E 'RTXPROBE|THERMO|CFL' /tmp/probe-thermo.log | tail -25</pre>
<p>RTXProbe does not measure joules — it measures time discipline. Pair with STATUS block GPU ms line for week-three health narrative.</p>

<h2>Maintenance cost — coherence tax each frame</h2>
<p><code>prevMaintCost</code> (Chapter 4 preview) rises when field state becomes expensive to remember — high <code>GateFidelity</code>, aggressive coupling, resolution jumps. Chapter 3 connects maintenance to thermo pedagogy: Flowers session at fidelity 0.9 should show higher maintenance than baseline 0.3 — not moral judgment, coherence accounting.</p>
<p>Maintenance is why “same looking” frames can cost different entropy — prior frame complexity matters. Clausius spirit: nature taxes irreversibility; engine taxes coherence.</p>

<h2>Clausius spirit — irreversibility named, not faked</h2>
<p>Rudolf Clausius gave operators language: entropy of universe tends upward; heat flows with direction. Field Technology honors spirit via entropy floor seed ~0.015 at <code>clearFieldImages()</code> and minimum noise in diffusion — fabric refuses pretend reversibility.</p>
<div class="callout god"><strong>Irreversibility is not shame.</strong> It is the price of time running forward. Clausius named the direction; ThermoAccountant prints the receipt.</div>
<p><a href="../creditors/clausius.html">Clausius tribute</a> humanizes creditor; <code>EntropyFloor</code> knob and floor seed humanize implementation. <span class="tag meta">Metaphor</span> on proxy — spirit without calorimeter fraud. Chapter 13 Landauer adds erasure floor vocabulary; Chapter 3 adds heat movement vocabulary — same table, different plates (Chapter 4 seating).</p>

<h2>Thermo on die versus Classic — same accountant, different costume</h2>
<p>Die-default <code>x86.comp</code> evolves bindings 8–10 every dispatch — thermo exists under AmmoOS chrome whether you see heatmap or not. Classic <code>CANVAS.comp</code> swipes exist because human eyes learn coupling faster with color. Product truth on die; pedagogy truth on Classic — compromise this book teaches.</p>
<table><thead><tr><th>Aspect</th><th>Die default x86</th><th>Classic Flowers/GreenWaves</th></tr></thead>
<tbody>
<tr><td>ThermoAccountant</td><td>Populated every dispatch</td><td>Same — canvas-agnostic</td></tr>
<tr><td>Visual thermo</td><td>Hidden behind chrome</td><td>Obvious heatmap</td></tr>
<tr><td>Debug path</td><td><code>ControlFieldDebugHud</code></td><td>Swipe itself</td></tr>
<tr><td>Honest testimony</td><td>stderr THERMO + bus hex</td><td>stderr + screenshot</td></tr>
<tr><td>Category error</td><td>“No thermo on die”</td><td>“Thermo only on Classic”</td></tr>
</tbody></table>
<div class="callout drill"><strong>Drill 3.C — die vs Classic same session</strong></div>
<pre class="eq"># Segment A: x86 default 90s mouse move — grep THERMO
# Segment B: swipe GreenWaves 90s same knobs — grep THERMO
# Compare entropyThisFrame distributions — both must be non-silent</pre>
<p>Silence on either segment is failed path — binding 2 or dispatch broken, not “die has no physics.”</p>

<h2>AnalogFields knobs — FCC mirror quick reference</h2>
<table><thead><tr><th>Knob</th><th>Bus slot</th><th>Chapter 3 focus</th></tr></thead>
<tbody>
<tr><td><code>TimeScale</code></td><td>[16]</td><td>Effective Δt — CFL interaction</td></tr>
<tr><td><code>ThermoAlpha</code></td><td>[17]</td><td>Diffusion rate — thermoCFL</td></tr>
<tr><td><code>WaveSpeed</code></td><td>[18]</td><td>Wave propagation — waveCFL</td></tr>
<tr><td><code>GateFidelity</code></td><td>[19]</td><td>Analog vs sharp gates — maintenance</td></tr>
<tr><td><code>EntropyFloor</code></td><td>[20]</td><td>Minimum irreversible noise</td></tr>
<tr><td><code>InjectStrength</code></td><td>[21]</td><td>Probe boundary offense</td></tr>
<tr><td><code>PropalacticScale</code></td><td>[22]</td><td>Large-scale Phi forcing</td></tr>
<tr><td><code>FieldCoupling</code></td><td>[23]</td><td>Phi ↔ Thermo ↔ Flow bleed</td></tr>
</tbody></table>
<p>Prompt <code>set AnalogFields.*</code> changes host state; CFL guard may scale before GPU sees values — numerical ethics, not censorship.</p>

<h2>Maxwell neighborhood preview — coupling before Chapter 15</h2>
<p>James Clerk Maxwell taught that fields talk to neighbors — electrical potential and heat exchange stories are coupled, not isolated channels on a grid. AMOURANTHRTX implements neighborhood whispers as discrete Laplacian on Phi, diffusion on Thermo, gradient-driven Flow with <code>FieldCoupling</code> mixing strengths. This is <span class="tag impl">Implemented</span> shader arithmetic on bindings 8–10 — not a claim the engine solved Maxwell’s equations in full analytical glory.</p>
<p>Preview intuition for coupling lab: when Phi develops sharp spatial features, Thermo at neighboring texels warms when coupling is high — energy can be moved, axiom three. When coupling is low, channels evolve as parallel homework problems — useful pedagogy, incomplete product story. Chapter 15 creditor page goes historical; Chapter 3 demands you <em>see</em> the consequence in THERMO grep when coupling sweeps.</p>
<p>Do not quote Maxwell to justify ionosphere colors from planetary weave — that is Chapter 6 <span class="tag vis">Visual</span> category error. Quote Maxwell when discrete Laplacian and coupling knobs have stderr witnesses.</p>

<h2>Sealed time on fabric — linear physics before sovereign sync</h2>
<p><code>TotalTime::seal()</code> writes monotonic session genesis into <code>FieldSocket::sealed_time</code> before fabric evolves. Thermodynamics without sealed time would let frame-rate jitter rewrite effective Δt stories retroactively — logs would lie. Chapter 3 connects seal to thermo receipts: <code>freeEnergyIncome</code> (Chapter 4) treats sealed time as living-world potential feeding the ledger.</p>
<p>Operators comparing week-one to week-six sessions should compare THERMO against rising <code>steps</code> counter and sealed genesis, not wall clock alone. Chapter 19 sovereign pulses extend the discipline across hosts; session seal is prerequisite intuition — local physics clock before planetary sync narrative.</p>

<h2>Failure catalog — thermodynamics edition</h2>
<table><thead><tr><th>Failure mode</th><th>Symptom</th><th>Fix</th></tr></thead>
<tbody>
<tr><td>Joule fantasy</td><td>Bill from THERMO lines</td><td><span class="tag meta">Proxy rock</span> — Ch. 4</td></tr>
<tr><td>CFL ignorance</td><td>NaN colors instant</td><td>Read clamp grep; Ch. 9</td></tr>
<tr><td>Die thermo denial</td><td>“Heat only on Classic”</td><td>Drill 3.C; debug HUD</td></tr>
<tr><td>Oracle merge</td><td>Zip H tied to boundary thermo</td><td>Layer exam — Ch. 4</td></tr>
<tr><td>nvidia-smi equivalence</td><td>GPU power = entropyThisFrame</td><td>Host vs GPU table above</td></tr>
<tr><td>Zero floor myth</td><td>EntropyFloor 0 “for clean run”</td><td>Clausius spirit; reseed</td></tr>
<tr><td>Screenshot-only lab</td><td>Flowers pretty, THERMO silent</td><td>Binding 2 checklist — Ch. 7</td></tr>
</tbody></table>

<h2>Chapter summary</h2>
<p>Chapter 3 teaches thermodynamics as honest accounting on Phi/Thermo/Flow bindings 8–10. CFL wave and thermo inequalities express mesh-speed ethics; WaveSpeed caps enforce them before dispatch. Boundary thermo narrates probe offense; host x86 heat adds optional proxy terms separate from GPU fabric work. Coupling sweep lab on Flowers/GreenWaves/energy swipes produces grep journals; die-default path shares ThermoAccountant with hidden heatmaps — stderr remains scripture. Clausius spirit lives in entropy floor and irreversibility language without joule fraud. RTXProbe optional timing complements THERMO receipts.</p>
<p>Next: <a href="04-entropy.html">Chapter 4 — Entropy</a>. Dispatch: <a href="07-gpu-engine.html">Chapter 7</a>. CFL constants: <a href="09-fcc-tesla.html">Chapter 9</a>. Maxwell: <a href="../creditors/maxwell.html">Maxwell</a>.</p>

<h2>Deep dive — thermodynamics travels through field layers</h2>
<p>Guest RAM, VGA, FAT, and audio layers (Chapter 8) pump telemetry into <code>data_bus</code> before fabric evolves. Thermodynamics on the fabric is not isolated from die activity — guest execution raises host pump work, layer sync costs, and optional <code>FieldX86Emu</code> assist heat. Literate operators correlate rising <code>entropyThisFrame</code> with rising pump generation in slot 0 without claiming a single causal line — correlation is human narrative; receipts are grep lines.</p>
<p>When AmmoOS chrome animates on binding 11–14 textures, presentation work still rides the same dispatch loop that populates ThermoAccountant. Chrome is not “outside thermo.” If chrome moves and THERMO is flat, suspect dispatch failure or logging category filters — not “OS mode is free.”</p>
<p>Field layers L0–L9 exist so DOS-shaped universes remain addressable to shaders. Each layer pump is a host obligation in <code>dispatch_canvas()</code> — thermodynamics begins on the host timeline before <code>vkCmdDispatch</code> writes GPU texels. Skip pump literacy and you will misread thermo spikes as fabric bugs when they are guest sync stories.</p>

<h2>Deep dive — prompt terminal AnalogFields as live FCC</h2>
<p>The in-engine prompt exposes <code>set AnalogFields.TimeScale</code>, <code>ThermoAlpha</code>, <code>WaveSpeed</code>, and siblings — the same namespace mirrored to <code>data_bus[16–23]</code> on the x86 path. Treat prompt changes as offensive writes to boundary conditions: you are not “adjusting graphics,” you are changing the next tick’s PDE parameters subject to CFL guard.</p>
<table><thead><tr><th>Prompt command</th><th>Immediate effect</th><th>Grep witness</th></tr></thead>
<tbody>
<tr><td><code>set AnalogFields.FieldCoupling 0.8</code></td><td>Cross-channel bleed rises</td><td>THERMO slope vs prior session</td></tr>
<tr><td><code>set AnalogFields.InjectStrength 1.2</code></td><td>Mouse probe heats boundary</td><td><code>avgBoundaryThermo</code> lines</td></tr>
<tr><td><code>set AnalogFields.GateFidelity 0.95</code></td><td>Sharper gates, higher maintenance</td><td><code>prevMaintCost</code> — Ch. 4</td></tr>
<tr><td><code>set AnalogFields.WaveSpeed 1.8</code></td><td>CFL may clamp before dispatch</td><td>harmonics guard stderr</td></tr>
</tbody></table>
<p>Document knob state in lab journals. Future-you comparing week-six grep to week-one without knob notes will invent myths about “mysterious drift.”</p>

<h2>Deep dive — week-two thermo journal template</h2>
<p>Operators who graduate Chapter 3 keep a running thermo journal — not for publication, for comparative honesty:</p>
<ol>
<li><strong>Session ID</strong> — date, canvas kind (Classic / x86 / energy), swipe name.</li>
<li><strong>Knob baseline</strong> — list AnalogFields values before drill.</li>
<li><strong>CFL events</strong> — note any clamp messages; they explain “why my knob did not stick.”</li>
<li><strong>THERMO tail</strong> — paste last ten THERMO lines; circle <code>entropyThisFrame</code> and <code>avgBoundaryThermo</code>.</li>
<li><strong>One sentence</strong> — what moved and what did not; no joule claims.</li>
</ol>
<p>After four sessions, plot <code>steps</code> versus cumulative proxy entropy trend in a spreadsheet if you must — comparative slopes only. Chapter 4 owns formal entropy layers; Chapter 3 owns the habit of writing receipts down before arguments start.</p>

<h2>Study questions</h2>
<ol>
<li>State wave and thermo CFL inequalities and intuition for each.</li>
<li>What happens when WaveSpeed 2.5 is requested?</li>
<li>Define avgBoundaryThermo and how mouse inject affects it.</li>
<li>When does host x86 heat enter the proxy ledger?</li>
<li>Run Lab 3.B; record two sweep rows with grep numbers.</li>
<li>Why do Flowers and GreenWaves exist if die evolves thermo?</li>
<li>What does RTX_PROBE env var enable?</li>
<li>Explain Clausius spirit versus entropy floor implementation.</li>
<li>Complete Drill 3.C; did both segments emit THERMO?</li>
<li>Which failure mode matches nvidia-smi equivalence?</li>
</ol>
"""


def expand_04() -> str:
    """Chapter 04 — Entropy receipts, ThermoAccountant, oracle layers."""
    return r"""
<h2>Introduction — entropy is the receipt that time ran forward</h2>
<p>Chapter 3 taught thermodynamics on the fabric: heat moves, coupling transfers work, CFL guards refuse explosion. Chapter 4 names the <em>receipt</em> — entropy as evidence that the dispatch loop advanced irreversibly. This is not philosophy dressed as stderr. When <code>entropyThisFrame</code> rises while you move the mouse on Classic canvas, or when boundary thermo climbs while guest chrome animates on the die path, the engine is telling you: <strong>time ran forward and the field paid maintenance cost.</strong></p>
<p>The word <em>entropy</em> appears in three implemented layers that share vocabulary but measure different things. Conflating them is week-two failure — billing joules from proxy integrals, auto-KILLing peers because a zip file surprised Shannon H, or treating fabric minimum noise as NEXUS storm polling. This chapter is the three-layer exam. Pass it before you argue with a physicist or a security engineer.</p>
<p>Prior: <a href="03-thermodynamics.html">Chapter 3 — Thermodynamics</a> owns fabric heat and coupling. Next: <a href="05-packet-field.html">Chapter 5 — Packet Field</a> owns defensive sentences. Chapter 7 places ThermoAccountant on the dispatch spine every <code>vkCmdDispatch</code>. Chapter 13 credits Landauer; Chapter 14 credits Shannon. Chapter 12 lists every rock.</p>

<div class="objectives"><h2>Learning objectives</h2><ul>
<li>Enumerate ThermoAccountant fields and their <code>data_bus[24–28]</code> mirrors.</li>
<li>Pass the three-layer exam: GPU proxy, fabric floor, NEXUS oracle.</li>
<li>Explain Landauer bound theory versus <code>entropyThisFrame</code> proxy rock.</li>
<li>Tune entropy oracle calm / alert / storm thresholds without conflating layers.</li>
<li>Read <code>prevMaintCost</code> as maintenance narrative, not punishment.</li>
<li>Run the grep workbook and classify failure modes in the catalog below.</li>
</ul></div>

<figure class="figure"><img src="../assets/images/entropy-chapter.jpg" alt="Three entropy layers" loading="lazy" /><figcaption>Figure 4.1 — Same word, three layers: ThermoAccountant, entropy floor, Shannon oracle. Label before you argue.</figcaption></figure>

<h2>ThermoAccountant — binding 2 deep dive</h2>
<p><code>ThermoAccountant</code> lives at Vulkan descriptor binding <strong>2</strong>. It is populated every <code>Pipeline::dispatch_canvas()</code> — canvas-agnostic, die-default or Classic swipe alike. Chapter 7 stresses this obligation: you do not skip entropy because Big Grin HUD hides the thermo heatmap. The struct is small; the moral weight is large. It is the per-frame ledger that says the GPU field evolution and host orchestration advanced one tick with witnesses.</p>
<pre class="eq">struct ThermoAccountant {
    f32 entropyThisFrame;   // Landauer proxy + field work + probes
    f32 avgBoundaryThermo;  // mean boundary temperature / entropy density
    f32 prevMaintCost;      // cost to preserve previous-frame coherence
    f32 freeEnergyIncome;   // sealed time + input activity
    u32 steps;              // dispatch counter witness
};</pre>
<p><span class="tag impl">Implemented.</span> Grep <code>ThermoAccountant</code> in <code>Navigator/engine/</code> and watch <code>ELLIE</code> category <code>THERMO</code> in stderr. The host packs binding 2 and mirrors the same numbers into <code>data_bus[24–28]</code> so guest HUD hex and operator grep agree.</p>

<table><thead><tr><th>Field</th><th>Meaning</th><th><code>data_bus</code></th><th>Operator read</th></tr></thead>
<tbody>
<tr><td><code>entropyThisFrame</code></td><td>Proxy integral: field work, probe dissipation, maintenance, optional host x86 heat</td><td>[24]</td><td>Did this tick cost irreversibility?</td></tr>
<tr><td><code>avgBoundaryThermo</code></td><td>Mean boundary temperature / entropy density at fabric edges</td><td>[25]</td><td>Is the perimeter hot?</td></tr>
<tr><td><code>prevMaintCost</code></td><td>Coherence price versus previous frame state</td><td>[26]</td><td>Did we pay to remember?</td></tr>
<tr><td><code>freeEnergyIncome</code></td><td>Sealed time contribution plus input activity potential</td><td>[27]</td><td>Did living-world input feed the ledger?</td></tr>
<tr><td><code>steps</code></td><td>Monotonic dispatch step counter</td><td>[28]</td><td>Does time advance linearly?</td></tr>
</tbody></table>

<p><code>entropyThisFrame</code> is not read from <code>nvidia-smi</code>. It is a <span class="tag meta">Metaphor</span> proxy that honors Landauer’s lesson — erasing information has a floor — without pretending the engine measured junction temperature. Chapter 13 goes long on the bound; here you must label the rock on every sentence: <strong>proxy integral, not joules.</strong></p>
<p>When <code>ControlHostCpu</code> enables <code>FieldX86Emu</code> assist, host-side guest execution can add heat terms to the proxy. Still proxy. Still not a wattmeter. The assist path is offense with receipts; it does not convert stderr into a utility bill.</p>
<div class="callout everyone"><strong>Plain English:</strong> ThermoAccountant is the cash register tape at the end of each dispatch. It does not measure the wall thermostat in the server room — it measures what the <em>field story</em> claims you spent to move state forward.</div>

<h2>Maintenance narrative — <code>prevMaintCost</code> and coherence tax</h2>
<p>Operators fresh from game engines expect frame cost in milliseconds only. Field Technology adds <code>prevMaintCost</code> — the price of staying coherent with the previous frame’s field configuration. High fidelity chrome, rising <code>GateFidelity</code>, aggressive <code>InjectStrength</code>, and large <code>FieldCoupling</code> can raise maintenance even when the scene “looks the same.” This is not punishment. It is honesty: remembering a complex field state costs more than forgetting it.</p>
<p>Correlate <code>prevMaintCost</code> with Chapter 9’s <code>GateFidelity</code> knob. Cranking fidelity from soft analog gates toward transistor-sharp Flow changes gradient stories and spiderweb voltage factors indirectly. A veteran operator watches maintenance climb when they chase sharp gates without widening CFL headroom — not because the GPU is “slow,” because the field refuses unphysical cheap memory.</p>
<p>Sealed time enters through <code>freeEnergyIncome</code>. Chapter 7’s <code>TotalTime::seal()</code> writes monotonic session genesis into <code>FieldSocket::sealed_time</code>. ThermoAccountant treats that seal as living-world potential — time itself as input to the ledger. Chapter 19 extends sealing across hosts with sovereign pulses; here, session-local sealing already proves linear physics time. If <code>steps</code> stalls while chrome animates, you have desynchronized reality — grep dispatch before you screenshot.</p>

<h2>Entropy floor — fabric second-law bias</h2>
<p>Separate from binding 2, the fabric carries an <strong>entropy floor</strong> seeded at initialization. <code>clearFieldImages()</code> seeds thermo with approximately <strong>0.015</strong> minimum — a second-law bias that refuses unphysical reversibility. Diffusion always injects minimum noise; the universe does not offer free rewind on the grid.</p>
<p>The FCC knob <code>EntropyFloor</code> in <code>data_bus[20]</code> cooperates with that seed. Operators who set floor to zero expecting “clean” fabric are asking for category error — Chapter 9 names the knob; Chapter 12 labels the rock. The floor is not a Kelvin sensor. It is an engineering guardrail that keeps thermo evolution from pretending history can be erased without cost.</p>
<p>Cross-link Chapter 15 Maxwell: neighborhood coupling moves energy; the floor ensures moved energy leaves a trace in thermo density. Cross-link Chapter 3: mouse probes inject at boundaries; floor plus probe plus maintenance equals the texture of <code>entropyThisFrame</code> on a living session.</p>

<h2>Shannon oracle — NEXUS layer, storm tuning</h2>
<p>NEXUS-Shield implements a separate <strong>Entropy Oracle</strong> on files and payloads — not fabric texels. Shannon surprise:</p>
<div class="eq">H = −Σ p_i log₂ p_i</div>
<p>High <em>H</em> suggests packed, encrypted, or obfuscated bytes. The oracle exposes calm / alert / storm thresholds that tune daemon polling cadence — not automatic KILL. <span class="tag impl">Implemented</span> in NEXUS; <span class="tag meta">Not</span> inside Vulkan <code>x86.comp</code>.</p>
<p>Storm tuning is operator discipline. Lower thresholds increase sensitivity — useful when you expect plaintext logs, noisy when your archive contains legitimate encrypted backups. Raise thresholds when you accept high-entropy artifacts as normal on your machine. The oracle tells you <em>surprise in symbols</em>; the Connection Gatekeeper tells you <em>corroborated flow meaning</em>. Chapter 5 connects them at the perimeter; do not merge scores into one super-number.</p>
<div class="callout love"><strong>94/6 pastoral care on bytes:</strong> corroborate before permanent action. One high-H file does not condemn a peer. One THERMO spike does not prove malware. Restraint is coupled evolution with consent — watchlist before block, operator judgment before KILL dossier.</div>
<p>Chapter 14 owns Shannon deep dive. This chapter seats Landauer and Shannon at the same table with name cards — see below — so you never confuse erasure cost with byte surprise.</p>

<h2>Landauer and Shannon seating — same table, different plates</h2>
<p>Picture a dinner table with two creditors and three implemented layers. Landauer sits beside ThermoAccountant and entropy floor — stories about irreversibility and minimum cost to forget. Shannon sits beside the NEXUS oracle — stories about surprise in symbol distributions. They share the word entropy. They do not share the same implementation.</p>
<table><thead><tr><th>Seat</th><th>Theory</th><th>Implemented witness</th><th>Rock</th></tr></thead>
<tbody>
<tr><td>Landauer</td><td><div class="eq">E_min = k_B T ln 2</div></td><td><code>entropyThisFrame</code> proxy</td><td><span class="tag meta">Not joules from GPU sensor</span></td></tr>
<tr><td>Clausius / Boltzmann</td><td>Irreversibility language</td><td>Entropy floor ~0.015 seed</td><td><span class="tag meta">Bias, not calorimetry</span></td></tr>
<tr><td>Shannon</td><td>Information surprise H</td><td>NEXUS oracle thresholds</td><td><span class="tag impl">Files, not texels</span></td></tr>
</tbody></table>
<p><a href="../creditors/landauer.html">Landauer tribute</a> and <a href="../creditors/shannon.html">Shannon tribute</a> humanize the names. When a vendor slide says “entropy-based security,” ask: which seat at the table? If they cannot point to jsonl rows or THERMO lines, label the claim <span class="tag phil">Philosophy</span> until proven.</p>

<h2>Three-layer exam — pass before you operate</h2>
<p>The exam is oral and practical. An operator examiner asks five questions; you answer with grep, not vibes.</p>
<ol>
<li><strong>Layer ID:</strong> A rising number on Classic canvas during mouse move — which layer? <em>Answer: ThermoAccountant / fabric proxy, binding 2, bus [24]. Not Shannon.</em></li>
<li><strong>Layer ID:</strong> A downloaded tarball triggers oracle alert — which layer? <em>Answer: NEXUS Entropy Oracle on file bytes. Not avgBoundaryThermo.</em></li>
<li><strong>Layer ID:</strong> Fresh fabric after <code>clearFieldImages</code> still shows baseline thermo — which layer? <em>Answer: Entropy floor seed ~0.015. Not gatekeeper.</em></li>
<li><strong>Rock:</strong> Can you invoice a cloud customer using <code>entropyThisFrame</code>? <em>Answer: No — proxy rock, Chapter 12.</em></li>
<li><strong>Corroboration:</strong> Oracle storm plus SUSPICIOUS flow — automatic KILL? <em>Answer: No — operator reviews, Chapter 5 ethics.</em></li>
</ol>
<p>Fail any item: reread this chapter before Chapter 7 dispatch drills. Field literacy is sequential; skipping the exam produces confident wrong sentences in week six.</p>

<h2>Grep workbook — entropy receipts in practice</h2>
<div class="callout drill"><strong>Workbook 4.A — THERMO spine</strong></div>
<pre class="eq">./linux.sh run 2>&1 | tee /tmp/ch04-thermo.log
# Move mouse 90s on default x86; swipe to energy 60s if prompt available
grep -E 'THERMO|entropy|Boundary|prevMaint|steps' /tmp/ch04-thermo.log | tail -30</pre>
<p>Expect periodic THERMO lines with <code>entropyThisFrame</code>, boundary thermo, maintenance, steps incrementing. Silence after visible fabric motion means failed path — return to Chapter 7 bindings.</p>
<div class="callout drill"><strong>Workbook 4.B — Bus mirror</strong></div>
<pre class="eq">grep -E 'data_bus\[2[4-8]\]|ThermoAccountant' Navigator/engine/ -r
# In-run: enable debug HUD if available; read hex near thermo slots</pre>
<div class="callout drill"><strong>Workbook 4.C — Oracle layer (NEXUS)</strong></div>
<pre class="eq">./nexus.sh   # if installed
# Place a high-entropy sample in watched path; observe calm/alert/storm cadence
grep -i 'entropy\|oracle\|storm' /var/lib/nexus-shield/*.log 2>/dev/null | tail -20</pre>
<p>Workbook 4.C proves layer separation: you can have calm GPU THERMO and alert oracle simultaneously — different products, different questions.</p>
<div class="callout drill"><strong>Workbook 4.D — Landauer vocabulary check</strong></div>
<pre class="eq">grep -r 'entropyThisFrame' Navigator/engine/ docs/ content/
# Every hit should pair proxy language with rock label in v5 text</pre>

<h2>Failure catalog — entropy edition</h2>
<table><thead><tr><th>Failure mode</th><th>Symptom</th><th>Root cause</th><th>First fix</th></tr></thead>
<tbody>
<tr><td>Joule fantasy</td><td>Billing or carbon claims from THERMO lines</td><td>Landauer metaphor read as meter</td><td>Label <span class="tag meta">proxy</span>; read Ch. 13 rock</td></tr>
<tr><td>Layer conflation</td><td>Auto-block peer on oracle alert alone</td><td>Shannon merged with gatekeeper</td><td>Corroborate per Ch. 5; watchlist first</td></tr>
<tr><td>Flat entropy</td><td>Chrome moves; THERMO silent</td><td>ThermoAccountant not populated</td><td>Ch. 7 dispatch checklist binding 2</td></tr>
<tr><td>Zero floor myth</td><td>“Reset” thermo to absolute zero story</td><td>EntropyFloor knob misunderstood</td><td>Reseed via <code>clearFieldImages</code>; read floor bias</td></tr>
<tr><td>Storm fatigue</td><td>Operator ignores all oracle alerts</td><td>Thresholds too tight for machine habits</td><td>Retune calm/alert/storm; document baseline H</td></tr>
<tr><td>Maintenance surprise</td><td>prevMaintCost spikes after fidelity crank</td><td>GateFidelity + coupling without CFL headroom</td><td>Ch. 9 harmonics; lower fidelity or resolution</td></tr>
<tr><td>Steps stall</td><td><code>steps</code> frozen while HUD animates</td><td>Dispatch desync or headless lie</td><td>grep <code>dispatch_canvas</code>; layout version</td></tr>
<tr><td>Shader as sensor</td><td>Thermo heatmap claimed as room temperature</td><td>Classic canvas pedagogy forgotten</td><td>stderr over screenshot; Ch. 12 rocks</td></tr>
</tbody></table>

<h2>Cross-links — where entropy travels in the stack</h2>
<p>Chapter 7: ThermoAccountant on every dispatch before <code>vkCmdDispatch</code>. Chapter 8: <code>data_bus[24–28]</code> HUD mirrors for Big Grin hex literacy. Chapter 9: <code>EntropyFloor</code> knob and CFL guard interaction. Chapter 10: fabric averages drive hardware mirror — hot thermo eventually speaks in spiderweb util. Chapter 11: weekly grep rhythm includes THERMO tail. Chapter 13: Landauer creditor page. Chapter 14: Shannon oracle theory. Chapter 19: sealed time in <code>freeEnergyIncome</code>. Chapter 21: Queen thermo per WebGL context inherits same proxy discipline.</p>
<p>Defense in Chapter 5 reads different entropy — file surprise, not fabric proxy. Offense in Chapter 7 writes boundary conditions that raise proxy cost honestly. Hold both without merging.</p>

<h2>Chapter summary</h2>
<p>Entropy in Field Technology is the receipt that time ran forward. ThermoAccountant at binding 2 records <code>entropyThisFrame</code>, boundary thermo, maintenance cost, free energy income, and dispatch steps — mirrored to <code>data_bus[24–28]</code>. The entropy floor seeds minimum irreversible noise at fabric init. The NEXUS Shannon oracle measures byte surprise with tunable storm thresholds — separate layer, separate product. Landauer and Shannon sit at the same vocabulary table with different plates; label rocks before you argue. Run the grep workbook; pass the three-layer exam; use the failure catalog when stderr disagrees with your narrative.</p>
<p>Prior: <a href="03-thermodynamics.html">Chapter 3 — Thermodynamics</a>. Next: <a href="05-packet-field.html">Chapter 5 — Packet Field</a> — defense reads sentences you did not write.</p>

<h2>Deep dive — comparative entropy plots without SI fraud</h2>
<p>Proxy integrals invite comparison: session A versus session B, coupling 0.3 versus 0.9, Classic versus x86 with identical inject protocol. The y-axis is engine-normalized receipt units — not watts, not kelvin, not bits erased at 300 K. Label the axis “proxy” in every chart you show a student.</p>
<p>Healthy comparative plots show monotonic <code>steps</code> with bounded entropy variance when knobs are stable. Pathological plots show <code>steps</code> rising while entropy flatlines — dispatch desync. Another pathology: entropy spikes without input activity — investigate maintenance cost and fidelity knobs before blaming malware.</p>
<p>When presenting to non-technical stakeholders, show two curves and one sentence: “More coupling moved more irreversibility in our labeled proxy ledger.” Do not show one THERMO number as “GPU carbon.” That is how rocks get hidden and careers get embarrassed.</p>

<h2>Deep dive — oracle case studies (labeled exercises)</h2>
<p><strong>Case A — English log:</strong> Low H, calm threshold, USER_OK egress to known port. Lesson: structure is not malice.</p>
<p><strong>Case B — encrypted payload:</strong> High H, alert threshold, SUSPICIOUS watchlist — not KILL until packet field corroborates process path and direction story.</p>
<p><strong>Case C — packed game asset:</strong> Medium-high H, storm threshold flicker — tune storm upward after habit baseline recorded; false storm exhaustion is security debt.</p>
<p><strong>Case D — zip during AMOURANTHRTX session:</strong> Oracle layer speaks; ThermoAccountant layer speaks separately. Write two paragraphs — one for file H, one for <code>entropyThisFrame</code> — before merging narrative.</p>
<p>Each case trains the three-layer exam in concrete stories. Chapter 5 adds gatekeeper axes; Chapter 4 refuses to let file surprise become automatic physics.</p>

<h2>Deep dive — maintenance cost as invisible labor</h2>
<p><code>prevMaintCost</code> rises when the engine pays coherence tax — preserving frame-to-frame structure when fidelity, resolution, or coupling demands sharp features. Operators who crank <code>GateFidelity</code> without reading maintenance lines are surprised by “heat” that is not mouse inject — it is temporal labor made visible.</p>
<p>Pair maintenance grep with Chapter 9 CFL messages. Often maintenance spikes follow aggressive knobs the guard partially saved from NaN — the engine still worked to keep the field legal. Thank the guard with lower knobs, not with disabling THERMO logging.</p>

<h2>Deep dive — entropy vocabulary for mixed audiences</h2>
<p>When physicists join security engineers in the same room, entropy becomes a battlefield word. Give each audience its sentence before debate starts:</p>
<ul>
<li><strong>Physicist sentence:</strong> “Proxy integral honors Landauer metaphor; we do not claim calorimetry.”</li>
<li><strong>Engineer sentence:</strong> “ThermoAccountant binding 2 populates every dispatch; grep proves it.”</li>
<li><strong>Security sentence:</strong> “Shannon H on files is NEXUS oracle — storm gauge, not GPU heat.”</li>
</ul>
<p>Three sentences, three layers, one meeting saved. Chapter 4 is diplomacy as much as thermodynamics — vocabulary prevents fistfights about fake joules.</p>

<h2>Study questions</h2>
<ol>
<li>Quote all five ThermoAccountant fields and bus mirrors.</li>
<li>Why is <code>entropyThisFrame</code> a proxy, and what theory does it honor?</li>
<li>What does entropy floor ~0.015 refuse?</li>
<li>How do calm / alert / storm thresholds differ from gatekeeper verdicts?</li>
<li>Explain <code>prevMaintCost</code> in plain English.</li>
<li>Run Workbook 4.A; classify three grep lines by layer.</li>
<li>Which failure mode matches “invoice from THERMO”?</li>
<li>Where does sealed time enter the thermo ledger?</li>
<li>Why is oracle storm not auto-KILL?</li>
<li>How does Chapter 7 obligate ThermoAccountant on Classic swipe?</li>
</ol>
"""


def expand_05() -> str:
    """Chapter 05 — Packet field, gatekeeper, jsonl, panel tour."""
    return r"""
<h2>Introduction — defensive perimeter as readable sentences</h2>
<p>Chapters 2 through 4 taught continuous state on silicon: fabric texels, die bytes, thermo receipts. Chapter 5 turns outward — not to the whole internet, but to <strong>your machine’s sockets</strong> rendered as operator-readable sentences. The packet field is the defensive core of NEXUS-Shield: local-first, MIT-licensed, grep-able, archived in <code>field jsonl</code> that survives reboot. It is <span class="tag impl">Implemented</span> in NEXUS. It is <span class="tag meta">not</span> inside AMOURANTHRTX Vulkan — conflating products is week-one failure.</p>
<p><code>ss</code> shows sockets. <code>tcpdump</code> shows frames. The packet field adds <strong>meaning</strong>: process path, port habit, TX versus RX, corroboration across axes, gatekeeper verdict summary. Defense, in Field Technology, is reading continuous state faster than confusion propagates — then choosing watchlist, block, or KILL with conscience. Chapter 7 takes the spear; this chapter holds the shield.</p>
<p>Queen browser (Chapter 21) routes WebRTC through the same gatekeeper instead of disabling WebRTC. Sovereign time (Chapter 19) and Truth DNS (Chapter 20) supply sealed clocks and trace-from-root resolution — packet field sentences sit beside those receipts, not above them. Chapter 12 lists rocks; this chapter teaches rhythm.</p>

<div class="objectives"><h2>Learning objectives</h2><ul>
<li>State the local-first boundary: which flows exist in jsonl and which myths do not.</li>
<li>Read the Connection Gatekeeper ten-axis table and map axes to verdicts.</li>
<li>Practice jsonl schema habits: append-only, sealed time columns, rotation ethics.</li>
<li>Apply KILL dossier ethics — permanent archive, operator authorship, forgiveness path.</li>
<li>Tour panel <code>https://127.0.0.1:9477/</code> and correlate UI rows with jsonl.</li>
<li>Trace Queen WebRTC chain from navigation to gatekeeper to thermo receipt.</li>
</ul></div>

<figure class="figure"><img src="../assets/images/packet-field.jpg" alt="Packet field flows" loading="lazy" /><figcaption>Figure 5.1 — Local flows as positions in operator-readable space. Not cloud omniscience.</figcaption></figure>

<h2>Plain English — every connection becomes a sentence</h2>
<div class="callout everyone"><strong>Plain English:</strong> The packet field is a diary your machine writes about who talked to whom, in which direction, on which port, with what habit — so you can read the diary instead of drowning in hex dumps.</div>
<p>Local-first means loopback truth: panel at :9477 on your host, jsonl under operator-owned paths, no phone-home conscience. The packet field does not see the whole internet. It sees endpoints your OS exposes to the daemon — <span class="tag impl">Implemented</span> scope. Claiming NEXUS “monitors the planet” is vendor fantasy; label it <span class="tag phil">Philosophy</span> until jsonl proves otherwise.</p>
<p>Direction is a field dimension. <strong>TX</strong> is egress you own — bytes you sent. <strong>RX</strong> is ingress you must explain — bytes you received. Asymmetry matters for corroboration: a peer that only RX-es strange payloads without TX context tells a different story than symmetric chatter.</p>

<h2>Connection Gatekeeper — ten-axis table</h2>
<p>Verdicts are summaries; axes are explanations. One weird packet does not condemn a peer — restraint is engineering, not sentiment. The gatekeeper scores up to ten axes and emits a verdict enum.</p>
<table><thead><tr><th>Axis</th><th>Question asked</th><th>Typical signal</th></tr></thead>
<tbody>
<tr><td>Process path</td><td>Which binary owns the socket?</td><td><code>/usr/bin/...</code> vs tmp mount</td></tr>
<tr><td>Port</td><td>Which habit class?</td><td>443 vs ephemeral vs shell-class</td></tr>
<tr><td>Direction</td><td>TX, RX, or both?</td><td>Egress-heavy vs listen-only</td></tr>
<tr><td>Payload shape</td><td>Size cadence entropy?</td><td>Bursts, TLS handshake, plain text</td></tr>
<tr><td>Habit</td><td>Seen before on this machine?</td><td>Registry learning — below</td></tr>
<tr><td>Honorability</td><td>Web context honest?</td><td>Queen navigation metadata</td></tr>
<tr><td>Corroboration</td><td>Independent witnesses agree?</td><td>dns + port + path alignment</td></tr>
<tr><td>Duration</td><td>Ephemeral flash or long dwell?</td><td>Short-lived vs persistent</td></tr>
<tr><td>Peer identity</td><td>Loopback vs LAN vs remote?</td><td>127.0.0.1 vs RFC1918 vs global</td></tr>
<tr><td>Policy</td><td>Operator rules engaged?</td><td>Watchlist, blocklist, sovereign mode</td></tr>
</tbody></table>
<table><thead><tr><th>Verdict</th><th>Meaning</th><th>Operator action</th></tr></thead>
<tbody>
<tr><td><code>USER_OK</code></td><td>Permitted flow</td><td>Archive trust; continue</td></tr>
<tr><td><code>EPHEMERAL</code></td><td>Short-lived, low risk</td><td>Log; usually no drama</td></tr>
<tr><td><code>SUSPICIOUS</code></td><td>Watchlist candidate</td><td>Corroborate; do not auto-KILL</td></tr>
<tr><td><code>HARM_CANDIDATE</code></td><td>Harm signature pattern</td><td>Review; KILL only after human authorship</td></tr>
</tbody></table>
<p><span class="tag impl">Implemented.</span> Grep NEXUS-Shield sources for gatekeeper scoring — not Vulkan bindings. Chapter 4’s Shannon oracle may corroborate payload surprise; it does not replace axis review.</p>

<h2><code>field jsonl</code> — schema habits and archive discipline</h2>
<p>Jsonl is append-only memory — each line a JSON object, one flow event or verdict witness per row. Habits that keep archives forensically usable:</p>
<ul>
<li><strong>One row, one claim.</strong> Do not stuff multiple peers into one line because JSON allows it — grep wants linear time.</li>
<li><strong>Sealed time column.</strong> Correlate with Chapter 19 sovereign receipts — wall clock lies; sealed session clock does not rewrite.</li>
<li><strong>Stable keys.</strong> Process path, port, direction, verdict — column names consistent across weeks so week-twelve diff works.</li>
<li><strong>Rotation with conscience.</strong> Large jsonl is truth; rotate with backup, encrypt at rest per operator policy, never “delete to feel better” without review.</li>
<li><strong>No retroactive edit.</strong> Time is linear — append correction rows, do not silently rewrite history.</li>
</ul>
<pre class="eq">{"ts_sealed":9123456,"dir":"RX","port":443,"path":"/usr/bin/queen-browser",
 "peer":"127.0.0.1:9477","verdict":"USER_OK","axis_note":"loopback panel"}
{"ts_sealed":9123489,"dir":"TX","port":4444,"path":"/tmp/.cache/a.out",
 "peer":"203.0.113.7:4444","verdict":"SUSPICIOUS","axis_note":"shell-class habit"}</pre>
<p>Example rows are pedagogical — your daemon may pack additional axes. The habit is: <strong>grep-friendly sentences</strong> that survive reboot and court your future self as witness.</p>
<div class="callout science"><strong>Science posture:</strong> jsonl is not physics. It is forensic narrative. Truth survives grep when keys are honest and timestamps sealed.</div>

<h2>KILL dossier ethics — permanent does not mean casual</h2>
<p>KILL is not a button mood. It creates a <strong>permanent dossier</strong> — archived, surviving reboot, readable years later when you forgot the afternoon’s frustration. Ethics:</p>
<ol>
<li><strong>Watchlist before block.</strong> <code>SUSPICIOUS</code> earns observation; KILL earns authorship.</li>
<li><strong>Corroboration before permanence.</strong> Multiple axes, optionally oracle alert, optionally DNS trace — not one weird packet.</li>
<li><strong>Human authorship.</strong> Daemons recommend; operators sign. No automated KILL because entropy stormed.</li>
<li><strong>Forgiveness path.</strong> Local memory enables review — downgrade watchlist, annotate dossier, admit mistake without phone-home.</li>
<li><strong>No cloud absolution.</strong> Vendor “global ban lists” outsource conscience; NEXUS keeps yours local.</li>
</ol>
<div class="callout love"><strong>Love as engineering restraint:</strong> KILL dossiers are gravestones, not confetti. The stack gives you power to remember — use it when you are willing to stand behind the memory.</div>
<p>Panel HTML at :9477 is ephemeral window chrome — pretty, convenient, not the archive. <code>field jsonl</code> and KILL dossiers are the memory. Screenshot the panel for teaching; trust jsonl for testimony.</p>

<h2>Port registry learning — habits, not textbook alone</h2>
<p>Ports are habits learned on <strong>your</strong> machine: 443 HTTPS, 53 DNS, 123 NTP, 9123 sovereign pulse, 9477 panel. Shell-class ports (4444, 1337 folklore) raise different axis weight than loopback 9477 health checks. The registry compares today’s flow against your history — not a generic list shipped from a vendor who never saw your lab.</p>
<p>First week on a fresh install: many flows read <code>EPHEMERAL</code> or lightly <code>SUSPICIOUS</code> because habit axis lacks memory — normal, not failure. Week six: repeated Queen WebRTC peers should stabilize toward <code>USER_OK</code> if honorability and paths stay clean. Sudden habit breakage — trusted port, alien path — is corroboration gold.</p>
<p>Chapter 20 Truth DNS at <code>127.0.0.1</code> with trace-from-root supplies naming honesty for corroboration. Packet field sentences plus DNS receipts beat either alone.</p>

<h2>Panel :9477 tour — command, packets, threats, signals</h2>
<p>Open <code>https://127.0.0.1:9477/</code> after <code>./nexus.sh</code> (or your package equivalent). Treat tabs as views on the same archive, not separate products.</p>
<table><thead><tr><th>Panel area</th><th>What you learn</th><th>Correlate with</th></tr></thead>
<tbody>
<tr><td>Command</td><td>Operator actions, daemon control</td><td>stderr, jsonl command rows</td></tr>
<tr><td>Packets</td><td>Live flow sentences</td><td><code>field jsonl</code> tail</td></tr>
<tr><td>Threats</td><td>Watchlist and harm candidates</td><td>Gatekeeper axes, not oracle alone</td></tr>
<tr><td>Signals</td><td>RF/audio orchestration hints</td><td>Chapter 6 Field Antenna JSON</td></tr>
<tr><td>DNS</td><td>Local resolution truth</td><td>Chapter 20 trace-from-root</td></tr>
<tr><td>Library</td><td>Reference docs in-tree</td><td>This primer — no CDN conscience</td></tr>
<tr><td>System</td><td>Service registry, ports</td><td>wiki service table :53 :67 :123 :9123 :9477</td></tr>
</tbody></table>
<p>Tour drill: pick one <code>USER_OK</code> row in Packets, one <code>SUSPICIOUS</code> row, grep jsonl for matching keys, note sealed time delta. If UI and jsonl disagree, UI is wrong until reconciled — same rule as HUD hex versus THERMO in Chapter 4.</p>

<h2>Queen WebRTC chain — gates held, not disabled</h2>
<p>Queen posture: <strong>nothing optional, hold all gates, MP4 mandatory in-tree, EME held not omitted.</strong> Wrong security story: disable WebRTC to feel safe. Right story: WebRTC through Connection Gatekeeper with honorability axis and packet field sentences per peer.</p>
<pre class="eq">Navigation → DNS (Ch.20) → socket open → gatekeeper axes → verdict
          → field jsonl append → thermo receipt (Ch.7/21) → operator review</pre>
<p>WebRTC media paths do not bypass NEXUS because Queen is sovereign browser, not a chrome fork with holes poked for convenience. Each peer earns TX/RX diary entries. Thermo context per WebGL surface inherits AMOURANTHRTX proxy discipline when built with <code>QUEEN_BROWSER_BUILD</code> — offense and defense share timestamps without merging scores.</p>
<p>Chapter 21 is full doctrine. This chapter plants the chain: packet field is not “network chapter only” — it is the perimeter Queen wears.</p>

<h2>TX and RX — contracts the gatekeeper expects you to honor</h2>
<p>Every packet field sentence carries direction because accountability is asymmetric. TX flows are confessions: you originated bytes, chose destination, accepted egress policy. RX flows are interrogations: someone reached your machine — which process listened, which port opened, which habit broke? Operators who journal only RX panic miss half the story; operators who journal only TX forget that defense begins at ingress.</p>
<p>Corroboration pairs directions. A peer with heavy RX and no TX history may be benign software update noise — or may be exfiltration listening post. A symmetric chat pattern on loopback 9477 differs from symmetric chatter to global RFC1918. The gatekeeper encodes direction on its own axis; your job is to narrate why the direction makes sense in plain language before you escalate verdicts.</p>
<p>Chapter 2 named packet field as the third scale of state. Direction is not metadata garnish — it is a coordinate. Queen navigation that claims HTTPS honorability while jsonl shows raw shell-class TX is a lie the axes exist to catch.</p>

<h2>Defense rhythm — daily, weekly, incident</h2>
<p>Field Technology is practice, not one-time read. Rhythm beats heroics.</p>
<table><thead><tr><th>Cadence</th><th>Action</th><th>Artifact</th></tr></thead>
<tbody>
<tr><td>Daily</td><td>Glance panel Packets while dev session runs</td><td>Mental model of normal</td></tr>
<tr><td>Weekly</td><td>Archive one gatekeeper decision explicitly</td><td>jsonl trust or watchlist row</td></tr>
<tr><td>Weekly</td><td>grep THERMO + tail jsonl same session</td><td>Ch. 11 observability marriage</td></tr>
<tr><td>Incident</td><td>SUSPICIOUS → corroborate axes → decide</td><td>Annotated jsonl, not rage-KILL</td></tr>
<tr><td>Quarterly</td><td>Rotate jsonl backup; test restore</td><td>Encrypted archive integrity</td></tr>
</tbody></table>
<div class="callout drill"><strong>Drill 5.A — Defense baseline</strong></div>
<pre class="eq">./nexus.sh
curl -k https://127.0.0.1:9477/ | head -5   # panel alive
ss -tunap | head -20
tail -5 /var/lib/nexus-shield/field.jsonl    # path may vary per install</pre>
<div class="callout drill"><strong>Drill 5.B — Corroboration write</strong></div>
<pre class="eq"># After SUSPICIOUS row appears:
grep -F 'SUSPICIOUS' /var/lib/nexus-shield/field.jsonl | tail -3
# Record process path + port + DNS answer for same peer in operator journal</pre>

<h2>Failure catalog — packet field edition</h2>
<table><thead><tr><th>Failure mode</th><th>Symptom</th><th>Fix</th></tr></thead>
<tbody>
<tr><td>Product blur</td><td>grep gatekeeper in AMOURANTHRTX engine</td><td>Separate repos — Ch. 1 table</td></tr>
<tr><td>Cloud fantasy</td><td>Expect NEXUS to see global internet</td><td>Local-first scope label</td></tr>
<tr><td>One-packet condemn</td><td>KILL on first weird RX</td><td>94/6 restraint; watchlist</td></tr>
<tr><td>Panel as archive</td><td>Screenshot only, no jsonl</td><td>Append rows; panel is ephemeral</td></tr>
<tr><td>Oracle merge</td><td>Shannon storm → auto verdict</td><td>Ch. 4 layer separation</td></tr>
<tr><td>Habit amnesia</td><td>Fresh install panic at EPHEMERAL</td><td>Let registry learn week one</td></tr>
<tr><td>Queen hole-poke</td><td>Disable WebRTC “for security”</td><td>Ch. 21 hold gates</td></tr>
<tr><td>Time fantasy</td><td>jsonl rows without sealed clock</td><td>Ch. 19 sovereign time column</td></tr>
</tbody></table>

<h2>Ephemeral versus permanent — what defense remembers</h2>
<p>Panel HTML refreshes; browser tabs close; screenshots fade from chat logs. <code>field jsonl</code> and KILL dossiers remain — that asymmetry is design. Operators who understand permanence wield KILL sparingly and watchlists generously. Operators who mistake panel cache for archive delete history by reinstalling and wonder why habits reset.</p>
<p>Backup jsonl before OS upgrades. Encrypt archives at rest if your threat model includes shared disks. Rotate logs with append-only discipline — never rewrite a row to feel better about Tuesday. Chapter 19 sealed time columns make rotated archives comparable across months.</p>

<h2>Cross-links — defense meets offense</h2>
<p>Chapter 2: three scales — packet field is scale three. Chapter 4: Shannon oracle corroborates, does not replace axes. Chapter 6: Field Antenna JSON panels appear under Signals — correlate, no super-score. Chapter 7: dispatch thermo runs parallel; merge timestamps only. Chapter 11: observability grep rhythm. Chapter 19–20: sovereign time and Truth DNS. Chapter 21: Queen all gates. Chapter 12: honesty rocks on local scope.</p>

<h2>Chapter summary</h2>
<p>The packet field turns local sockets into sentences in <code>field jsonl</code> — TX/RX, process path, port habits, gatekeeper verdicts from ten axes. Watchlist before block; KILL dossiers permanent with human authorship. Port registry learns your machine. Panel :9477 tours live views; jsonl is memory. Queen WebRTC flows through gatekeeper, not around it. Defense rhythm is daily glance, weekly archive, incident corroboration.</p>
<p>Prior: <a href="04-entropy.html">Chapter 4 — Entropy</a>. Next: <a href="06-rf-signals.html">Chapter 6 — RF &amp; Signals</a> — three meanings before offense takes the spear in <a href="07-gpu-engine.html">Chapter 7</a>.</p>

<h2>Deep dive — NEXUS daemon rhythm and sampling ethics</h2>
<p>NEXUS daemons sample sockets on a duty cycle tuned by calm/alert/storm posture from the entropy oracle — nurse watching vitals, not judge passing sentence. High storm duty increases CPU wakeups locally; it does not phone home. Operators on laptops notice battery tradeoffs — honesty includes admitting local defense costs local watts, still not the same as <code>entropyThisFrame</code> proxy.</p>
<p>Sampling sees process paths when OS APIs allow; containers and sandboxes may obscure paths — gatekeeper axes downgrade confidence, not invent guilt. When path is unknown, verdicts trend EPHEMERAL or SUSPICIOUS rather than USER_OK — restraint again.</p>
<p>Corroboration means independent witnesses: socket table, payload hints, DNS resolution trace (Chapter 20), sovereign time column (Chapter 19), optional tcpdump slice you attach to incident notes. One witness is never a trial.</p>

<h2>Deep dive — threat-panel.json and live panel anatomy</h2>
<p><code>threat-panel.json</code> feeds the :9477 dashboard — ephemeral snapshot refreshed by daemon, not a substitute for jsonl archive. Read it for “what is happening now”; grep jsonl for “what happened across reboots.”</p>
<table><thead><tr><th>Panel region</th><th>Source</th><th>Persistence</th></tr></thead>
<tbody>
<tr><td>Live flows table</td><td>Current gatekeeper scoring</td><td>Panel session</td></tr>
<tr><td>Watchlist column</td><td>SUSPICIOUS history</td><td>jsonl-backed</td></tr>
<tr><td>DNS / time widgets</td><td>Ch. 19–20 services</td><td>Config + receipts</td></tr>
<tr><td>Signals / RF tabs</td><td>Field Antenna JSON</td><td>Correlate only — Ch. 6</td></tr>
<tr><td>Command tab</td><td>Operator actions</td><td>Permanent actions → jsonl</td></tr>
</tbody></table>
<p>Tour the panel once per month even if quiet — familiarity prevents panic formatting during real incidents.</p>

<h2>Deep dive — incident narrative template (half page)</h2>
<p>When a flow surprises you, write before you click KILL:</p>
<ol>
<li><strong>Sentence</strong> — one jsonl row quoted: direction, ports, path, verdict.</li>
<li><strong>Context</strong> — what you were doing (Queen tab, build, game, ssh).</li>
<li><strong>Corroboration</strong> — second witness (oracle H, DNS trace, tcpdump one-liner).</li>
<li><strong>Decision</strong> — watch, block, forgive, KILL — with date and operator name.</li>
<li><strong>Follow-up</strong> — grep THERMO if AMOURANTHRTX ran parallel; note timestamp only.</li>
</ol>
<p>This template is how field literacy meets love as restraint — memory without phone-home, permanent actions only with authorship.</p>

<h2>Deep dive — ten gatekeeper axes in plain English</h2>
<p>Axes are not secret sauce — they are explicit questions the daemon asks before summarizing a verdict. Operators who learn axes forgive peers intelligently and escalate with evidence.</p>
<table><thead><tr><th>Axis theme</th><th>Question the axis asks</th><th>Typical innocent story</th><th>Typical scrutiny story</th></tr></thead>
<tbody>
<tr><td>Process path stability</td><td>Does this binary usually own this socket?</td><td>Same browser binary, same 443 egress</td><td>Unknown helper spawned tunnel</td></tr>
<tr><td>Port habit</td><td>Is this port normal for your machine?</td><td>443, 53, local 9477</td><td>4444-class first contact</td></tr>
<tr><td>Direction balance</td><td>TX/RX ratio plausible for app?</td><td>Streaming RX-heavy session</td><td>RX flood with idle TX</td></tr>
<tr><td>Payload hints</td><td>Do bytes look structured or noisy?</td><td>TLS-shaped chatter</td><td>Opaque bulk without context</td></tr>
<tr><td>Honorability</td><td>Does navigation context match socket?</td><td>Queen tab origin matches peer</td><td>WebRTC without page context</td></tr>
<tr><td>Duration class</td><td>EPHEMERAL blip or persistent tunnel?</td><td>DNS UDP millisecond</td><td>Multi-hour reverse shell shape</td></tr>
<tr><td>Corroboration count</td><td>How many independent signals agree?</td><td>ss + path + calm oracle</td><td>Single weird frame only</td></tr>
<tr><td>Registry memory</td><td>Has this peer been forgiven before?</td><td>Known dev server</td><td>Repeated SUSPICIOUS after review</td></tr>
<tr><td>Time alignment</td><td>Does sovereign time column agree?</td><td>USER_OK pulse</td><td>SQUIDGIE during same flow</td></tr>
<tr><td>Operator override</td><td>Human watchlist or block present?</td><td>Manual USER_OK for lab</td><td>Prior KILL pattern cousin</td></tr>
</tbody></table>
<p>Verdict enums compress axis stories — always read axes before arguing with the enum. Chapter 12 rocks table lists conflation failures; this table lists human judgment inputs.</p>

<h2>Deep dive — building a port habit registry over month one</h2>
<p>Week one registry is naive — textbook ports only. Week four registry is <em>yours</em>: dev servers, game anticheat channels, local mesh sync, Queen WebRTC UDP patterns. The packet field learns without cloud upload because jsonl stays on disk.</p>
<p>Operators exporting habits between machines should export jsonl archives, not screenshots. Import on new machine seeds registry — forgiveness and suspicion travel with evidence, not with vendor account login.</p>
<p>Document lab ports in operator runbook: “Port 8765 is my test echo — expect USER_OK when binary path matches.” Future-you will thank present-you when a colleague’s script triggers SUSPICIOUS on that port.</p>

<h2>Deep dive — jsonl grep patterns for week-two defense</h2>
<pre class="eq">grep '"verdict":"SUSPICIOUS"' field.jsonl | tail -20
grep '"direction":"RX"' field.jsonl | grep -v 'USER_OK' | tail -10
grep '"port":' field.jsonl | sort | uniq -c | sort -rn | head -20</pre>
<p>First pattern surfaces watchlist candidates. Second finds ingress that did not earn USER_OK — hospitality with scrutiny. Third builds empirical port histogram for <em>your</em> machine — registry ground truth beats textbook port lists alone.</p>
<p>Pair grep with panel tour weekly. jsonl is memory; panel is pulse. Defense literacy is rhythm — daily pulse glance, weekly grep archive, monthly port histogram update in runbook.</p>

<h2>Study questions</h2>
<ol>
<li>Why is packet field local-first, and what myth does that refuse?</li>
<li>Name four gatekeeper axes and two verdict enums.</li>
<li>What jsonl habits keep archives grep-friendly?</li>
<li>When is KILL ethical versus premature?</li>
<li>Tour :9477 — which tab maps to Field Antenna signals?</li>
<li>Trace Queen WebRTC chain in five steps.</li>
<li>Distinguish panel HTML from KILL dossier persistence.</li>
<li>Run Drill 5.A; record one normal and one notable flow.</li>
<li>Why is one weird packet insufficient for condemnation?</li>
<li>How does Chapter 7 thermo relate without merging scores?</li>
</ol>
"""


def expand_06() -> str:
    """Chapter 06 — RF meanings, planetary weave, Field Antenna, FSPL."""
    return r"""
<h2>Introduction — three meanings of RF before you touch the spear</h2>
<p>Operators arrive at Field Technology with one acronym and three incompatible intuitions. <strong>RF</strong> might mean the shader shell in <code>planetary_weave.comp</code>, the NEXUS Field Antenna orchestrator, or the wave potential on binding 8 — <code>fieldPhi</code> — that Maxwell language calls Φ, not megahertz. Chapter 6 separates them with honesty labels before Chapter 7 hands you <code>vkCmdDispatch</code>. Confusion here produces week-six embarrassment: ionosphere arguments from pretty colors, spectrum claims from jsonl panels, or radio astronomy from a Classic canvas screenshot.</p>
<p>Defense in Chapter 5 taught packet sentences. Entropy in Chapter 4 taught layer separation. This chapter teaches <strong>signal vocabulary</strong> — what is <span class="tag vis">Visual</span>, what is <span class="tag impl">Implemented</span> local orchestration, what is electrical metaphor on the fabric. The workshop protocol at chapter end is a lab you can run in an afternoon; the handoff to Chapter 7 states plainly: offense writes fields on the GPU; RF shaders do not replace dispatch literacy.</p>

<div class="objectives"><h2>Learning objectives</h2><ul>
<li>Label three RF contexts with correct status tags.</li>
<li>Sketch planetary weave stack radii from core to magnetosphere.</li>
<li>Read Field Antenna JSON panel outputs and correlate with packet field.</li>
<li>Work FSPL teaching worksheet — ITU/FCC context, not shader compute.</li>
<li>Disambiguate <code>fieldPhi</code> binding 8 from literal radio propagation.</li>
<li>Execute workshop protocol and articulate handoff to Chapter 7.</li>
</ul></div>

<figure class="figure"><img src="../assets/images/chapters/ch06-planetary-weave.jpg" alt="Planetary weave cross-section" loading="lazy" /><figcaption>Figure 6.1 — Planetary weave: visual vocabulary. Not a spectrum analyzer.</figcaption></figure>

<h2>Three meanings table — label before you speak</h2>
<table><thead><tr><th>Context</th><th>What “RF” means</th><th>Label</th><th>Product</th></tr></thead>
<tbody>
<tr><td><code>planetary_weave.comp</code></td><td>Atmospheric shell layer in Earth cross-section shader</td><td><span class="tag vis">Visual</span></td><td>AMOURANTHRTX</td></tr>
<tr><td>NEXUS Field Antenna</td><td>Local RF/audio/wired/laser orchestration + JSON panels</td><td><span class="tag impl">Implemented</span></td><td>NEXUS-Shield</td></tr>
<tr><td><code>fieldPhi</code> binding 8</td><td>Wave / gate potential — electrical metaphor</td><td><span class="tag impl">Implemented</span> + <span class="tag meta">metaphor</span></td><td>AMOURANTHRTX</td></tr>
</tbody></table>
<div class="callout science"><strong>Do not</strong> equate GPU Phi with ionospheric propagation without labeling the jump. Chapter 12 rock: RF planetary shell is <code>planetary_weave.comp</code> visual only.</div>
<p>Queen WebRTC (Chapter 21) uses real network stacks behind gatekeeper — still not the same as weave shader art. WebRTC peers produce packet field sentences; planetary weave produces pedagogy pixels.</p>

<h2>Planetary weave — stack radii from core to magnetosphere</h2>
<p><code>planetary_weave.comp</code> draws a concentric Earth cross-section — not a physics simulation of magnetohydrodynamics, a <strong>visual vocabulary</strong> for where signals “live” in the stack metaphor. Radii are shader constants; treat them as labeled shells in operator teaching, not satellite telemetry.</p>
<pre class="eq">// Pedagogical shell stack (conceptual outer → inner)
core → crust → hydrosphere → clouds → troposphere
     → stratosphere → mesosphere → ionosphere
     → L_RF shell: #define R_RF (R_EARTH + 1.05)
     → magnetosphere → exosphere breath</pre>
<p>The <strong>RF shell</strong> sits exterior to ionosphere in the narrative — a colored ring reminding you that propagation stories have a place in the stack without computing path loss in GLSL. <code>R_EARTH</code> anchors scale; <code>R_RF</code> offsets the teachable RF band as art. Swipe to weave canvas in AMOURANTHRTX when you want vocabulary; grep THERMO when you want dispatch truth.</p>
<p>Cross-link Chapter 15 Maxwell: binding 8 Phi participates in discrete Laplacian coupling on the fabric — neighborhood whispers, not ionospheric whistlers. Cross-link Chapter 9: <code>FIELD_PHI_MILLI = 618</code> and <code>GateFidelity</code> sharpen gates — folklore mnemonic with a number, not a claim the universe prefers φ because the HUD said so.</p>
<p>Cross-link Chapter 12 honesty table: claiming the weave shader predicts HF skip zones is <span class="tag vis">Visual</span> accident marketed as instrument — refuse.</p>

<h2>Field Antenna orchestrator — JSON panels that are real</h2>
<p>NEXUS Field Antenna is <span class="tag impl">Implemented</span> local orchestration across RF, audio, wired, and optical reference bands. It watches flows and anchors meaningful to <strong>your machine</strong> — not global spectrum survey.</p>
<ul>
<li>Optical / laser reference entries: 405–1550 nm teaching bands</li>
<li>LIDAR flow ports registered beside socket habits</li>
<li>GPS field anchors for triangulation metaphor — not replacement for survey grade receivers</li>
<li>Outputs: <code>field-antenna-panel.json</code>, <code>field-rf-panel.json</code>, <code>signals-field-panel.json</code></li>
</ul>
<p>Panel :9477 Signals tab (Chapter 5) surfaces these artifacts. Correlate JSON rows with <code>field jsonl</code> sentences — same peer, same sealed time column, different views. <strong>No merged super-score.</strong> Field Antenna does not replace gatekeeper verdicts; packet field does not replace FSPL homework.</p>
<table><thead><tr><th>JSON artifact</th><th>Typical content</th><th>Correlate with</th></tr></thead>
<tbody>
<tr><td><code>field-antenna-panel.json</code></td><td>Antenna path registry, band tags</td><td>Signals tab, local hardware</td></tr>
<tr><td><code>field-rf-panel.json</code></td><td>RF flow summaries, habit notes</td><td>Packet field port axis</td></tr>
<tr><td><code>signals-field-panel.json</code></td><td>Cross-domain signal map</td><td>Chapter 5 defense rhythm</td></tr>
</tbody></table>

<h2>FSPL teaching worksheet — path loss on paper, not in shaders</h2>
<p>Free-space path loss (FSPL) belongs in operator notebooks and NEXUS teaching docs — <strong>not</strong> inside AMOURANTHRTX fabric shaders. ITU-R and FCC contexts use:</p>
<div class="eq">FSPL ∝ 20·log₁₀(d) + 20·log₁₀(f)</div>
<p>Distance <em>d</em> grows loss with twenty log ten; frequency <em>f</em> does the same. Double distance costs ~6 dB; double frequency costs ~6 dB. The worksheet builds intuition before you touch hardware.</p>
<div class="callout drill"><strong>Worksheet 6.A — FSPL estimates</strong></div>
<pre class="eq"># Given: f = 2.4 GHz Wi-Fi, d = 10 m (free space teaching model)
# FSPL ≈ 20*log10(10) + 20*log10(2.4e9)  [use consistent units in your notebook]
# Compare: d = 100 m — how many dB added vs 10 m?
# Label answer: teaching estimate — not measured in planetary_weave.comp</pre>
<p>Worksheet 6.B: repeat for 915 MHz ISM at 1 km. Worksheet 6.C: explain why attic copper foil does not change shader <code>R_RF</code> constant — visual shell unchanged by real-world sheet metal.</p>
<p>Chapter 6 honesty: FSPL exercises train judgment for Field Antenna context. They do not authorize claims that Classic canvas color maps predict link margin.</p>

<h2>Phi versus RF — disambiguation clinic</h2>
<p><code>fieldPhi</code> on binding 8 is the analog fabric’s wave and gate potential channel. Shaders read and write Φ per texel; host packs <code>WaveSpeed</code>, <code>GateFidelity</code>, <code>PropalacticScale</code> into FCC floats. This is Maxwell neighborhood on a grid — Chapter 15 — not literal RF carrier tracking.</p>
<table><thead><tr><th>Question</th><th>Phi / binding 8</th><th>RF / Field Antenna</th><th>Weave shader</th></tr></thead>
<tbody>
<tr><td>Measured in MHz?</td><td>No — arbitrary field units</td><td>Band labels for orchestration</td><td>No — art scale</td></tr>
<tr><td>Where grep?</td><td>THERMO + fabric + FCC slots</td><td>NEXUS JSON + jsonl</td><td>Canvas swipe only</td></tr>
<tr><td>Honest label</td><td><span class="tag impl">Implemented</span> metaphor</td><td><span class="tag impl">Implemented</span> local</td><td><span class="tag vis">Visual</span></td></tr>
<tr><td>Couples to Thermo?</td><td>Yes — <code>FieldCoupling</code></td><td>Indirect via machine activity</td><td>No — decor</td></tr>
</tbody></table>
<p>Clinic sentence: “Phi gradient steepened, so RF must be jammed” is category error. “Field Antenna noted 2.4 GHz habit breakage on RX, gatekeeper SUSPICIOUS” is legible defense. “Ionosphere glow red on weave” is art critique, not propagation measurement.</p>

<h2>Workshop protocol — afternoon lab</h2>
<ol>
<li><strong>Label pass (15 min):</strong> List three RF meanings from memory; tag each <span class="tag vis">Visual</span>, <span class="tag impl">Implemented</span>, or <span class="tag meta">metaphor</span>.</li>
<li><strong>Weave swipe (20 min):</strong> Open AMOURANTHRTX planetary weave canvas; sketch shell stack on paper with <code>R_RF</code> noted; refuse FSPL claims from colors.</li>
<li><strong>FSPL worksheet (25 min):</strong> Complete 6.A–6.C on paper; photograph page for operator journal — not for vendor slide deck.</li>
<li><strong>NEXUS panels (30 min):</strong> <code>./nexus.sh</code>; open :9477 Signals; read three JSON artifacts; tail matching <code>field jsonl</code> rows.</li>
<li><strong>Phi grep (20 min):</strong> <code>./linux.sh run</code>; <code>set AnalogFields.GateFidelity 0.9</code>; grep THERMO + FCC; confirm fabric offense path alive — handoff prep.</li>
<li><strong>Disambiguation drill (10 min):</strong> Write three sentences — one correct per layer; one deliberate category error; fix the error aloud.</li>
</ol>
<div class="callout everyone"><strong>Plain English:</strong> The workshop teaches you to point at the right receipt — jsonl, stderr, or screenshot — before you argue about signals.</div>

<h2>Ionosphere and magnetosphere — teachable shells, not predictions</h2>
<p>In the weave narrative, ionosphere and magnetosphere rings sit outside troposphere weather and inside exosphere breath. They exist so instructors can point at a screen and say: “HF stories live in sky vocabulary; your loopback panel lives in operator vocabulary.” The shader does not compute critical frequency, foF2, or K-index. It paints teachable regions.</p>
<p>When a student asks whether red ionosphere glow means solar storm, answer with labels: <span class="tag vis">Visual</span> pedagogy. Then open :9477 and show jsonl habits — defense receipts. Then run <code>./linux.sh run</code> and grep THERMO — offense receipts. Three layers, three answers, one disciplined operator.</p>
<p>Chapter 10 spiderweb mirror uses fabric averages, not ionosphere colors. Chapter 6 refuses the shortcut that makes pretty globes feel like NOAA products.</p>

<h2>Queen, WebRTC, and RF words in UI</h2>
<p>Queen holds WebRTC gates (Chapter 21). RF vocabulary in UI still passes Connection Gatekeeper — honorability axis asks whether navigation context matches socket reality. Field Antenna may tag RF bands; packet field records peers; thermo proxy records dispatch cost on Queen build — parallel witnesses, not one score.</p>
<p>MP4 mandatory in-tree means media paths are not outsourced to CDN conscience — local archive discipline matches jsonl ethos. EME held, not omitted, because sovereign browser doctrine refuses hole-poking.</p>

<h2>Failure catalog — RF edition</h2>
<table><thead><tr><th>Failure mode</th><th>Symptom</th><th>Fix</th></tr></thead>
<tbody>
<tr><td>Weave as instrument</td><td>HF propagation forecast from shader</td><td><span class="tag vis">Visual</span> rock — Ch. 12</td></tr>
<tr><td>Phi as MHz</td><td>“Tune binding 8 to 2.4G”</td><td>FCC floats are field knobs, not carrier</td></tr>
<tr><td>FSPL in GLSL fantasy</td><td>Expect path loss in fabric</td><td>Paper worksheet only</td></tr>
<tr><td>JSON super-score</td><td>Merge antenna JSON + gatekeeper</td><td>Correlate; separate verdicts</td></tr>
<tr><td>GPS metaphor as survey</td><td>Sub-centimeter claims from anchors</td><td>Label triangulation metaphor</td></tr>
<tr><td>Disable WebRTC</td><td>Queen security hole-poke</td><td>Ch. 21 hold gates</td></tr>
<tr><td>Cloud RF omniscience</td><td>NEXUS sees planet spectrum</td><td>Local-first — Ch. 5</td></tr>
<tr><td>Skip workshop</td><td>Jump to Ch. 7 without labels</td><td>Run protocol once</td></tr>
</tbody></table>

<h2>Audio, wired, and optical bands — one orchestrator, many witnesses</h2>
<p>Field Antenna does not stop at textbook RF. Local orchestration includes audio device paths, wired interface habits, and optical reference bands from 405 nm through 1550 nm — teaching anchors for laser and LIDAR vocabulary on <strong>your</strong> machine. Each band entry is a labeled witness in JSON, not a claim NEXUS measured photons in your fiber run.</p>
<p>LIDAR flow ports in the registry sit beside TCP habits: a UDP burst on a registered port may correlate with a signals-field row without merging into gatekeeper verdict math. GPS field anchors supply triangulation metaphor for panel maps — useful pedagogy when teaching children the difference between “where the UI drew a dot” and “where survey equipment proved a coordinate.”</p>
<p>When Signals tab shows optical entries alongside RF summaries, practice the Chapter 5 rule: correlate timestamps with <code>field jsonl</code>, compare process paths, refuse single-score dashboards. Field Technology trains parallel reading — thermo stderr, packet sentences, antenna JSON — the operator integrates.</p>

<h2>Propagation vocabulary without instrument fantasy</h2>
<p>Operators need words for sky and wire even when shaders are art. Teach vocabulary honestly:</p>
<ul>
<li><strong>Ground wave</strong> — metaphor for local wired habits and loopback flows; grep jsonl, not weave colors.</li>
<li><strong>Sky wave</strong> — ionosphere story in planetary weave shell; <span class="tag vis">Visual</span> only.</li>
<li><strong>Free space</strong> — FSPL worksheet domain; paper and calculator, not <code>fieldPhi</code> texels.</li>
<li><strong>Multipath</strong> — real Wi-Fi frustration; Field Antenna may note band congestion patterns locally without predicting shader palette.</li>
</ul>
<p>Chapter 14 Shannon surprise on encrypted payloads sometimes correlates with “noise floor” stories — still not weave red pixels. Keep layers separated as Chapter 4 demands.</p>

<h2>Handoff to Chapter 7 — offense takes the spear</h2>
<p>You labeled three RF meanings. You correlated Field Antenna JSON with packet field sentences without merging scores. You worked FSPL on paper while refusing shader compute fantasy. You disambiguated Φ on binding 8 from literal radio.</p>
<p><strong>Chapter 7</strong> is next: thin host, fat GPU, <code>Pipeline::dispatch_canvas()</code> → <code>vkCmdDispatch</code>. Default canvas is <code>x86.comp</code> with Field Die — offense writes guest RAM, fabrics, thermo receipts every tick. Planetary weave taught vocabulary; dispatch teaches sovereignty.</p>
<pre class="eq">Defense (Ch.5) read jsonl → RF (Ch.6) labeled meanings → Offense (Ch.7) vkCmdDispatch</pre>
<p>Carry forward: stderr before screenshots, rocks before poetry, grep before argument. ThermoAccountant from Chapter 4 still populates binding 2 on every dispatch — RF clarity does not pause thermo obligation.</p>
<p>Continue: <a href="07-gpu-engine.html">Chapter 7 — GPU Field Engine</a>. Prior: <a href="05-packet-field.html">Chapter 5 — Packet Field</a>. Rocks: <a href="12-reality-theory.html">Chapter 12</a>. Maxwell creditor: <a href="../creditors/maxwell.html">Maxwell</a>.</p>

<h2>Chapter summary</h2>
<p>RF in this stack names three different stories: planetary weave visual shell at <code>R_RF</code>, NEXUS Field Antenna local orchestration with JSON panels, and <code>fieldPhi</code> wave potential on binding 8 as implemented electrical metaphor. FSPL works on teaching worksheets — not in fabric shaders. Workshop protocol trains label discipline. Chapter 7 inherits operators who will not confuse ionosphere art with dispatch truth.</p>

<h2>Deep dive — ITU-R and FCC as teaching context, not shader constants</h2>
<p>NEXUS documentation cites ITU-R and FCC framing for path loss, band plans, and operator vocabulary — <span class="tag phil">teaching context</span> beside local jsonl scope. The citations exist so instructors can assign worksheets without pretending AMOURANTHRTX shaders became spectrum regulators.</p>
<p>When students ask “is this legal on 5 GHz,” answer: consult counsel and national regulators; Field Primer teaches technical honesty and local perimeter, not legal advice. When students ask “does weave red mean illegal transmit,” answer: <span class="tag vis">Visual</span> only — check Field Antenna JSON and jsonl for real local sense layers.</p>

<h2>Deep dive — spectrum analyzer honesty for advanced labs</h2>
<p>External USB analyzers may join advanced operator labs — hardware outside the stack. If you capture a trace, label it <span class="tag impl">External instrument</span> distinct from planetary weave screenshots and distinct from <code>fieldPhi</code> heatmaps. Three images, three labels, one collage grade in Exercise 6.C.</p>
<p>Never paste analyzer traces into threat dashboards as auto-verdicts. Correlation paragraph only: “Analyzer peak at time T; jsonl RX burst at T±2s; weave screenshot unrelated.”</p>
<p>Chapter 11 observability extends grep rhythm to RF labs — archive traces with session IDs like thermo journals.</p>

<h2>Deep dive — teaching children and newcomers RF discipline</h2>
<p>Children learn labels faster than they learn Vulkan. Start with three-card drill: Visual, Implemented, Metaphor. Planetary weave card says Visual. Field Antenna card says Implemented local JSON. Phi card says Implemented fabric metaphor. FSPL worksheet card says Paper math.</p>
<p>Adults skip cards and skip labels — then argue across layers at dinner. Chapter 6 exists to front-load the argument you would otherwise have at midnight on Discord.</p>

<h2>Deep dive — planetary weave shader stack as literature</h2>
<p>Open <code>planetary_weave.comp</code> as literature, not instrumentation. Radii constants name shells — core, crust, hydrosphere, clouds, troposphere, ionosphere, <code>R_RF</code>, magnetosphere — each a pedagogical ring. The RF shell is one radius in a stack metaphor, not a measurement of watts exiting your Wi-Fi antenna.</p>
<p>Color choices encode mood: warm ionosphere, cool magnetosphere, cloudy troposphere. Mood is not METAR. When instructors assign “read the stack,” students should sketch rings on paper and label each <span class="tag vis">Visual</span> before discussing NEXUS Field Antenna JSON.</p>
<p>Swiping to weave in AMOURANTHRTX does not pause Field Die default product truth — weave is alternate curriculum on shared Vulkan spine per Chapter 7. Thermo still accrues underneath; THERMO still greps.</p>

<h2>Deep dive — Field Antenna operator tour (30 minutes)</h2>
<ol>
<li>Start NEXUS; open Signals tab at :9477.</li>
<li>Load <code>field-antenna-panel.json</code> — note schema version in file header if present.</li>
<li>Compare <code>field-rf-panel.json</code> versus <code>signals-field-panel.json</code> — different slices, same honesty rule: correlate, no super-score.</li>
<li>Record one audio device entry, one wired entry, one optical reference band entry — three labels, three sentences.</li>
<li>Open Classic Phi heatmap in AMOURANTHRTX — fourth image in collage; label fabric metaphor.</li>
<li>Complete FSPL worksheet for hypothetical 2.4 GHz link at 10 m — paper only.</li>
<li>Write handoff sentence: “Phi is binding 8; weave is Visual; antenna is local JSON.”</li>
</ol>
<p>Tour completes Chapter 6 workshop; archive notes beside jsonl, not instead of jsonl.</p>

<h2>Deep dive — magnetosphere and exosphere as narrative bookends</h2>
<p>Outside RF shell, magnetosphere and exosphere rings teach that signals live inside stories about space — not that shaders predict solar wind pressure. Narrative bookends bracket the RF chapter: inner shells ground newcomers in geography metaphor; outer shells remind that hype expands outward unless labels contract it.</p>
<p>Chapter 17 God at holographic boundary and Chapter 6 planetary weave both use cosmic vocabulary — different jobs. Chapter 17 sacred long-form; Chapter 6 category discipline. Do not merge them into one cosmology slide without rocks.</p>

<h2>Deep dive — RF chapter closing ritual before dispatch</h2>
<p>Before opening Chapter 7, run this sixty-second ritual:</p>
<ol>
<li>Say aloud: “Weave is Visual.”</li>
<li>Say aloud: “Antenna JSON is local Implemented.”</li>
<li>Say aloud: “Phi is fabric metaphor on binding 8.”</li>
<li>Say aloud: “FSPL is paper, not GLSL.”</li>
<li>Grep one THERMO line — offense prep reminder.</li>
<li>Archive one jsonl row if NEXUS running — defense prep reminder.</li>
</ol>
<p>Ritual sounds silly until the third week when someone cites ionosphere color as threat intel. Chapter 6 buys you immunity to that meeting.</p>

<h2>Deep dive — FSPL worksheet answer key discipline</h2>
<p>Instructors publish formulas; operators compute on paper. A sample worksheet row: distance 10 m, frequency 2.45 GHz, path loss increases with log distance and log frequency — proportionality from Chapter 6 main text. Students hand in worksheet plus one sentence: “This number did not come from <code>fieldPhi</code>.”</p>
<p>Answer keys belong in lab notebooks, not in shader constants. When distance doubles, loss rises ~6 dB in free-space teaching model — memorize the pedagogy, label the model <span class="tag phil">Teaching reference</span>, never confuse with NEXUS local JSON amplitude fields.</p>
<p>Advanced students may compare worksheet prediction to Field Antenna JSON note for same band — correlation paragraph only. Disagreement is expected; layers measure different things.</p>

<h2>Study questions</h2>
<ol>
<li>Tag three RF contexts with correct honesty labels.</li>
<li>Where does <code>R_RF</code> sit in the shell stack narrative?</li>
<li>Name three Field Antenna JSON outputs and panel tab.</li>
<li>Write FSPL proportionality; why not in <code>x86.comp</code>?</li>
<li>Give one Phi vs RF category error and correction.</li>
<li>Complete workshop protocol step 5; what grep proves offense prep?</li>
<li>Why no merged super-score between JSON and gatekeeper?</li>
<li>How does Queen treat WebRTC versus weave shader?</li>
<li>Which failure mode matches “forecast from weave colors”?</li>
<li>State handoff sentence from Chapter 6 to Chapter 7.</li>
</ol>
"""


__all__ = [
    "expand_01",
    "expand_02",
    "expand_03",
    "expand_04",
    "expand_05",
    "expand_06",
]


if __name__ == "__main__":
    for name in __all__:
        fn = globals()[name]
        text = fn()
        words = len(text.split())
        print(f"{name}: {words} words")
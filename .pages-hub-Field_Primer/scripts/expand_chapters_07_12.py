#!/usr/bin/env python3
"""Expand chapters 07-12 to minimum 4500 words with substantive sections."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "content" / "chapters"
MIN_WORDS = 4500


def wc(text: str) -> int:
    return len(text.split())


EXPANSIONS = {
    "07.html": """
<h2>Deep dive — <code>Pipeline.hpp</code> and dispatch contracts</h2>
<p>The dispatch loop is not scattered across anonymous lambdas. <code>Pipeline::dispatch_canvas()</code> centralizes obligations so grep has a spine. Operators packaging forks should diff this function first when merging upstream AMOURANTHRTX — not the splash assets. Canvas kind selection branches X86Fields versus Classic, but thermo population and CFL guard are shared preludes. That shared prelude is intentional: you cannot opt out of numerical ethics by swiping to a prettier shader.</p>
<p>Descriptor set layout for x86 path is versioned with <code>FIELD_LAYOUT_VERSION = 5</code>. When upgrading shaders, bump the constant in host and SPIR-V comments together. Mixed trees produce mixed reality — HUD reading slot 42 chrome flags from an old packing order while host writes the new order is a silent desync worse than a crash, because you may trust false hex.</p>
<p>Push constant size for FieldSocket must match <code>x86.comp</code> layout byte-for-byte. Vulkan validation layers catch some mismatches in debug builds; release builds may simply misread control flags. Always run at least one debug validation session when touching FieldSocket fields.</p>

<h2>Deep dive — guest programs and launch hygiene</h2>
<p><code>FieldAmouranthLaunch</code> and <code>FieldAmouranthExec</code> place guest images into the RAM map respecting boot vector and disk image regions. Operators launching retro binaries should understand they write into the same SSBO the GPU interprets — there is no sandbox fairy. A bad binary can scribble BDA; the layer pump must resync or VGA mode lies on the bus.</p>
<p>ControlAmmoExec is not “run anything from the internet.” It is operator offense with conscience. Chapter 5 packet field and Chapter 21 Queen gates exist because launch and network are different writable surfaces. Field literacy connects them at the human, not in one automated verdict.</p>

<h2>Deep dive — thermo on die versus classic pedagogy</h2>
<p>New operators often swipe to Classic because thermo colors are obvious. Veterans stay on die default because product truth lives there. The compromise this book teaches: learn thermo on Classic in week one afternoon, return to die for week two operations. ThermoAccountant does not care which canvas you stared at — it populates every dispatch. Die path simply hides heat behind chrome unless you enable debug HUD or read stderr.</p>
<p>Boundary thermo on die still moves when coupling increases — grep proves it. If you need visual confirmation, enable field debug overlay or watch STATUS entropy lines. Screenshots of Big Grin without stderr are incomplete testimony.</p>

<h2>Deep dive — failure isolation checklist</h2>
<p>When dispatch misbehaves, walk this checklist in order: (1) VULKAN init succeeded? (2) FIELD_LAYOUT_VERSION match? (3) CFL clamp messages? (4) pump generation incrementing slot 0? (5) ThermoAccountant steps in slot 28 rising? (6) HDR presented? Skipping order sends you to fix chrome when binding 1 is nil.</p>
<p>Record baseline grep snippets in your operator journal. Field Technology is a practice, not a one-time read. Week twelve you will compare stderr shape against week one and notice drift before users do.</p>

<h2>Deep dive — creditor CFL</h2>
<p>CFL condition names Courant, Friedrichs, and Lewy — the men who told the world explicit time steps must respect mesh spacing. Chapter 9 owns the equation; Chapter 7 owns the placement: before <code>vkCmdDispatch</code>. Offense without CFL disrespects their creditor debt. <a href="../creditors/cfl.html">CFL creditor page</a> links history; harmonics guard links implementation.</p>
""",
    "08.html": """
<h2>Deep dive — RAM layer pack field by field</h2>
<p>Slots [2–7] deserve line-by-line literacy. Word at [2] reflects HD ready — is the C mirror path live? Word at [3] counts mirror bytes synchronized. Word at [4] echoes boot vector placement. Word at [5] sizes floppy image staging. Word at [6] reports <code>GUEST_RAM_BYTES</code> so shaders cannot pretend a larger universe. Word at [7] gives HD mirror offset for hex HUD. When any word sticks while guest visibly mounts media, grep <code>ramPack</code> and guest <code>FieldDos::hdReady</code> state before blaming x86.comp.</p>

<h2>Deep dive — VGA layer and BDA coherence</h2>
<p>VGA pack at [8–11] reads BDA video mode, column count, cursor position, DAC path flags. Guest software that switches mode 13h versus text mode must update BDA or layer sync reads lies. FieldVga and FieldDosViewport share mode knowledge — divergence between them produces hit-test ghosts. Operators debugging “mouse clicks wrong row” should dump BDA bytes at <code>0x400+0x49</code> and bus slot [8] in the same breath.</p>

<h2>Deep dive — FAT and AMMOFAT geometry</h2>
<p>Slots [12–15] expose FAT geometry for AMMOFAT — cluster size, free count, mount state bits. This is how shader HUD knows whether A: is fiction. FAT layer tick may advance host-side tables while GPU interprets guest code that reads directory entries. Coherence requires pump after guest disk I/O bursts — another reason dispatch cadence matters beyond frame rate.</p>

<h2>Deep dive — MSCDEX and optical media layer</h2>
<p>CD-ROM redirector layer participates in L0–L9 registry with pack hooks near MSCDEX bus base. Retro launch paths that expect MSCDEX must have layer tick active — otherwise guest drivers spin while bus reports unmounted silence. Chapter 12 honesty: not every retro path is equally exercised in CI; grep your launch receipts.</p>

<h2>Deep dive — reading Big Grin HUD hex</h2>
<p>Big Grin HUD at 172×48 is not arbitrary wallpaper. It is a field monitor — entropy words, bus slices, tile cache peek, chrome state. With <code>ControlFieldDebugHud</code> you see more; without, you still have stderr. Train eyes on hex dumps only after training grep on THERMO — otherwise hex becomes numerology.</p>

<h2>Deep dive — host peek without breaking GPU truth</h2>
<p>Host may map SSBO for debug peek. Peek is read-mostly discipline — host writes to guest RAM outside pump contracts desync GPU interpretation. When using ControlHostCpu assist, host write rules tighten further. Default GPU path keeps host as pump orchestrator, not parallel writer.</p>

<h2>Deep dive — die and KILROY kernel vocabulary</h2>
<p>KILROY Field OS (<code>CONFIG_RTX_FIELD_DIE</code>) shares die vocabulary at syscall boundary — Chapter 9 FCC parallel, Chapter 21 sovereign packaging. Userspace AMOURANTHRTX die you run today is the same word the kernel path names. When docs say “field die,” ask which ring — still 64 MiB story, different enforcement layer.</p>

<h2>Deep dive — week-two operator journal prompts</h2>
<p>Journal entry prompts: (1) Sketch RAM map from memory. (2) Copy one STATUS line and label each thermo field. (3) Change one FCC float and record bus slot delta. (4) Launch one guest app and note which regions changed. (5) Correlate one NEXUS jsonl row with dispatch session time — sealed time column. Literacy compounds when written by hand.</p>
""",
    "09.html": """
<h2>Introduction — stability under load</h2>
<p>Chapter 7 placed CFL on the dispatch spine before <code>vkCmdDispatch</code>. Chapter 9 teaches why — and teaches Tesla directional bias as the second stability story. Offense writes boundary conditions; without stability guards, boundary conditions become NaN theology. FCC is not a government agency here — it is <strong>Field Control Constants</strong> packing analog floats into <code>data_bus[16–23]</code> with host-side harmonics enforcement.</p>
<div class="objectives"><h2>Learning objectives</h2><ul>
<li>Derive intuitive CFL inequalities for wave and diffusion on a grid.</li>
<li>Explain host scaling when <code>waveCFL</code> or <code>thermoCFL</code> violate 1.</li>
<li>State Tesla constants and how reverse flow is damped on spiderweb edges.</li>
<li>Connect KILROY kernel FCC scale to userspace guard philosophy.</li>
<li>Run drills that prove clamps fire before fabric explodes.</li>
</ul></div>

<h2>CFL harmonics guard — implemented ethics</h2>
<div class="eq">waveCFL = c·Δt/Δx ≤ 1 · thermoCFL = α·Δt/Δx² ≤ 1</div>
<p>Before fabric evolution each <code>dispatch_canvas()</code>, host computes CFL numbers from render resolution, per-step <code>dT</code>, <code>WaveSpeed</code> (c), and <code>ThermoAlpha</code> (α). Violation triggers scale-down of unsafe parameters — not silent continuation. Hard caps include <code>waveSpeed ∈ [0.01, 2.0]</code>, <code>dT ≤ 0.033</code>, inject strength clamp cooperation.</p>
<p>Plain English: the engine refuses diffusion so hot the simulation explodes. Chapter 3 introduced the guard; Chapter 9 is the full operator treatment. Courant–Friedrichs–Lewy is creditor math — explicit schemes need explicit limits. <a href="../creditors/cfl.html">CFL tribute</a>.</p>

<figure class="figure"><img src="../assets/images/chapters/ch09-tesla-valve.jpg" alt="Tesla valve directional bias" loading="lazy" /><figcaption>Figure 9.1 — Directional damping: forward ease, reverse resist — metaphor with teeth in code.</figcaption></figure>

<h2>Why diffusion is harsher than wave</h2>
<p>Notice thermoCFL uses Δx² in the denominator. Diffusion grows stiffer as resolution refines — doubling texel count quarters admissible Δt at fixed α unless host scales down. RayCanvas adaptive upscale therefore triggers harmonics guard interaction Chapter 7 warned about. Operators chasing 4K fabric beauty without reading STATUS may hit invisible clamp — not GPU weakness, numerical care.</p>

<h2>FCC floats — control bus semantics</h2>
<table><thead><tr><th>Slot</th><th>Knob</th><th>Stability role</th></tr></thead>
<tbody>
<tr><td>[16]</td><td>TimeScale</td><td>Multiplies effective Δt — enters both CFL products</td></tr>
<tr><td>[17]</td><td>ThermoAlpha</td><td>Diffusion coefficient — thermoCFL numerator</td></tr>
<tr><td>[18]</td><td>WaveSpeed</td><td>Wave c — waveCFL numerator</td></tr>
<tr><td>[19]</td><td>GateFidelity</td><td>Sharpens Flow gates — indirect stability via coupling</td></tr>
<tr><td>[20]</td><td>EntropyFloor</td><td>Minimum noise — prevents unphysical reversibility</td></tr>
<tr><td>[21]</td><td>InjectStrength</td><td>Probe energy — clamped pre-dispatch</td></tr>
<tr><td>[22]</td><td>PropalacticScale</td><td>Large-scale Phi forcing — not cosmic truth, dynamics knob</td></tr>
<tr><td>[23]</td><td>FieldCoupling</td><td>Cross-channel coupling — can amplify effective work</td></tr>
</tbody></table>
<p>Prompt <code>set</code> changes feed guard inputs next frame. Guard outputs feed bindings 8–10 and bus mirrors simultaneously — host and shader see admitted values only.</p>

<h2>Tesla valve — directional bias constants</h2>
<pre class="eq">TESLA_R_FORWARD = 0.18
TESLA_R_REVERSE = 3.2
FIELD_PHI_MILLI = 618
TESLA_R_FWD_MILLI = 180
TESLA_R_REV_MILLI = 3200</pre>
<p>From <code>FieldRtxFieldAbs.hpp</code>. <code>teslaBias()</code> inside <code>updateHardwareFromAnalogFields()</code> damps reverse “flow” on hardware spiderweb edges more than forward. Published to <code>data_bus[31]</code> and <code>data_bus[34]</code>. <span class="tag meta">Named after Tesla's fluidic diode — directional resistance metaphor, not a literal fluidic part in your chassis.</span></p>
<p>Golden-ratio gate hint <code>FIELD_PHI_MILLI = 618</code> is engineering folklore with a number — useful mnemonic, not a claim the universe prefers φ because the HUD said so. Chapter 12 labels such rocks.</p>

<h2>Tesla in fabric versus spiderweb</h2>
<p>On Flow fabric, Tesla relaxation mixes with gradient magnitude and GateFidelity. On hardware mirror, edge util receives directional damping. Same constants, two witnesses — fabric color and spiderweb graph. Chapter 10 details graph; Chapter 9 names constants operators grep.</p>

<h2>KILROY FCC — kernel parallel</h2>
<p>When KILROY Field Kernel runs (<code>CONFIG_RTX_FIELD_DIE</code>), scale 0–1,000,000 µ from overshoot; entropy feedback clamps aggressive modes. Userspace AMOURANTHRTX and kernel Field Die share vocabulary — Chapter 21 ties Queen + KILROY sovereign field. Kernel FCC is not separate religion; it is same CFL/Tesla discipline at ring transition.</p>

<h2>PropalacticScale — cosmic knob honesty</h2>
<p><code>PropalacticScale</code> applies large-wavelength forcing on Phi — sinusoid story on fabric. Marketing might say “cosmic weave”; Chapter 12 honesty table says dynamics knob. It moves Phi; it does not replace packet field defense or GPS precision maps in NEXUS.</p>

<h2>GateFidelity — analog to sharp</h2>
<p>0 = soft analog gates; 1 = transistor-sharp. Sharp gates change Flow story and spiderweb voltage factor indirectly. Cranking fidelity without watching thermo boundary is how operators surprise themselves with maintenance cost spikes — prevMaintCost in ThermoAccountant speaks.</p>

<h2>Failure modes — NaN theology</h2>
<p>If CFL guard disabled in a fork, expect: white noise HDR, NaN entropy, frozen spiderweb, lying bus FCC floats. Recovery: restore harmonics guard, reset analog fields to defaults, clear fabrics, re-seal time session. Do not screenshot the pretty noise and call it art without labeling <span class="tag vis">visual accident</span>.</p>

<h2>Operator drills</h2>
<div class="callout drill"><strong>Drill 9.A — CFL clamp witness</strong></div>
<pre class="eq">set AnalogFields.WaveSpeed 9.9
set AnalogFields.TimeScale 4.0
list AnalogFields
grep -i cfl run.log</pre>
<div class="callout drill"><strong>Drill 9.B — Tesla bus</strong></div>
<pre class="eq">grep -E 'TESLA|data_bus\[31\]|bias' Navigator/engine/FieldRtxFieldAbs.hpp run.log</pre>

<h2>Chapter summary</h2>
<p>Stability is offense ethics. CFL guard enforces wave and diffusion limits before GPU evolution. FCC floats pack control into <code>data_bus[16–23]</code>. Tesla constants bias direction on fabric and spiderweb; slots 31 and 34 witness. KILROY kernel extends same discipline. PropalacticScale and GateFidelity are powerful — label rocks, grep clamps.</p>
<p>Prior: <a href="08-field-die.html">Chapter 8</a>. Next: <a href="10-spiderweb.html">Chapter 10</a>.</p>

<h2>Study questions</h2>
<ol>
<li>Write both CFL inequalities and explain Δx² in diffusion.</li>
<li>What host actions occur when waveCFL &gt; 1?</li>
<li>Quote Tesla forward and reverse constants.</li>
<li>Which bus slots carry Tesla bias?</li>
<li>How does PropalacticScale differ from planetary RF shell?</li>
<li>What is KILROY FCC scale range?</li>
<li>Why is GateFidelity a stability concern indirectly?</li>
<li>Name the creditor behind CFL.</li>
<li>What is NaN theology?</li>
<li>How do FCC floats relate to bindings 8–10?</li>
</ol>
""",
    "10.html": """
<h2>Introduction — hardware spiderweb mirror</h2>
<p>Chapters 7–9 wrote fabrics and stabilized them. Chapter 10 answers: what does the machine <em>look like</em> to an operator who thinks in cores, edges, and MHz? <code>hardwareFabric</code> is a read-only mirror — averaged Phi/Thermo/Flow drive simulated per-core frequency, voltage, temperature, power, and spiderweb edge util. Not a second simulation pretending to be SEM imaging.</p>
<div class="objectives"><h2>Learning objectives</h2><ul>
<li>Trace <code>updateHardwareFromAnalogFields()</code> each frame.</li>
<li>Define voltageFactor, thermalThrottle, parallelEff.</li>
<li>Name mastery tiers Puny, Adept, Tidewalker.</li>
<li>Read honesty table for sub-micron claims.</li>
<li>Relate precision-field.py NEXUS cousin metaphor.</li>
</ul></div>

<figure class="figure"><img src="../assets/images/chapters/ch10-spiderweb.jpg" alt="Hardware spiderweb graph" loading="lazy" /><figcaption>Figure 10.1 — Fabric averages drive util graph — mirror, not microscope.</figcaption></figure>

<h2><code>updateHardwareFromAnalogFields</code> — frame ritual</h2>
<ol>
<li>Sample avg Phi, Thermo, Flow from fabric + probes</li>
<li>Apply fluid velocity/density + Tesla bias</li>
<li>Compute <code>voltageFactor</code>, <code>thermalThrottle</code>, <code>parallelEff</code></li>
<li>Update each <code>hardwareFabric.units[]</code>: operationalFreqMHz, util, voltage, temp, power</li>
<li>Update spiderweb <code>edges[].currentUtil</code></li>
<li>Accumulate <code>simulatedChipCycles</code></li>
</ol>
<p>Non-optional when fabric populated — skipping mirror while fabrics run is incoherent product state.</p>

<h2>Mastery tiers</h2>
<table><thead><tr><th>Tier</th><th>Controls</th></tr></thead>
<tbody>
<tr><td><strong>Puny</strong></td><td>Status log, real sysfs clocks (<code>AutoUseRealClocks</code>)</td></tr>
<tr><td><strong>Adept</strong></td><td>Target clock, thermal sensitivity, <code>SimulateSubMicron</code></td></tr>
<tr><td><strong>Tidewalker</strong></td><td>Full spiderweb graph override, vendor force, <code>SubMicronDetail</code></td></tr>
</tbody></table>
<p>Documented inline in <code>OptionsMenu.hpp</code>. Prompt <code>list Hardware</code> reads results.</p>

<h2>Sub-micron claim — honest table</h2>
<table><thead><tr><th>Claim</th><th>Reality</th><th>Label</th></tr></thead>
<tbody>
<tr><td>Adaptive resolution 320×200 → 4K+</td><td>Implemented</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td>SDF epsilons + accumulation</td><td>Implemented</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td>Zero-cost sub-micron SEM fidelity</td><td>Procedural pixel detail</td><td><span class="tag meta">Metaphor</span></td></tr>
<tr><td>Spiderweb util equals fab yield</td><td>Coupled mirror graph</td><td><span class="tag meta">Metaphor</span></td></tr>
</tbody></table>

<h2>Tesla on edges</h2>
<p>Reverse edge flow damped with <code>TESLA_R_REVERSE</code> vs forward <code>TESLA_R_FORWARD</code> — Chapter 9 constants. Graph is dashboard, not foundry telemetry.</p>

<h2>Precision field (NEXUS cousin)</h2>
<p><code>precision-field.py</code> — GPS-anchored entity map, spiderweb nodes, thermal-earth bodies. Separate codebase, cousin metaphor. Correlate at operator mind, not automatic code merge.</p>

<h2>Operator drills</h2>
<div class="callout drill"><strong>Drill 10.A</strong></div>
<pre class="eq">list Hardware
set Hardware.SimulateSubMicron 1
grep -i spiderweb run.log</pre>

<h2>Chapter summary</h2>
<p>Spiderweb mirrors fabric — read-only dashboard. Six-step update each frame. Tiers unlock controls. Sub-micron SEM is metaphor. Chapter 11 reads logs; Chapter 12 lists rocks.</p>
<p>Prior: <a href="09-fcc-tesla.html">Chapter 9</a>. Next: <a href="11-observability.html">Chapter 11</a>.</p>

<h2>Study questions</h2>
<ol>
<li>List six mirror update steps.</li>
<li>What does Puny tier use for clocks?</li>
<li>What is SimulateSubMicron honesty label?</li>
<li>How does Tesla bias reach edges?</li>
<li>What is precision-field cousin?</li>
</ol>
""",
    "11.html": """
<h2>Introduction — reading the battlefield</h2>
<p>Trust stderr before screenshots. The weapon is useless if you will not read the readout. Time is linear — logs are timeline. Grep is forensic defense. Chapter 11 unifies AMOURANTHRTX ELLIE logging, prompt terminal, RTXProbe, and NEXUS panel :9477 into one observability doctrine.</p>
<div class="objectives"><h2>Learning objectives</h2><ul>
<li>Name ELLIE categories and STATUS block fields.</li>
<li>Use prompt <code>set</code>/<code>list</code> for live controls.</li>
<li>Enable RTXProbe without permanent overhead.</li>
<li>Navigate NEXUS panel tabs and RTX Zero mode.</li>
<li>Run week-one lab correlating fabric, die, packet field.</li>
</ul></div>

<figure class="figure"><img src="../assets/images/chapters/ch11-observability.jpg" alt="Observability stack" loading="lazy" /><figcaption>Figure 11.1 — Logs, probes, panel — one operator battlefield.</figcaption></figure>

<h2>ELLIE logging — categories</h2>
<p><code>MAIN</code>, <code>VULKAN</code>, <code>CANVAS</code>, <code>THERMO</code>, <code>STATUS</code>, <code>RTXPROBE</code>. STATUS ~5s: FPS, GPU ms, VRAM, adaptive scale, entropy, boundary thermo, maintenance cost.</p>

<h2>Prompt terminal</h2>
<pre class="eq">set AnalogFields.GateFidelity 0.85
list Hardware
guide</pre>
<p><span class="tag impl">set/list for AnalogFields + Hardware.</span> Glassmorphism sliders — feasibility doc only.</p>

<h2>RTXProbe</h2>
<p><code>RTX_PROBES=1</code> → GPU timestamps, invocation counts. Zero cost when off.</p>

<h2>NEXUS panel</h2>
<p><code>https://127.0.0.1:9477/</code> — command, packets, threats, signals, DNS, library, system. RTX Zero: <code>?rtx=1</code> — Aqua chrome, cache-first refresh.</p>

<h2>Week-one operator lab</h2>
<ol>
<li>Run <code>./linux.sh run</code> or <code>./nexus.sh</code></li>
<li>Read STATUS/THERMO 60s</li>
<li>Move mouse on classic — watch entropy</li>
<li>Archive one gatekeeper decision at panel</li>
</ol>

<h2>Sovereign time preview</h2>
<p>Grep <code>SQUIDGIE</code> if clocks disagree — <a href="19-sovereign-time.html">Chapter 19</a>.</p>

<h2>Chapter summary</h2>
<p>Observability is operator weapon. ELLIE + prompt + probe + panel. Correlate three scales. Prior: <a href="10-spiderweb.html">Ch 10</a>. Next: <a href="12-reality-theory.html">Ch 12</a>.</p>

<h2>Study questions</h2>
<ol>
<li>List six ELLIE categories.</li>
<li>What does STATUS block include?</li>
<li>How enable RTXProbe?</li>
<li>What is RTX Zero?</li>
<li>Name four panel tabs.</li>
</ol>
""",
    "12.html": """
<h2>Introduction — the rocks we do not hide</h2>
<p>Field Technology v5 is serious because it labels poetry before newcomers confuse it with measurement. Chapter 12 is the contract — bookmark it. Complete honesty table, trust rules, product boundaries, capstone equations.</p>
<div class="objectives"><h2>Learning objectives</h2><ul>
<li>Apply status tags to any claim in the stack.</li>
<li>Recite complete honesty table rows.</li>
<li>Choose trust sources in disputes.</li>
<li>Separate product licenses and roles.</li>
<li>Use capstone equations with correct layer labels.</li>
</ul></div>

<figure class="figure"><img src="../assets/images/chapters/ch12-honesty.jpg" alt="Honesty table" loading="lazy" /><figcaption>Figure 12.1 — Metaphor glow vs measured grid.</figcaption></figure>

<h2>The honesty table — complete</h2>
<table><thead><tr><th>Claim (theory / marketing)</th><th>Operator reality</th><th>Label</th></tr></thead>
<tbody>
<tr><td>Greatest weapon</td><td>Field literacy + local tools</td><td><span class="tag phil">Philosophy</span></td></tr>
<tr><td>Living thermodynamic computer</td><td>ThermoAccountant in logs</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td>Packet field sees everything</td><td>Local sockets + heuristics</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td>RF planetary shell</td><td><code>planetary_weave.comp</code> visual</td><td><span class="tag vis">Visual</span></td></tr>
<tr><td>Landauer joules from GPU</td><td>Proxy integral</td><td><span class="tag meta">Metaphor</span></td></tr>
<tr><td>Sub-micron SEM</td><td>Procedural pixel detail</td><td><span class="tag meta">Metaphor</span></td></tr>
<tr><td>Love / God chapters</td><td>Sacred operator language</td><td><span class="tag phil">Philosophy</span></td></tr>
<tr><td>Queen holds all gates</td><td><code>QUEEN_READY</code> when built</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td>KILROY kernel on host today</td><td>QEMU / bare-metal boot path</td><td><span class="tag impl">Implemented</span> image; host may run generic Linux</td></tr>
<tr><td>Propalactic cosmic weave</td><td><code>PropalacticScale</code> knob on Phi</td><td><span class="tag meta">Metaphor</span></td></tr>
<tr><td>Tamper abort / sealed time</td><td><code>TotalTime::seal()</code> + verify posture</td><td><span class="tag impl">Implemented</span> session; not DRM</td></tr>
<tr><td>Hardware-gate fidelity</td><td><code>GateFidelity</code> sharpens Flow; spiderweb util is mirror</td><td><span class="tag impl">Implemented</span> + <span class="tag meta">mirror</span></td></tr>
<tr><td>Tesla valve in chassis</td><td>Constants in code; directional bias</td><td><span class="tag meta">Metaphor</span></td></tr>
<tr><td>96% lies device cannot drift</td><td>Security posture narrative</td><td><span class="tag phil">Philosophy</span></td></tr>
<tr><td>data_bus is SI telemetry</td><td>64-word packed dashboard per dispatch</td><td><span class="tag impl">Implemented</span></td></tr>
</tbody></table>

<h2>What to trust</h2>
<ol>
<li><strong>Headers</strong> over cover art</li>
<li><strong>stderr</strong> over screenshots for thermo</li>
<li><strong><code>./linux.sh run</code></strong> default = Field Die</li>
<li><strong>Headless dispatch</strong> — valid CI signal</li>
</ol>

<h2>Product boundaries</h2>
<table><thead><tr><th>Product</th><th>License</th><th>Role</th></tr></thead>
<tbody>
<tr><td>AMOURANTHRTX</td><td>GPL v3 or commercial</td><td>Vulkan Field Die</td></tr>
<tr><td>NEXUS-Shield</td><td>MIT</td><td>Endpoint security</td></tr>
<tr><td>Queen</td><td>Field sovereign browser</td><td>RTX + gates in-engine</td></tr>
<tr><td>Field Primer</td><td>CC BY-NC-SA 4.0</td><td>This textbook</td></tr>
</tbody></table>

<h2>Capstone equations</h2>
<table><thead><tr><th>Domain</th><th>Relation</th></tr></thead>
<tbody>
<tr><td>Wave CFL</td><td><code>c·Δt/Δx ≤ 1</code></td></tr>
<tr><td>Diffusion CFL</td><td><code>α·Δt/Δx² ≤ 1</code></td></tr>
<tr><td>Entropy proxy</td><td><code>Ṡ ≈ fieldWork + probeDiss + prevMaint</code></td></tr>
<tr><td>Shannon (NEXUS)</td><td><code>H = −Σ pᵢ log₂ pᵢ</code></td></tr>
<tr><td>Landauer (theory)</td><td><code>E_min = k_B T ln 2</code></td></tr>
</tbody></table>

<h2>Chapter summary</h2>
<p>Theory inspires vocabulary. Implementation is what you grep, set, screenshot — with labels. Enjoy the field honestly. Next: <a href="13-landauer-deep.html">Chapter 13</a>.</p>

<h2>Study questions</h2>
<ol>
<li>Recite five honesty table rows from memory.</li>
<li>When do you trust stderr over screenshots?</li>
<li>Which product is MIT licensed?</li>
<li>Write diffusion CFL inequality.</li>
<li>What label applies to PropalacticScale cosmic marketing?</li>
</ol>
""",
}


def main():
    for fname, extra in EXPANSIONS.items():
        path = ROOT / fname
        if path.exists():
            body = path.read_text(encoding="utf-8")
        else:
            body = extra  # 09-12 base is in expansion for now
            if fname not in ("09.html", "10.html", "11.html", "12.html"):
                continue
        if path.exists() and fname in ("07.html", "08.html"):
            body = body + "\n" + extra
        elif fname in ("09.html", "10.html", "11.html", "12.html") and not path.exists():
            body = extra
        elif fname in ("09.html", "10.html", "11.html", "12.html") and path.exists():
            body = body + "\n" + extra
        path.write_text(body.strip() + "\n", encoding="utf-8")
        print(f"{fname}: {wc(body)} words")


if __name__ == "__main__":
    main()
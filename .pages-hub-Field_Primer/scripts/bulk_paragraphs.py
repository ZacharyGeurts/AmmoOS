"""Bulk paragraph banks for chapter generation — substantive textbook prose."""


def paras(*texts: str) -> str:
    return "\n".join(f"<p>{t}</p>" for t in texts)


def bulk_ch01_extra() -> str:
    sections = []
    sections.append(
        "<h2>Holographic boundary — where rendering pays cost</h2>"
        + paras(
            "The holographic boundary in this stack is where HDR frame pairs meet analog fabric — where beauty costs heat in ThermoAccountant receipts, where existence becomes visible to the operator eye. Chapter 17 names God at that boundary as philosophy. Chapter 1 names it as engineering fact: every presented frame that evolved fabric texels left a trace in proxy entropy unless dispatch failed.",
            "Operators who screenshot without grepping mistake the boundary for decoration. The boundary is the invoice. Not joules from a wattmeter — <span class=\"tag meta\">proxy integral</span> — but an honest invoice nonetheless. When entropy reads zero while fabric moves, physics refuses to lie for you; the dispatch path failed.",
            "Queen browser inherits the same boundary when WebGL and WebGPU contexts accrue thermo per context (Chapter 21). Browser tabs are not outside field theory; they are another writable surface held behind gates.",
        )
    )
    sections.append(
        "<h2>ThermoAccountant — preview from Chapter 4</h2>"
        + paras(
            "Vulkan binding <strong>2</strong> carries ThermoAccountant — populated every <code>dispatch_canvas()</code>. Fields include <code>entropyThisFrame</code>, <code>avgBoundaryThermo</code>, <code>prevMaintCost</code>, <code>freeEnergyIncome</code>, <code>steps</code>. Mirrored to <code>data_bus[24–28]</code> for HUD and grep.",
            "<pre class=\"eq\">entropyThisFrame — Landauer proxy + field work + probes\navgBoundaryThermo — mean boundary temperature / entropy density\nprevMaintCost — coherence with previous frame</pre>",
            "<span class=\"tag meta\"><strong>Rock:</strong> entropyThisFrame is proxy — field work + probe dissipation + maintenance. Not joules from nvidia-smi.</span> Chapter 4 and Chapter 13 go deeper. Preface plants the label so newcomers do not bill the power company from stderr.",
        )
    )
    sections.append(
        "<h2>Sealed time — preview from Chapter 19</h2>"
        + paras(
            "<code>TotalTime::seal()</code> locks session genesis into <code>FieldSocket::sealed_time</code>. Frame-rate jitter cannot rewrite physics time. Sovereign time extends seal-forward and verify-at-receive across hosts with HMAC pulses and <code>SQUIDGIE</code> verdicts.",
            "Time is linear is not nostalgia for log files. It is refusal to let adversaries squidgie clocks — nudge RTC, desync GPS sub-micron nodes, desync thermo correlation — without a grep-able verdict.",
        )
    )
    sections.append(
        "<h2>Packet field and Queen — defensive perimeter preview</h2>"
        + paras(
            "NEXUS Connection Gatekeeper: ten-axis scoring → USER_OK, EPHEMERAL, SUSPICIOUS, HARM_CANDIDATE. <span class=\"tag impl\">Implemented.</span> <span class=\"tag phil\">94/6 truth filter</span> — watchlist before block; KILL permanent and archived.",
            "Queen holds all gates — WebRTC through gatekeeper, MP4 mandatory in-tree, EME held not omitted. Wrong posture disables capabilities; right posture receipts every wire exit. Chapter 5 and Chapter 21 own the full treatment.",
            "Packet field is local only — your sockets, your habits, your jsonl. It does not see the whole internet. Planetary weave RF shell is <span class=\"tag vis\">Visual</span> only — Chapter 6.",
        )
    )
    sections.append(
        "<h2>Reading headers versus reading chapters</h2>"
        + paras(
            "This manual is not a substitute for <code>Pipeline.hpp</code>, <code>FieldRtxFieldAbs.hpp</code>, or NEXUS lib sources. Headers win arguments about what compiles. Chapters win arguments about what mistakes will hurt you in week six.",
            "Pedagogy order: preface labels → Chapter 2 addresses → Chapter 3 thermo → Chapter 4 entropy layers → Chapter 5 defense → Chapter 7 dispatch → Chapter 12 rocks. Skipping to Chapter 21 Queen gates without Chapter 5 packet field is how operators enable WebRTC without gatekeeper discipline.",
            "Wiki pages are quick reference. These chapters are the long sit-down. Both must agree; when they disagree, headers and stderr adjudicate.",
        )
    )
    sections.append(
        "<h2>Field Primer license and teaching covenant</h2>"
        + paras(
            "Field Primer is CC BY-NC-SA 4.0 — teach freely with rocks visible. AMOURANTHRTX is GPL v3 or commercial. NEXUS-Shield is MIT. Queen and KILROY carry sovereign packaging described in Chapter 21.",
            "Chapter 18 Operator Covenant long form: teach freely, build locally, honor creditors, bring love, name God without letting poetry pretend calorimetry, hold gates. Preface introduces the covenant; Chapter 18 signs it in spirit.",
        )
    )
    sections.append(
        "<h2>Newcomer FAQ — honest answers</h2>"
        + paras(
            "<strong>Is this a game engine?</strong> It is a Field Die engine that can present like a game. Default run is guest RAM on GPU, not a postcard raymarch.",
            "<strong>Is NEXUS cloud AV?</strong> No. Local-first endpoint security with jsonl memory on your machine.",
            "<strong>Does planetary weave measure RF?</strong> No. <span class=\"tag vis\">Visual</span> vocabulary only.",
            "<strong>Are thermo numbers joules?</strong> No. <span class=\"tag meta\">Proxy</span> comparative receipts.",
            "<strong>Does packet field see the world?</strong> No. Local sockets and heuristics only.",
        )
    )
    sections.append(
        "<h2>Integration roadmap — Chapters 2 through 6</h2>"
        + paras(
            "Chapter 2 maps three dimensions of state — scalar Phi/Thermo, vector Flow gradients, telemetry <code>data_bus[64]</code>. Scale 1 GPU fabric, scale 2 Field Die, scale 3 packet field — one operator panel correlates without collapsing metrics.",
            "Chapter 3 moves energy through coupled channels — <code>FieldCoupling</code>, CFL guards, <code>AnalogFields</code> knobs. Chapter 4 separates ThermoAccountant, entropy floor, Shannon oracle — same word, different layers.",
            "Chapter 5 defends perimeter — TX/RX contracts, corroboration, field memory. Chapter 6 separates three RF meanings — planetary weave visual, NEXUS Field Antenna implemented, Phi gate potential implemented.",
            "Read in order once. Return to Chapter 12 when marketing sells cosmology.",
        )
    )
    return "\n\n".join(sections)


def bulk_ch02() -> str:
    return r"""
<div class="objectives">
<h2>Learning objectives</h2>
<ol>
<li>Map Reality is 3D to fabric texels, die bytes, and packet positions.</li>
<li>Distinguish scalar, vector, and telemetry fields with stack examples.</li>
<li>Trace GPU fabric, Field Die, and packet field paths without category errors.</li>
<li>Explain why the host never runs a CPU PDE on analog fabric.</li>
<li>Correlate three scales at the operator panel without collapsing metrics.</li>
<li>Identify integration via <code>data_bus[64]</code>, <code>hardwareFabric</code>, and jsonl.</li>
</ol>
</div>

<h2>Introduction — three dimensions of state</h2>
<p>Chapter 2 maps <strong>three dimensions of state</strong> — our reading of “Reality is 3D.” This is not cosmology. It is the minimum honest map for texels, die bytes, and packet sentences occupying space you can address, read, and write.</p>
<p>Most rendering textbooks stop at pixels. Most security textbooks stop at packets. Field Technology refuses the split: offense and defense are the same literacy applied to different writable surfaces. If you cannot name the address, you cannot defend it. If you cannot predict neighbor response, you cannot dispatch responsibly.</p>
<p>Chapter 1 named three field families. This chapter names three <em>mathematical postures</em> toward those families — scalar, vector, telemetry — and three <em>physical scales</em> — GPU fabric, Field Die, packet field. Integration is not marketing glue; it is how one human at :9477 correlates stderr, bus words, and jsonl without letting a vendor collapse them into one misleading score.</p>

<h2>Scalar, vector, and telemetry — mathematical postures</h2>
<table><thead><tr><th>Type</th><th>Stack example</th><th>What each cell carries</th></tr></thead>
<tbody>
<tr><td><strong>Scalar field</strong></td><td>Thermo (binding 9)</td><td>One heat/entropy density per texel</td></tr>
<tr><td><strong>Vector field</strong></td><td>Flow <code>.gb</code> (binding 10)</td><td>Gradient components per texel</td></tr>
<tr><td><strong>Telemetry field</strong></td><td><code>data_bus[64]</code></td><td>Sixty-four packed words per dispatch</td></tr>
</tbody></table>
<p>A scalar tells how hot a cell is. A vector tells which direction activity tends. Telemetry tells what shader and host agree happened this tick — the spine the operator greps. Phi can be read as scalar potential per texel on binding 8; Flow's vector structure is where advection stories live.</p>
<div class="callout science"><strong>Do not</strong> treat telemetry as a spatial grid. <code>data_bus</code> is a dashboard vector, not a second fabric. Category errors here produce dashboards that lie about dimensionality.</div>

<h3>Phi as potential — scalar posture</h3>
<p>Phi carries wave and gate potential — electrical metaphor on the fabric. Discrete Laplacian steps in <code>CANVAS.comp</code> treat Phi as a scalar field evolving with <code>WaveSpeed</code> and <code>propalacticScale</code> forcing. <span class="tag impl">Implemented</span> at binding 8. <span class="tag meta">Electrical metaphor</span> — not a claim your GPU measures volts on the PCIe slot.</p>

<h3>Flow gradients — vector posture</h3>
<p>Flow stores momentum and advection structure; gradients in <code>.gb</code> channels give vector-field readings per texel. Coupling to <code>GateFidelity</code> and Tesla relaxation sharpens or softens gates. Chapter 3 details evolution; Chapter 2 fixes the vocabulary.</p>

<h3>data_bus — telemetry posture</h3>
<p>Sixty-four words per dispatch — not sixty-four texels. Slots carry pump generation, RAM/VGA telemetry, analog FCC floats [16–23], ThermoAccountant mirrors [24–28], input [32–41], audio/BIOS/IO [57–63]. Chapter 8 is the slot map; Chapter 2 insists it is a <em>telemetry field</em>, not a spatial substitute for Thermo.</p>

<h2>Scale 1 — GPU analog fabric (spatial)</h2>
<pre class="eq">RayCanvas → createAnalogFieldFabric() → CANVAS.comp / x86.comp → hardwareFabric mirror</pre>
<p><span class="tag impl">Implemented.</span> Each texel is a cell in a 2D sheet stacked with channel depth (Phi, Thermo, Flow). The host <em>never</em> runs a CPU-side PDE solver on the fabric. Evolution is compute-shader work each <code>vkCmdDispatch</code>. That architectural choice is offensive dispatch: the GPU writes the next tick; the host opens the window and enforces CFL.</p>
<p>Bindings 8, 9, and 10 are not decorative names. They are where electrical metaphor (Phi), thermal accounting (Thermo), and advective story (Flow) remain addressable after the frame ends. <code>updateHardwareFromAnalogFields()</code> samples averages into <code>hardwareFabric</code> — Chapter 10 — so fabric offense becomes spiderweb readout.</p>

<h3>Fabric creation and lifetime</h3>
<p><code>RayCanvas::createAnalogFieldFabric()</code> allocates storage images for Phi, Thermo, Flow. They persist across swipes that change binding-0 presentation shaders. Swiping to Classic thermo demos does not destroy die infrastructure — Chapter 7 swipe pedagogy. Fabric is the long-lived spatial state; canvas kind changes which shader emphasizes which lesson.</p>

<h3>Why no host PDE</h3>
<p>CPU PDE solvers on large grids compete with GPU memory bandwidth and split truth — host texels diverging from GPU texels is desynchronized reality. Single-source evolution on GPU keeps one writable truth surface. Host enforces CFL, packs buses, seals time — thin host, fat GPU.</p>

<h2>Scale 2 — Field Die (address space)</h2>
<pre class="eq">FieldX86Die SSBO (binding 1) → 64 MiB guest map → VGA @ 0xB8000 → C mirror @ 0x01000000</pre>
<p>The Field Die is a <em>universe with coordinates</em>, not a screenshot of DOS nostalgia. Guest RAM is where RTX-DOS and AmmoOS live. <code>data_bus</code> is the dashboard the shader reads — FCC floats, thermo mirrors, input slots, Tesla bias. <span class="tag impl">64 MiB implemented.</span> Chapter 8 is entirely this scale.</p>
<p>Reality is 3D on the bus: addresses, offsets, layers L0–L9. Time is linear in the pump loop. Energy moves through fabric coupling and thermo mirrors into bus slots. Default <code>./linux.sh run</code> boots this canvas.</p>

<h3>Guest RAM as spatial field</h3>
<p>Every byte in guest linear map is a cell in a 1D field indexed by offset — a different geometry than 2D fabric, same literacy. VGA at <code>0xB8000</code> is a structured subfield. ZMM1024 tile cache in the SSBO tail is shader-side sample cache for HUD hex dumps without leaving dispatch.</p>

<h3>Host assist versus GPU default</h3>
<p><code>FieldX86Emu</code> when <code>ControlHostCpu</code> set — optional assist path. Default remains GPU <code>x86.comp</code> interpretation. Category error: assuming emulation is the product because you once enabled assist.</p>

<h2>Scale 3 — Packet field (network topology)</h2>
<pre class="eq">ss / intent / DPI sample → gatekeeper scoring → threat-panel.json → panel :9477 + field jsonl</pre>
<p>NEXUS turns sockets into sentences: process path, port habit, TX vs RX, corroboration before permanent action. Defense begins when flows become <em>readable positions</em> in operator space. <span class="tag impl">Implemented in NEXUS.</span> <span class="tag meta">Not AMOURANTHRTX Vulkan.</span></p>
<p>Packet field is <strong>local-first</strong> — your machine's habits, not the whole internet. Chapter 5 full treatment. Queen inherits perimeter — Chapter 21.</p>

<h3>TX and RX as directional field</h3>
<p>TX: egress you own. RX: ingress you must explain. Direction is a dimension of the packet field — without it, flows are symmetric noise.</p>

<h3>Gatekeeper positions</h3>
<p>Verdicts attach to flows as boundary conditions on what the operator panel displays — USER_OK through HARM_CANDIDATE. One weird packet does not condemn a peer — <span class="tag phil">love as restraint</span>.</p>

<h2>Integration — one operator panel</h2>
<p>Three scales converge in observability without merging into one fake number:</p>
<ul>
<li>Fabric averages → <code>hardwareFabric</code> (Chapter 10)</li>
<li>Die telemetry → <code>data_bus</code> slots HUD reads (Chapter 8)</li>
<li>Packet rows → jsonl panel archives (Chapter 5)</li>
</ul>
<p>The operator at :9477 correlates all three. Thermo rising on fabric does not auto-explain SUSPICIOUS socket — but literate operators notice simultaneous stress.</p>

<figure class="figure"><img src="../assets/images/fabric-triple.jpg" alt="Three fabric channels" loading="lazy" /><figcaption>Figure 2.1 — Phi, Thermo, Flow: three channels, one fabric. Packet field and die are parallel scales, not substitutes.</figcaption></figure>

<h2>Category errors — learn these early</h2>
<div class="callout science"><strong>Do not</strong> treat shader visual as instrumentation. <strong>Do not</strong> treat JSON verdict as joules. <strong>Do not</strong> treat guest RAM metaphor as cloud perimeter. 3D state ≠ 3D hype.</div>
<p>Additional errors: treating <code>data_bus</code> as a 2D heatmap; treating planetary weave as spectrum truth; treating Shannon H as GPU entropy; treating Queen MP4 policy as optional codec luxury — it is mandatory in-tree gate doctrine.</p>

<h2>From pixels to packets — pipeline story</h2>
<p>Pixels are presentation. Packets are perimeter. Die bytes are address-space sovereignty. Field Technology connects them through operator literacy, not through one subsystem pretending to be all three.</p>
<p>Chapter 3 follows energy on fabric. Chapter 4 follows receipts. Chapter 5 follows defense. Chapter 6 separates RF meanings. Chapter 7 returns offense via dispatch. Read 2 before 7 — you must know what addresses dispatch writes.</p>

<h2>Operator drill — three-scale grep</h2>
<pre class="eq"># Fabric / die — AMOURANTHRTX
./linux.sh run 2>&1 | tee /tmp/ch2.log
grep -E 'THERMO|data_bus|dispatch' /tmp/ch2.log | tail -15

# Packet field — NEXUS
./nexus.sh
curl -sk https://127.0.0.1:9477/threat-panel.json | head -c 2000</pre>
<p>Name which scale each artifact belongs to. If you cannot, reread scalar/vector/telemetry table.</p>

<h2>Failure modes</h2>
<table><thead><tr><th>Mode</th><th>Symptom</th><th>Fix</th></tr></thead>
<tbody>
<tr><td>2D confusion</td><td>Plotting data_bus as heatmap</td><td>Telemetry ≠ spatial grid</td></tr>
<tr><td>Product blur</td><td>Gatekeeper in Vulkan grep</td><td>NEXUS boundary</td></tr>
<tr><td>Cosmology drift</td><td>3D hype without addresses</td><td>Reality is 3D = coordinates</td></tr>
<tr><td>Fabric bypass</td><td>Assuming die run ignores thermo</td><td>ThermoAccountant every dispatch</td></tr>
</tbody></table>

<h2>Chapter summary</h2>
<p>Reality is 3D here: texel (x,y), guest offset, socket quadruple. Scalar Thermo, vector Flow, telemetry data_bus. Three scales: fabric bindings 8–10, die 64 MiB binding 1, packet jsonl. Integration at panel without metric collapse. Time linear; energy coupled — Chapters 3–4 next.</p>

<h2>Study questions</h2>
<ol>
<li>Give three examples of addressable state — one per scale.</li>
<li>Why is data_bus telemetry, not a scalar spatial field?</li>
<li>Quote the fabric evolution path in one line.</li>
<li>What does local-first mean for packet field?</li>
<li>Name two category errors and their corrections.</li>
<li>How does hardwareFabric relate to fabric scale?</li>
<li>Default canvas at ./linux.sh run — which scale dominates?</li>
<li>Cross-link: which chapter owns CFL, gatekeeper, die map?</li>
</ol>
<p><a href="chapters/03-thermodynamics.html">Chapter 3 — Moving Energy →</a></p>
"""


def bulk_ch03() -> str:
    return r"""
<div class="objectives">
<h2>Learning objectives</h2>
<ol>
<li>Explain why thermodynamics appears in a Vulkan renderer as accounting, not calorimetry.</li>
<li>Name Phi, Thermo, Flow roles and bindings 8–10.</li>
<li>Describe per-texel evolution in CANVAS.comp and stability clamps.</li>
<li>Operate AnalogFields knobs and predict CFL guard behavior.</li>
<li>Relate Energy can be moved to FieldCoupling cross-channel exchange.</li>
<li>Run mouse-inject drill and grep THERMO receipts.</li>
</ol>
</div>

<h2>Why thermodynamics in a renderer?</h2>
<p>Every frame <strong>destroys information</strong> — noise injection, probes, diffusion steps, maintenance preserving coherence with the previous frame. The engine tracks that cost the way a power meter tracks joules: as <strong>accounting</strong>, not as a laboratory calorimeter taped to the GPU package.</p>
<p><strong>Energy can be moved.</strong> Chapter 3 is thermodynamics as honest bookkeeping — tracking where irreversibility goes, labeling proxy integrals before newcomers confuse them with billing data.</p>
<p>Rendering textbooks rarely discuss entropy. Security textbooks rarely discuss diffusion. Field Technology discusses both because the same fabric stores Phi beauty and Thermo cost — holographic boundary from Chapter 1 and Chapter 17.</p>

<figure class="figure inline-wide"><img src="../assets/images/v3/science/ch03-energy-transfer.jpg" alt="Coupled channels" loading="lazy" /><figcaption>Figure 3.1 — Coupled Phi, Thermo, Flow; energy moves every dispatch.</figcaption></figure>

<h2>The three fabric channels</h2>
<p>Created in <code>RayCanvas::createAnalogFieldFabric()</code>, bound at Vulkan slots <strong>8</strong>, <strong>9</strong>, <strong>10</strong>:</p>
<table><thead><tr><th>Fabric</th><th>Role</th><th>Binding</th></tr></thead>
<tbody>
<tr><td><strong>Phi (Φ)</strong></td><td>Wave / gate potential</td><td>8 — <code>fieldPhi</code></td></tr>
<tr><td><strong>Thermo</strong></td><td>Heat + entropy density</td><td>9 — <code>fieldThermo</code></td></tr>
<tr><td><strong>Flow</strong></td><td>Advection / momentum</td><td>10 — <code>fieldFlow</code> (.gb = gradients)</td></tr>
</tbody></table>
<p><strong>Cross-coupling:</strong> <code>FieldCoupling</code> links all three — electrical activity heats the die; heat affects flow; flow sharpens or softens gates through <code>GateFidelity</code>. Maxwell's neighborhood on a grid — Chapter 15 tribute.</p>

<h3>Phi evolution — wave step</h3>
<p>Discrete Laplacian + <code>WaveSpeed</code> + <code>propalacticScale</code> forcing. <span class="tag impl">CANVAS.comp</span> <span class="tag meta">Propalactic is cosmic-scale knob name — metaphor for large-wavelength forcing.</span></p>

<h3>Thermo evolution — diffusion</h3>
<p><code>ThermoAlpha</code> diffusivity, entropy floor, coupling to Phi. Seeded minimum in <code>clearFieldImages()</code> ~0.015 — second-law bias against unphysical reversibility.</p>

<h3>Flow evolution — advection story</h3>
<p>Gradient magnitude mixed with <code>GateFidelity</code> + Tesla relaxation. Directional bias in data_bus — Chapter 9.</p>

<h2>Per-texel evolution — CANVAS.comp ritual</h2>
<ol>
<li><strong>Phi</strong> — discrete Laplacian wave step + WaveSpeed + propalacticScale forcing</li>
<li><strong>Thermo</strong> — diffusion with ThermoAlpha, entropy floor, coupling to Phi</li>
<li><strong>Flow</strong> — gradient magnitude mixed with GateFidelity + Tesla relaxation</li>
</ol>
<pre class="eq">newPhi ∈ [-2.0, 2.0] · newThermo ∈ [0.0, 1.5] · newFlow ∈ [0.0, 1.0]</pre>
<p>Clamps are numerical ethics — the kitchen cannot invent infinite temperature because the UI got excited.</p>

<h2>Control knobs — Options::AnalogFields</h2>
<table><thead><tr><th>Knob</th><th>Effect</th></tr></thead>
<tbody>
<tr><td><code>TimeScale</code></td><td>Global Δt multiplier</td></tr>
<tr><td><code>ThermoAlpha</code></td><td>Thermal diffusivity α</td></tr>
<tr><td><code>WaveSpeed</code></td><td>Phi propagation speed c</td></tr>
<tr><td><code>GateFidelity</code></td><td>0 = soft analog … 1 = sharp gate</td></tr>
<tr><td><code>EntropyFloor</code></td><td>Minimum irreversible noise</td></tr>
<tr><td><code>InjectStrength</code></td><td>Mouse/probe energy injection</td></tr>
<tr><td><code>PropalacticScale</code></td><td>Large-wavelength forcing on Phi</td></tr>
<tr><td><code>FieldCoupling</code></td><td>Thermo ↔ Phi ↔ Flow coupling strength</td></tr>
</tbody></table>
<p>Prompt terminal <code>set AnalogFields.*</code> — Chapter 7 and 11. CFL may scale your ambition down before dispatch.</p>

<h2>Time is linear — dispatch and sealed time</h2>
<p><span class="tag impl"><code>dispatch_canvas()</code> advances one tick at a time.</span> <code>TotalTime::seal()</code> locks session genesis into <code>FieldSocket::sealed_time</code>. Frame-rate jitter cannot rewrite physics time. Energy accounting is per-frame, not retroactive myth. Chapter 19 extends posture across hosts.</p>

<h2>CFL guard — host refuses NaN theology</h2>
<pre class="eq">waveCFL = c·Δt/Δx ≤ 1 · thermoCFL = α·Δt/Δx² ≤ 1</pre>
<p>Before fabric evolution, host computes CFL. If violated, parameters scale down. Hard caps on <code>waveSpeed</code> and per-step <code>dT</code>. <span class="tag meta">Body-temperature seeding is simulation flavor — labeled, not hidden.</span></p>
<div class="callout everyone"><strong>Plain English:</strong> The engine refuses diffusion so hot the simulation explodes. Care for the operator who must grep logs after a long session.</div>

<h2>Energy accounting versus measurement</h2>
<p>ThermoAccountant binding 2 — preview Chapter 4. <span class="tag meta">Proxy integral, not joules.</span> Comparative receipts detect runaway dispatch, stuck entropy, broken coupling. Lab calorimetry is not replaced — honesty is.</p>

<h2>Coupling narrative — worked example</h2>
<p>Raise <code>FieldCoupling</code> and <code>InjectStrength</code>; move mouse on Classic canvas. Expect Phi ripples, Thermo rise, Flow structure change, stderr THERMO motion, spiderweb throttle hints — Chapter 10. If fabric moves and entropy stays zero, dispatch failed.</p>

<h2>Operator drill</h2>
<pre class="eq">./linux.sh run
# Swipe to energy or Classic if needed; move mouse 60s
grep -E 'THERMO|entropy|Boundary' run.log</pre>
<p>Boundary thermo and entropy proxy should move. If not, physics refuses to lie — fix dispatch path.</p>

<h2>Failure modes</h2>
<table><thead><tr><th>Mode</th><th>Symptom</th><th>Fix</th></tr></thead>
<tbody>
<tr><td>Joule fantasy</td><td>Billing from stderr thermo</td><td>Label proxy — Ch. 4</td></tr>
<tr><td>CFL ignore</td><td>NaN fabric, crash</td><td>Host guard — Ch. 9</td></tr>
<tr><td>Decoupled teaching</td><td>FieldCoupling 0 forever</td><td>Couple for full story</td></tr>
<tr><td>Canvas confusion</td><td>Thermo drill on x86 HUD only</td><td>Swipe Classic for visible fabric</td></tr>
</tbody></table>

<h2>Chapter summary</h2>
<p>Thermodynamics here is irreversibility accounting on Phi/Thermo/Flow — bindings 8–10, coupled by FieldCoupling, evolved in CANVAS.comp, guarded by CFL, receipted in ThermoAccountant. Energy can be moved between channels; measurement stays honestly proxy. Chapter 4 names entropy layers.</p>
<p>Tribute: <a href="../creditors/clausius-boltzmann.html">Clausius &amp; Boltzmann</a></p>

<h2>Study questions</h2>
<ol>
<li>Why thermodynamics in a renderer — one paragraph.</li>
<li>Write CFL inequalities and explain host action when violated.</li>
<li>Map each AnalogFields knob to effect.</li>
<li>What clamps bound newPhi, newThermo, newFlow?</li>
<li>Run mouse drill — paste one THERMO line and interpret.</li>
<li>How does FieldCoupling express Energy can be moved?</li>
<li>Why is body-temperature seeding labeled meta?</li>
<li>Cross-link chapters for entropy floor and Tesla bias.</li>
</ol>
<p><a href="chapters/04-entropy.html">Chapter 4 — Irreversibility &amp; Receipts →</a></p>
"""


def bulk_ch04() -> str:
    return r"""
<div class="objectives">
<h2>Learning objectives</h2>
<ol>
<li>Separate ThermoAccountant, entropy floor, and Shannon oracle — same word, different layers.</li>
<li>Describe ThermoAccountant fields and data_bus mirrors.</li>
<li>State Landauer bound as theory and proxy entropy as engine rock.</li>
<li>Operate week-one grep discipline for THERMO lines.</li>
<li>Explain entropy floor as second-law engineering bias.</li>
<li>Configure storm thresholds philosophy for NEXUS oracle.</li>
</ol>
</div>

<h2>Entropy is the receipt that time ran forward</h2>
<p>Entropy is the most abused word in security and the most honest word in thermodynamics. This chapter says both meanings out loud and refuses to let one pretend to be the other.</p>
<p>Time is linear means irreversibility leaves receipts — you cannot ungrep a frame. Energy can be moved means entropy proxy rises when coupling and probes do work. Reality is 3D means receipts land at bindings and bus slots you can address.</p>

<figure class="figure"><img src="../assets/images/entropy-chapter.jpg" alt="Entropy accounting" loading="lazy" /><figcaption>Figure 4.1 — Irreversibility: fabric floor, frame proxy, file randomness. Three layers, one vocabulary, three products.</figcaption></figure>

<h2>ThermoAccountant — engine layer</h2>
<p><span class="tag impl">Vulkan binding 2.</span> Populated every <code>dispatch_canvas()</code>:</p>
<pre class="eq">entropyThisFrame   — Landauer proxy + field work + probes
avgBoundaryThermo  — mean boundary temperature / entropy density
prevMaintCost      — cost to preserve previous-frame coherence
freeEnergyIncome   — sealed time + input activity
steps              — dispatch counter</pre>
<p>Mirrored to <code>data_bus[24–28]</code> for HUD and grep. THERMO lines in stderr are this structure's shadow. Chapter 7 stresses canvas-agnostic obligation — x86 HUD does not excuse skipping receipts.</p>

<h3>entropyThisFrame — proxy integral</h3>
<p>Components: field work from coupling, probe dissipation from mouse injection, maintenance cost for previous-frame coherence, host x86 heat when assist runs. <span class="tag meta"><strong>Rock:</strong> Not joules from nvidia-smi.</span> Comparative signal — spot stuck zero, runaway spikes, broken dispatch.</p>

<h3>Boundary and maintenance</h3>
<p><code>avgBoundaryThermo</code> summarizes boundary channel behavior — where fabric meets presentation. <code>prevMaintCost</code> is the price of memory across ticks — you cannot rewind for free.</p>

<h2>Landauer bound — theory</h2>
<div class="eq">E_min = k_B T ln 2</div>
<p>Minimum energy to erase one bit at temperature T. Landauer's insight is why irreversibility has a floor in physics — not optional decoration for GPU demos.</p>
<p>Chapter 13 deep dive honors Landauer without walking back proxy label. Theory inspires vocabulary; stderr shows implementation.</p>

<h2>Entropy floor — fabric bias</h2>
<p><code>clearFieldImages()</code> seeds thermo with ~0.015 minimum — prevents unphysical reversibility. Second law as engineering: diffusion always injects minimum noise. You cannot undo a frame by wishing.</p>
<p>Floor is <span class="tag impl">implemented</span> bias, not a claim the GPU measures Kelvin at the junction.</p>

<h2>Shannon oracle — NEXUS layer</h2>
<div class="eq">H = −Σ p_i log₂ p_i</div>
<p>High H on file payloads raises storm polling — defensive signal, not automatic verdict. Packed, encrypted, obfuscated payloads score high. Thresholds calm / alert / storm tune daemon polling like vitals, not sentence.</p>
<p><span class="tag impl">NEXUS-Shield.</span> Separate from ThermoAccountant — conflating them is vendor-dashboard lie.</p>

<table><thead><tr><th>Layer</th><th>Measures</th><th>Product</th></tr></thead>
<tbody>
<tr><td>ThermoAccountant</td><td>Frame entropy proxy</td><td>AMOURANTHRTX</td></tr>
<tr><td>Entropy floor</td><td>Fabric minimum noise</td><td>AMOURANTHRTX</td></tr>
<tr><td>Entropy Oracle</td><td>File randomness</td><td>NEXUS-Shield</td></tr>
</tbody></table>
<p><strong>Same word. Different layers. Do not conflate.</strong></p>

<h2>Operator grep — week one discipline</h2>
<pre class="eq">./linux.sh run 2>&1 | tee run.log
grep -E 'THERMO|entropy|Boundary|prevMaint' run.log</pre>
<p>If two entropies disagree, do not panic — they measure different layers. Panic is when marketing pretends one number does both jobs.</p>

<h2>Storm thresholds — pastoral care</h2>
<p>Shannon oracle changes how hard the perimeter watches — 94/6 posture applied to bytes. High H is nurse call, not auto-KILL. Chapter 14 expands oracle; Chapter 5 expands gatekeeper separation.</p>

<h2>Failure modes</h2>
<table><thead><tr><th>Mode</th><th>Symptom</th><th>Fix</th></tr></thead>
<tbody>
<tr><td>Layer conflation</td><td>Zip H compared to entropyThisFrame</td><td>Table above</td></tr>
<tr><td>Joule fantasy</td><td>Watt billing from proxy</td><td>Ch. 13 rock</td></tr>
<tr><td>Zero entropy pride</td><td>Fabric moves, entropy 0</td><td>Broken dispatch</td></tr>
<tr><td>Oracle as judge</td><td>Storm → auto block</td><td>Philosophy: corroborate</td></tr>
</tbody></table>

<h2>Chapter summary</h2>
<p>Entropy here is three layers — frame proxy, fabric floor, file oracle. Landauer is theory; proxy is metaphor with grep value. Shannon is NEXUS storm gauge. Label before you compare.</p>
<p>Tributes: <a href="../creditors/landauer.html">Landauer</a> · <a href="../creditors/shannon.html">Shannon</a></p>

<h2>Study questions</h2>
<ol>
<li>List ThermoAccountant fields and bus mirrors.</li>
<li>State Landauer bound and proxy rock in one sentence each.</li>
<li>Why entropy floor ~0.015?</li>
<li>When does high Shannon H matter — and what action does it <em>not</em> trigger?</li>
<li>Run grep drill; classify each line's layer.</li>
<li>What panic is justified vs not when entropies disagree?</li>
<li>Cross-link Ch. 13–14 for deep dives.</li>
</ol>
<p><a href="chapters/05-packet-field.html">Chapter 5 — Defensive Perimeter →</a></p>
"""


def bulk_ch05() -> str:
    return r"""
<div class="objectives">
<h2>Learning objectives</h2>
<ol>
<li>Define packet field as local-first connection sentences in jsonl.</li>
<li>Apply TX/RX operator contracts and corroboration before KILL.</li>
<li>Interpret Connection Gatekeeper verdicts and ten-axis scoring.</li>
<li>Map field memory artifacts to reboot survival.</li>
<li>Relate port stories to habits, not guilt.</li>
<li>Align Queen 2026 gates with packet field perimeter.</li>
</ol>
</div>

<h2>Defensive perimeter — the packet field</h2>
<p>The packet field is how you see what touches you <em>before</em> someone else narrates it for you. Offense and defense couple here: reading the field changes what you dare to run.</p>
<p><span class="tag impl">Implemented in NEXUS-Shield.</span> <span class="tag meta">Not inside AMOURANTHRTX Vulkan — different product boundary.</span> Local sockets, local jsonl, local panel :9477 — not cloud omniscience.</p>

<figure class="figure"><img src="../assets/images/packet-field.jpg" alt="Packet field" loading="lazy" /><figcaption>Figure 5.1 — Local flows as operator-readable positions in time. Not global internet vision.</figcaption></figure>

<h2>Plain English — sockets to sentences</h2>
<p>Every connection becomes a <strong>sentence</strong> in machine-readable log:</p>
<ul>
<li><code>ss</code> shows sockets</li>
<li><code>tcpdump</code> shows frames</li>
<li><strong>Packet field</strong> adds <em>meaning</em>: who, which port, TX vs RX, process path, corroboration</li>
</ul>
<div class="callout everyone"><strong>Plain English:</strong> ss is alphabet soup. Packet field is grammar — subject, verb, direction, story.</div>

<h2>TX / RX — operator perspective</h2>
<table><thead><tr><th>Direction</th><th>Contract</th></tr></thead>
<tbody>
<tr><td><strong>TX</strong></td><td>You sent bytes — egress you own</td></tr>
<tr><td><strong>RX</strong></td><td>You received bytes — ingress you must explain</td></tr>
</tbody></table>
<p>Direction is field dimension — symmetric flows without TX/RX are unreadable defense.</p>

<h2>Corroboration and 94/6 posture</h2>
<p>Multiple independent signals before permanent action. <span class="tag phil">94/6 truth filter</span> — watchlist before block; KILL is permanent and archived. One weird packet does not condemn a peer — love as engineering restraint.</p>
<div class="callout love">Reversible watchlists honor coupled evolution with consent. KILL dossiers survive reboot — forgiveness requires explicit operator review, not vendor cloud amnesty.</div>

<h2>Connection Gatekeeper — NEXUS</h2>
<p>Ten-axis scoring → verdicts:</p>
<table><thead><tr><th>Verdict</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td><code>USER_OK</code></td><td>Permitted flow</td></tr>
<tr><td><code>EPHEMERAL</code></td><td>Short-lived, low risk</td></tr>
<tr><td><code>SUSPICIOUS</code></td><td>Watchlist — not auto-block</td></tr>
<tr><td><code>HARM_CANDIDATE</code></td><td>Harm signature; operator review required</td></tr>
</tbody></table>
<p>Gatekeeper is <span class="tag impl">implemented</span> — grep lib sources and panel JSON. Not AMOURANTHRTX binding.</p>

<h3>Ten axes — literacy without memorizing every weight</h3>
<p>Axes include process path trust, port habit deviation, direction balance, payload surprise hooks, honorability cross-checks — full source in NEXUS lib. Operator stance: verdict is summary; jsonl row is receipt; human is judge.</p>

<h2>Field memory — what survives reboot</h2>
<table><thead><tr><th>Artifact</th><th>Survives reboot?</th></tr></thead>
<tbody>
<tr><td><code>field jsonl</code></td><td>Yes — packet history</td></tr>
<tr><td>KILL dossiers</td><td>Yes — permanent archive</td></tr>
<tr><td>Panel HTML</td><td>No — window only</td></tr>
</tbody></table>
<p>Memory is local-first discipline — your machine remembers so you can correlate across sessions without phone-home.</p>

<h2>Port stories — habits not guilt</h2>
<p>Ports are <strong>habits</strong>: 443 HTTPS, 53 DNS, 4444 shell-class risk. Registry learns <em>your machine's</em> habits, not textbook lists alone. A port is context for the sentence, not automatic guilt.</p>

<h2>Panel :9477 — operator command center</h2>
<p><code>https://127.0.0.1:9477/</code> — command, packets, threats, signals, DNS, library, system. RTX Zero <code>?rtx=1</code> — Aqua chrome. Correlate with AMOURANTHRTX stderr without merging products.</p>

<h2>Queen alignment — 2026</h2>
<p>Queen browser holds gates — WebRTC through gatekeeper, MP4 in-tree, EME held not omitted. Chapter 21 full doctrine. Packet field is perimeter Queen inherits — navigation → packet field → gatekeeper → honorability → thermo receipt.</p>
<pre class="eq">Navigation → Packet Field → Gatekeeper → Honorability → Thermo receipt
                ↑ Truth DNS (no Google shortcut)
                ↑ Sovereign Time (SQUIDGIE witness)</pre>

<h2>Operator drill</h2>
<pre class="eq">./nexus.sh
# Open panel :9477 — archive one gatekeeper decision
grep -E 'USER_OK|SUSPICIOUS|HARM' field.jsonl | tail -5</pre>

<h2>Failure modes</h2>
<table><thead><tr><th>Mode</th><th>Symptom</th><th>Fix</th></tr></thead>
<tbody>
<tr><td>Cloud fantasy</td><td>Expect global vision</td><td>Local-first scope</td></tr>
<tr><td>Auto-KILL</td><td>Storm → permanent block</td><td>Corroborate — 94/6</td></tr>
<tr><td>Product blur</td><td>Gatekeeper in Vulkan</td><td>NEXUS MIT layer</td></tr>
<tr><td>Port guilt</td><td>443 = evil</td><td>Habits in context</td></tr>
</tbody></table>

<h2>Chapter summary</h2>
<p>Packet field is local defensive perimeter — sentences in jsonl, gatekeeper verdicts, TX/RX contracts, corroboration before KILL. Queen inherits gates. Not AMOURANTHRTX Vulkan. Chapter 6 RF shell is separate visual layer.</p>

<h2>Study questions</h2>
<ol>
<li>What three tools does packet field extend — ss, tcpdump, and what addition?</li>
<li>Define TX and RX contracts.</li>
<li>Name four gatekeeper verdicts.</li>
<li>What survives reboot vs not?</li>
<li>Why are ports habits not guilt?</li>
<li>How does Queen bind to packet field without replacing NEXUS?</li>
<li>Archive one panel row — what fields prove local-first?</li>
</ol>
<p><a href="chapters/06-rf-signals.html">Chapter 6 — Signal Shell →</a></p>
"""


def bulk_ch06() -> str:
    return r"""
<div class="objectives">
<h2>Learning objectives</h2>
<ol>
<li>Separate three RF meanings in this stack with correct labels.</li>
<li>Describe planetary weave as visual-only vocabulary.</li>
<li>Locate Field Antenna Orchestrator outputs in NEXUS.</li>
<li>State FSPL as teaching reference, not shader computation.</li>
<li>Relate fieldPhi gate potential to RF metaphor without ionospheric claims.</li>
<li>Run panel drill for signals-field artifacts.</li>
</ol>
</div>

<h2>Three meanings of RF in this stack</h2>
<p>RF is three different weapons in the same word. Separate them or you will argue with a shader about ionospheric physics.</p>
<table><thead><tr><th>Context</th><th>What RF means</th><th>Label</th></tr></thead>
<tbody>
<tr><td><code>planetary_weave.comp</code></td><td>Atmospheric visual shell layer</td><td><span class="tag vis">Visual</span></td></tr>
<tr><td>NEXUS Field Antenna</td><td>Local RF/audio/wired orchestration</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td>Engine <code>fieldPhi</code></td><td>Gate voltage / wave potential</td><td><span class="tag impl">Implemented</span></td></tr>
</tbody></table>
<div class="callout science"><strong>Do not</strong> equate GPU Phi with ionospheric propagation without labeling the jump. Chapter 12 rocks table restates this.</div>

<figure class="figure"><img src="../assets/images/chapters/ch06-planetary-weave.jpg" alt="Planetary weave visual shell" loading="lazy" /><figcaption>Figure 6.1 — Visual shell only. Not a spectrum analyzer. Not FSPL in silicon.</figcaption></figure>

<h2>Planetary weave — visual layer</h2>
<p>Earth cross-section shader with concentric shells. RF layer sits in stack metaphor: core → crust → hydro → clouds → troposphere → ionosphere → <strong>RF shell</strong> → magnetosphere.</p>
<pre class="eq">#define R_RF  (R_EARTH + 1.05)   // Layer L_RF — visual vocabulary</pre>
<p><span class="tag vis">Visual vocabulary</span> — teaches where signals live in stack metaphor. Does <em>not</em> compute FSPL inside AMOURANTHRTX shaders. Honesty on every rock.</p>

<h3>What weave teaches</h3>
<p>Pedagogy: operators need a picture of where defense and dispatch stories sit relative to atmosphere and ionosphere. Weave supplies picture, not instrument. When someone claims weave color proves propagation anomaly, return to Chapter 12.</p>

<h2>fieldPhi — gate potential, not literal radio</h2>
<p>Binding 8 Phi carries wave and gate potential — electrical metaphor coupled to Thermo and Flow. <span class="tag impl">Implemented</span> fabric evolution. <span class="tag meta">Not</span> claim that texels measure RF watts at antenna.</p>
<p>Chapter 3 coupling; Chapter 15 Maxwell tribute. Phi is RF word only in metaphor sense — label before you speak.</p>

<h2>Field Antenna Orchestrator — NEXUS</h2>
<p>Monitors RF + audio + wired + laser reference bands. Optical/laser entries 405–1550 nm. LIDAR flow ports in registry. GPS field anchors for triangulation metaphor. Outputs:</p>
<ul>
<li><code>field-antenna-panel.json</code></li>
<li><code>field-rf-panel.json</code></li>
<li><code>signals-field-panel.json</code></li>
</ul>
<p><span class="tag impl">Implemented in NEXUS.</span> Local orchestration — correlate with packet field at panel :9477.</p>

<h3>Registry and habits</h3>
<p>Like port stories in Chapter 5, RF registry learns local device habits — context, not automatic verdict.</p>

<h2>Free-space path loss — teaching reference</h2>
<div class="eq">FSPL ∝ 20·log₁₀(d) + 20·log₁₀(f)</div>
<p>ITU-R/FCC context in NEXUS docs — <strong>not</strong> computed inside AMOURANTHRTX shaders. Teach path loss beside the label. Planetary weave does not replace FSPL math with colors.</p>

<h2>Signals panel integration</h2>
<p>Operator correlates signals-field JSON with packet field jsonl and AMOURANTHRTX THERMO — three scales from Chapter 2. No single dashboard metric collapse.</p>

<h2>Queen and WebRTC — RF-adjacent perimeter</h2>
<p>WebRTC is not disabled — gated through Connection Gatekeeper. RF words appear in peer stories; verdicts remain NEXUS. Chapter 21 Queen doctrine. MP4 mandatory in-tree; EME held.</p>

<h2>Operator drill</h2>
<pre class="eq">./nexus.sh
curl -sk https://127.0.0.1:9477/signals-field-panel.json | head -c 1500
# Name which RF meaning each JSON block belongs to</pre>

<h2>Failure modes</h2>
<table><thead><tr><th>Mode</th><th>Symptom</th><th>Fix</th></tr></thead>
<tbody>
<tr><td>Weave as instrument</td><td>Ionosphere claims from shader</td><td><span class="tag vis">Visual</span></td></tr>
<tr><td>Phi as MHz</td><td>Texel equals spectrum</td><td>Metaphor — binding 8</td></tr>
<tr><td>FSPL in GPU</td><td>Expect FSPL in weave</td><td>NEXUS docs only</td></tr>
<tr><td>Antenna omniscience</td><td>Global RF vision</td><td>Local orchestration</td></tr>
</tbody></table>

<h2>Chapter summary</h2>
<p>RF is three meanings — weave visual, NEXUS antenna implemented, Phi potential implemented metaphor. FSPL is teaching reference. Planetary weave is vocabulary art. Chapter 7 offense dispatch next.</p>

<h2>Study questions</h2>
<ol>
<li>Fill three-row RF table from memory with labels.</li>
<li>What does R_RF define — and what does it not compute?</li>
<li>Name three Field Antenna JSON outputs.</li>
<li>Why is FSPL not in AMOURANTHRTX shaders?</li>
<li>How does Phi differ from planetary weave RF shell?</li>
<li>Run signals panel drill — classify one JSON field.</li>
<li>Cross-link Queen WebRTC gates — which chapter?</li>
</ol>
<p><a href="chapters/07-gpu-engine.html">Chapter 7 — Offensive Dispatch →</a></p>
"""
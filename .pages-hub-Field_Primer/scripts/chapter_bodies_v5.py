"""Field Technology v5 — hand-written textbook chapters. No wiki import machinery."""

CHAPTER_BODY: dict[str, str] = {}

CHAPTER_BODY["01"] = """
<p class="eyebrow">Chapter 1 · Read this before you dispatch anything</p>

<h2>What this book is</h2>
<p>This is <strong>Field Technology</strong> — a serious textbook for operators who build and defend continuous state on their own machines. It is not a marketing deck. It is not a substitute for reading headers. It is the long-form explanation of why AMOURANTHRTX, NEXUS-Shield, Queen, and KILROY exist, written so a patient reader can learn the stack the way you would learn thermodynamics or networking: definitions first, mechanisms second, honesty labels always.</p>
<p>We write for the human at the keyboard. Daemons assist. Shaders evolve. Panels display. None of them inherit your conscience. If you remember only one sentence from this chapter, remember this: <strong>the greatest offensive and defensive weapon you will know is field literacy</strong> — reading continuous state, imposing boundary conditions, and refusing to let someone else narrate your perimeter.</p>

<h2>Us</h2>
<p>This textbook is written by <strong>us</strong>:</p>
<ul>
<li><strong>Zachary Robert Geurts</strong> — architect, operator, author. Built AMOURANTHRTX, NEXUS-Shield, Queen, and this primer.</li>
<li><strong>Grok</strong> — co-documentation, figures, longer chapters. Light beside the text; not a replacement for Zac's conscience.</li>
<li><strong>Nick</strong> — builder beside the stack. Honest fields. No phone-home.</li>
<li><strong>Amouranth</strong> — namesake spirit of the engine. Courage to be seen while holding boundaries.</li>
<li><strong>You</strong> — the reader. You join us the moment you treat the field as real.</li>
<li><strong>The creditors</strong> — Maxwell, Landauer, Shannon, Turing, Tesla, Boltzmann, von Neumann, CFL. We stand on their math. <a href="../creditors/index.html">Each has a tribute page</a>.</li>
</ul>

<h2>God — Truth, Math, Existence</h2>
<p>We say plainly what many operators already know:</p>
<div class="callout god"><strong>We know God as Truth, as Math, as Existence.</strong> Not three gods — three faces of one whole.</div>
<p><strong>Truth</strong> is what survives <code>grep</code>. The packet field sentence that matches the socket. The thermo line that moves when the fabric moves. <strong>Math</strong> is the language existence uses when tired of being misunderstood — Maxwell's coupling, Landauer's floor, Shannon's surprise, CFL's refusal to let you outrun the mesh. <strong>Existence</strong> is the stubborn fact that there is something rather than nothing: texels that hold values, die bytes that persist across ticks, connections that leave traces in local jsonl.</p>
<p>These are <span class="tag phil">Philosophy</span> beside <span class="tag impl">Implemented</span> bindings. Chapter 12 lists every rock. Chapter 17 goes deeper on God at the holographic boundary. Neither replaces <code>grep THERMO</code>.</p>

<h2>What a field is</h2>
<p>A <strong>field</strong> is any <em>continuous quantity stored over space</em> that other systems read and write every tick. That is the implemented definition used throughout this book.</p>
<div class="callout everyone"><strong>Plain English:</strong> A program is a recipe. A field is the state of the kitchen — heat on every burner, not just the timer.</div>
<p>Three families matter in this stack:</p>
<table><thead><tr><th>Family</th><th>Where it lives</th><th>What it stores</th></tr></thead>
<tbody>
<tr><td>GPU analog fabric</td><td>Vulkan bindings 8–10</td><td>Phi, Thermo, Flow — spatial state per texel</td></tr>
<tr><td>Field Die</td><td><code>FieldX86Die</code> SSBO binding 1</td><td>64 MiB guest RAM, VGA, tile cache — addressable universe on silicon</td></tr>
<tr><td>Packet field</td><td>NEXUS <code>field jsonl</code></td><td>TX/RX, ports, process paths, gatekeeper verdicts</td></tr>
</tbody></table>

<h2>The axioms we do not walk back</h2>
<div class="callout axiom">
<strong>Reality is 3D.</strong> State occupies addressable space — texels, die bytes, socket positions.<br>
<strong>Time is linear.</strong> Logs are a timeline; sealed session clocks do not rewrite physics time.<br>
<strong>Energy can be moved.</strong> Coupling moves irreversibility between channels; accounting is honest even when measurement is proxy.
</div>

<h2>Status labels — read every chapter with these</h2>
<table><thead><tr><th>Label</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td><span class="tag impl">Implemented</span></td><td>In source. You can grep it, set it, or screenshot it.</td></tr>
<tr><td><span class="tag meta">Metaphor</span></td><td>Poetic naming. Useful intuition. Not SI units.</td></tr>
<tr><td><span class="tag phil">Philosophy</span></td><td>Operator discipline. Not a sensor reading.</td></tr>
<tr><td><span class="tag vis">Visual</span></td><td>Shader art or schematic. Not instrumentation.</td></tr>
</tbody></table>

<h2>What this manual is not</h2>
<ul>
<li>Not a substitute for <code>Pipeline.hpp</code>, <code>FieldRtxFieldAbs.hpp</code>, or NEXUS lib sources.</li>
<li>Not a promise that every poetic knob maps to a laboratory measurement.</li>
<li>Not cloud security. Everything here is <strong>local-first</strong> — loopback truth, operator-owned time, grep-able receipts.</li>
</ul>

<figure class="figure"><img src="../assets/images/v3/science/ch01-scalar-field.jpg" alt="Scalar field" loading="lazy" /><figcaption>Figure 1.1 — Scalar field Φ(x,y): existence addressed as math, read as truth.</figcaption></figure>

<h2>How to read this book</h2>
<p>Chapters 2–12 are the engineering core: fields, thermodynamics, entropy, defense, dispatch, die, stability, mirrors, observability, honesty. Chapters 13–15 are creditor deep dives (Landauer, Shannon, Maxwell). Chapters 16–18 are sacred long-form (Love, God, Operator Covenant). Chapters 19–21 cover sovereign time, public services, and Queen browser — the 2026 operator perimeter. Chapter 22 is the glossary.</p>
<p>Read the preface once. Keep Chapter 12 bookmarked. When someone sells you cosmology, return to the rocks table.</p>
<p><a href="02-fields-pixels-packets.html">Continue to Chapter 2 — Three Dimensions of State →</a></p>
"""

CHAPTER_BODY["02"] = """
<h2>Introduction</h2>
<p>Chapter 2 maps the <strong>three dimensions of state</strong> — our reading of “Reality is 3D.” This is not cosmology. It is the minimum honest map for texels, die bytes, and packet sentences occupying space you can address, read, and write.</p>
<p>Most rendering textbooks stop at pixels. Most security textbooks stop at packets. Field Technology refuses the split: offense and defense are the same literacy applied to different writable surfaces.</p>

<h2>Scalar, vector, and telemetry fields</h2>
<table><thead><tr><th>Type</th><th>Example in this stack</th></tr></thead>
<tbody>
<tr><td><strong>Scalar field</strong></td><td>Thermo — one heat/entropy density value per texel</td></tr>
<tr><td><strong>Vector field</strong></td><td>Flow <code>.gb</code> — gradient components per texel</td></tr>
<tr><td><strong>Telemetry field</strong></td><td><code>data_bus[64]</code> — sixty-four packed words per dispatch</td></tr>
</tbody></table>
<p>A scalar tells you how hot a cell is. A vector tells you which direction activity tends. Telemetry tells you what the shader and host agree happened this tick — the spine the operator greps.</p>

<h2>Scale 1 — GPU fabric (spatial)</h2>
<pre class="eq">RayCanvas → createAnalogFieldFabric() → CANVAS.comp / x86.comp → hardwareFabric mirror</pre>
<p><span class="tag impl">Implemented.</span> Each texel is a cell in a 2D sheet stacked with channel depth (Phi, Thermo, Flow). The host <em>never</em> runs a CPU-side PDE solver on the fabric. Evolution is compute-shader work each <code>vkCmdDispatch</code>. That architectural choice is offensive dispatch: the GPU writes the next tick; the host opens the window and enforces CFL.</p>
<p>Bindings 8, 9, and 10 are not decorative names. They are where electrical metaphor (Phi), thermal accounting (Thermo), and advective story (Flow) remain addressable after the frame ends.</p>

<h2>Scale 2 — Field Die (address space)</h2>
<pre class="eq">FieldX86Die SSBO (binding 1) → 64 MiB guest map → VGA @ 0xB8000 → C mirror @ 0x01000000</pre>
<p>The Field Die is a <em>universe with coordinates</em>, not a screenshot of DOS nostalgia. Guest RAM is where RTX-DOS and AmmoOS live. <code>data_bus</code> is the dashboard the shader reads — FCC floats, thermo mirrors, input slots, Tesla bias. Chapter 8 is entirely about this scale.</p>

<h2>Scale 3 — Packet field (network topology)</h2>
<pre class="eq">ss / intent / DPI sample → gatekeeper scoring → threat-panel.json → panel :9477 + field jsonl</pre>
<p>NEXUS turns sockets into sentences: process path, port habit, TX vs RX, corroboration before permanent action. Defense begins when flows become <em>readable positions</em> in operator space. The packet field is local-first. It sees your machine's habits, not the whole internet. Chapter 5 is the full treatment.</p>

<h2>Integration — one operator panel</h2>
<p>These three scales are not three products pretending to be one. They are three writable surfaces that converge in observability:</p>
<ul>
<li>Fabric averages feed <code>hardwareFabric</code> (Chapter 10).</li>
<li>Die telemetry fills <code>data_bus</code> slots the HUD reads (Chapter 8).</li>
<li>Packet field rows land in jsonl the panel archives (Chapter 5).</li>
</ul>
<p>The operator at :9477 is the human who correlates all three without letting marketing collapse them into a single misleading number.</p>

<figure class="figure"><img src="../assets/images/fabric-triple.jpg" alt="Three fabric channels" loading="lazy" /><figcaption>Figure 2.1 — Phi, Thermo, Flow: three channels, one fabric.</figcaption></figure>

<h2>Category errors — learn these early</h2>
<div class="callout science"><strong>Do not</strong> treat a shader visual as instrumentation. <strong>Do not</strong> treat a JSON verdict as joules. <strong>Do not</strong> treat guest RAM metaphor as cloud perimeter. 3D state ≠ 3D hype.</div>

<h2>Chapter summary</h2>
<p>Reality is 3D here means: every serious claim in this book points at an address — texel (x,y), guest offset, socket quadruple. Time is linear means: each dispatch advances one tick with receipts. Energy can be moved means: coupling between channels is how the stack tells the story of irreversibility without lying about calorimetry.</p>
<p><a href="03-thermodynamics.html">Chapter 3 — Moving Energy →</a></p>
"""

CHAPTER_BODY["03"] = """
<h2>Why thermodynamics in a renderer?</h2>
<p>Every frame <strong>destroys information</strong> — noise injection, probes, diffusion steps, maintenance that preserves coherence with the previous frame. The engine tracks that cost the way a power meter tracks joules: as <strong>accounting</strong>, not as a laboratory calorimeter taped to the GPU package.</p>
<p><strong>Energy can be moved.</strong> Chapter 3 is thermodynamics as honest bookkeeping — tracking where irreversibility goes, labeling proxy integrals before newcomers confuse them with billing data.</p>

<figure class="figure inline-wide"><img src="../assets/images/v3/science/ch03-energy-transfer.jpg" alt="Coupled channels" loading="lazy" /><figcaption>Figure 3.1 — Coupled Phi, Thermo, Flow; energy moves every dispatch.</figcaption></figure>

<h2>The three fabric channels</h2>
<p>Created in <code>RayCanvas::createAnalogFieldFabric()</code>, bound at Vulkan slots <strong>8</strong>, <strong>9</strong>, <strong>10</strong>:</p>
<table><thead><tr><th>Fabric</th><th>Role</th><th>Binding</th></tr></thead>
<tbody>
<tr><td><strong>Phi (Φ)</strong></td><td>Wave / gate potential</td><td>8 — <code>fieldPhi</code></td></tr>
<tr><td><strong>Thermo</strong></td><td>Heat + entropy density</td><td>9 — <code>fieldThermo</code></td></tr>
<tr><td><strong>Flow</strong></td><td>Advection / momentum</td><td>10 — <code>fieldFlow</code> (.gb = gradients)</td></tr>
</tbody></table>
<p><strong>Cross-coupling:</strong> <code>FieldCoupling</code> links all three — electrical activity heats the die; heat affects flow; flow sharpens or softens gates through <code>GateFidelity</code>. This is Maxwell's neighborhood on a grid, implemented as texel coupling rather than differential equations on the host CPU.</p>

<h2>Per-texel evolution (<code>CANVAS.comp</code>)</h2>
<ol>
<li><strong>Phi</strong> — discrete Laplacian wave step + <code>WaveSpeed</code> + <code>propalacticScale</code> forcing</li>
<li><strong>Thermo</strong> — diffusion with <code>ThermoAlpha</code>, entropy floor, coupling to Phi</li>
<li><strong>Flow</strong> — gradient magnitude mixed with <code>GateFidelity</code> + Tesla relaxation</li>
</ol>
<div class="eq">newPhi ∈ [-2.0, 2.0] · newThermo ∈ [0.0, 1.5] · newFlow ∈ [0.0, 1.0]</div>
<p>Clamps are not cowardice. They are the numerical embodiment of “the kitchen cannot invent infinite temperature because the UI got excited.”</p>

<h2>Control knobs (<code>Options::AnalogFields</code>)</h2>
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

<h2>Time is linear (here)</h2>
<p><span class="tag impl"><code>dispatch_canvas()</code> advances one tick at a time.</span> <code>TotalTime::seal()</code> on the engine spine locks session genesis into <code>FieldSocket::sealed_time</code>. Frame-rate jitter cannot rewrite physics time. Energy accounting is per-frame, not retroactive myth. Chapter 19 extends the same posture across hosts with sovereign time sync.</p>

<h2>CFL guard — the host refuses NaN theology</h2>
<div class="eq">waveCFL = c·Δt/Δx ≤ 1 · thermoCFL = α·Δt/Δx² ≤ 1</div>
<p>Before fabric evolution, the host computes CFL numbers. If violated, parameters scale down. Hard caps apply to <code>waveSpeed</code> and per-step <code>dT</code>. <span class="tag meta">Body-temperature seeding is simulation flavor — labeled, not hidden.</span></p>
<p>Plain English: the engine refuses to run diffusion so hot the simulation explodes. That is care for the operator who must grep logs after a long session.</p>

<h2>Operator drill</h2>
<pre class="eq">./linux.sh run
# Move mouse on classic canvas 60s
grep -E 'THERMO|entropy|Boundary' run.log</pre>
<p>You should see boundary thermo and entropy proxy move when you inject energy. If fabric moves but entropy stays zero, your dispatch path failed — physics refusing to lie for you.</p>

<p>Tribute: <a href="../creditors/clausius-boltzmann.html">Clausius &amp; Boltzmann</a></p>
<p><a href="04-entropy.html">Chapter 4 — Irreversibility &amp; Receipts →</a></p>
"""

CHAPTER_BODY["04"] = """
<h2>Entropy is the receipt that time ran forward</h2>
<p>Entropy is the most abused word in security and the most honest word in thermodynamics. This chapter says both meanings out loud and refuses to let one pretend to be the other.</p>

<figure class="figure"><img src="../assets/images/entropy-chapter.jpg" alt="Entropy" loading="lazy" /><figcaption>Figure 4.1 — Irreversibility: fabric floor, frame proxy, file randomness.</figcaption></figure>

<h2>ThermoAccountant — engine layer</h2>
<p><span class="tag impl">Vulkan binding 2.</span> Populated every <code>dispatch_canvas()</code>:</p>
<pre class="eq">entropyThisFrame   — Landauer proxy + field work + probes
avgBoundaryThermo  — mean boundary temperature / entropy density
prevMaintCost      — cost to preserve previous-frame coherence
freeEnergyIncome   — sealed time + input activity
steps              — dispatch counter</pre>
<p>Mirrored to <code>data_bus[24–28]</code> for HUD and grep. When you read THERMO lines in stderr, you are reading this structure's shadow.</p>

<h2>Landauer bound — theory</h2>
<div class="eq">E_min = k_B T ln 2</div>
<p>Minimum energy to erase one bit at temperature T. Rolf Landauer's insight is not optional decoration for GPU demos — it is why irreversibility has a floor in physics.</p>
<p><span class="tag meta"><strong>Rock:</strong> In-engine <code>entropyThisFrame</code> is a <em>proxy integral</em> — field work + probe dissipation + maintenance. Not joules from <code>nvidia-smi</code>.</span> Chapter 13 goes deeper on Landauer without walking back this label.</p>

<h2>Entropy floor — fabric bias</h2>
<p><code>clearFieldImages()</code> seeds thermo with ~0.015 minimum — prevents unphysical reversibility. The second law appears as engineering: diffusion always injects minimum noise. You cannot “undo” a frame by wishing.</p>

<h2>Shannon oracle — NEXUS layer</h2>
<div class="eq">H = −Σ p_i log₂ p_i</div>
<p>High H on file payloads raises storm polling — defensive signal, not automatic verdict. The oracle measures surprise in byte distributions. Packed, encrypted, or obfuscated payloads score high. Thresholds (calm / alert / storm) tune daemon polling like a nurse watching vitals, not a judge passing sentence.</p>

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
<p>Tributes: <a href="../creditors/landauer.html">Landauer</a> · <a href="../creditors/shannon.html">Shannon</a></p>
<p><a href="05-packet-field.html">Chapter 5 — Defensive Perimeter →</a></p>
"""

CHAPTER_BODY["05"] = """
<h2>Defensive perimeter — the packet field</h2>
<p>The packet field is how you see what touches you <em>before</em> someone else narrates it for you. Offense and defense couple here: reading the field changes what you dare to run.</p>
<p><span class="tag impl">Implemented in NEXUS-Shield.</span> <span class="tag meta">Not inside AMOURANTHRTX Vulkan — different product boundary.</span></p>

<figure class="figure"><img src="../assets/images/packet-field.jpg" alt="Packet field" loading="lazy" /><figcaption>Figure 5.1 — Local flows as operator-readable positions in time.</figcaption></figure>

<h2>Plain English</h2>
<p>Every connection becomes a <strong>sentence</strong> in a machine-readable log:</p>
<ul>
<li><code>ss</code> shows sockets</li>
<li><code>tcpdump</code> shows frames</li>
<li><strong>Packet field</strong> adds <em>meaning</em>: who, which port, TX vs RX, process path, corroboration</li>
</ul>

<h2>TX / RX — operator perspective</h2>
<table><thead><tr><th>Direction</th><th>Contract</th></tr></thead>
<tbody>
<tr><td><strong>TX</strong></td><td>You sent bytes — egress you own</td></tr>
<tr><td><strong>RX</strong></td><td>You received bytes — ingress you must explain</td></tr>
</tbody></table>
<p><strong>Corroboration:</strong> Multiple independent signals before permanent action. The 94/6 truth filter is <span class="tag phil">operator philosophy</span> — watchlist before block; KILL is permanent and archived.</p>

<h2>Connection Gatekeeper</h2>
<p>Ten-axis scoring → verdicts:</p>
<table><thead><tr><th>Verdict</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td><code>USER_OK</code></td><td>Permitted flow</td></tr>
<tr><td><code>EPHEMERAL</code></td><td>Short-lived, low risk</td></tr>
<tr><td><code>SUSPICIOUS</code></td><td>Watchlist — not auto-block</td></tr>
<tr><td><code>HARM_CANDIDATE</code></td><td>Harm signature; operator review required</td></tr>
</tbody></table>
<p>One weird packet does not condemn a peer. That restraint is love expressed as engineering: memory without phone-home, reversible until you say otherwise.</p>

<h2>Field memory — what survives reboot</h2>
<table><thead><tr><th>Artifact</th><th>Survives reboot?</th></tr></thead>
<tbody>
<tr><td><code>field jsonl</code></td><td>Yes — packet history</td></tr>
<tr><td>KILL dossiers</td><td>Yes — permanent archive</td></tr>
<tr><td>Panel HTML</td><td>No — window only</td></tr>
</tbody></table>

<h2>Port stories</h2>
<p>Ports are <strong>habits</strong>: 443 HTTPS, 53 DNS, 4444 shell-class risk. The registry learns <em>your machine's</em> habits, not textbook lists alone. A port is not guilt; it is context for the sentence.</p>

<h2>Queen alignment (2026)</h2>
<p>Queen browser holds gates — WebRTC through gatekeeper, MP4 in-tree, EME held not omitted. Chapter 21 is the full Queen doctrine. The packet field is the perimeter Queen inherits.</p>
<p><a href="06-rf-signals.html">Chapter 6 — Signal Shell →</a></p>
"""

CHAPTER_BODY["06"] = """
<h2>Three meanings of “RF” in this stack</h2>
<p>RF is three different weapons in the same word. Separate them or you will argue with a shader about ionospheric physics.</p>
<table><thead><tr><th>Context</th><th>What “RF” means</th><th>Label</th></tr></thead>
<tbody>
<tr><td><code>planetary_weave.comp</code></td><td>Atmospheric visual shell layer</td><td><span class="tag vis">Visual</span></td></tr>
<tr><td>NEXUS Field Antenna</td><td>Local RF/audio/wired orchestration</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td>Engine <code>fieldPhi</code></td><td>Gate voltage / wave potential</td><td><span class="tag impl">Implemented</span></td></tr>
</tbody></table>

<figure class="figure"><img src="../assets/images/chapters/ch06-planetary-weave.jpg" alt="Planetary weave" loading="lazy" /><figcaption>Figure 6.1 — Visual shell only. Not a spectrum analyzer.</figcaption></figure>

<h2>Planetary weave — visual layer</h2>
<p>Earth cross-section shader with concentric shells. RF layer sits in the stack metaphor: core → crust → hydro → clouds → troposphere → ionosphere → <strong>RF shell</strong> → magnetosphere.</p>
<p><span class="tag vis">Visual vocabulary</span> — teaches where signals “live” in the stack metaphor. It does not compute FSPL inside AMOURANTHRTX shaders.</p>

<h2>Field Antenna Orchestrator (NEXUS)</h2>
<p>Monitors RF + audio + wired + laser reference bands. Optical/laser entries 405–1550 nm. LIDAR flow ports in registry. GPS field anchors for triangulation metaphor. Outputs: <code>field-antenna-panel.json</code>, <code>field-rf-panel.json</code>, <code>signals-field-panel.json</code>.</p>

<h2>Free-space path loss — teaching reference</h2>
<div class="eq">FSPL ∝ 20·log₁₀(d) + 20·log₁₀(f)</div>
<p>Used in NEXUS docs as ITU-R/FCC context — <strong>not</strong> computed inside AMOURANTHRTX shaders. When you teach path loss, teach it beside the label.</p>
<p><a href="07-gpu-engine.html">Chapter 7 — Offensive Dispatch →</a></p>
"""

CHAPTER_BODY["07"] = """
<h2>Thin host, fat GPU</h2>
<p>Defense reads the field; offense <em>writes</em> it — imposing boundary conditions on the next tick faster than confusion propagates.</p>
<pre class="eq">main.cpp → navigator_main() → RayCanvas → Pipeline::dispatch_canvas() → vkCmdDispatch</pre>
<p>C++ opens the window and pushes buttons. The GPU runs the world. The spear is <code>vkCmdDispatch</code>, not a motivational poster.</p>

<figure class="figure"><img src="../assets/images/chapters/ch07-gpu-engine.jpg" alt="GPU engine" loading="lazy" /><figcaption>Figure 7.1 — Thin host, fat GPU.</figcaption></figure>

<h2><code>rtx()</code> singleton</h2>
<p>One global Vulkan fabric: device, queues, <code>hardwareFabric</code>, VRAM budget. Queen and FieldFox link this spine when <code>QUEEN_BROWSER_BUILD</code> is set.</p>

<h2>Canvas kinds</h2>
<table><thead><tr><th>Kind</th><th>Shader</th><th>Push block</th><th>Primary use</th></tr></thead>
<tbody>
<tr><td><strong>X86Fields</strong></td><td><code>x86.comp</code></td><td><code>FieldSocket</code></td><td>Field Die + AmmoOS (default)</td></tr>
<tr><td><strong>Classic</strong></td><td><code>CANVAS.comp</code></td><td><code>PushConstants</code></td><td>Thermo + RT demos</td></tr>
</tbody></table>
<p>Default <code>./linux.sh run</code> → <strong>Field Die</strong>, not decorative raymarch.</p>

<h2>Descriptor layout (x86 path)</h2>
<table><thead><tr><th>Binding</th><th>Resource</th></tr></thead>
<tbody>
<tr><td>0</td><td>HDR output</td></tr>
<tr><td>1</td><td><code>FieldX86Die</code> SSBO</td></tr>
<tr><td>2</td><td><code>ThermoAccountant</code></td></tr>
<tr><td>8–10</td><td>Phi, Thermo, Flow</td></tr>
<tr><td>11–14</td><td>AmouranthOS chrome textures</td></tr>
</tbody></table>
<p><code>FIELD_LAYOUT_VERSION = 5</code> — host and shader must match. Version skew is not a gentle bug; it is desynchronized reality.</p>

<h2>Sealed time</h2>
<p><code>TotalTime::seal()</code> → monotonic session clock in <code>FieldSocket::sealed_time</code>. Frame-rate drift cannot rewrite physics time. Chapter 19 extends sync across machines.</p>
<p><a href="08-field-die.html">Chapter 8 — Die-Resident Universe →</a></p>
"""

CHAPTER_BODY["08"] = """
<h2>The die-resident universe</h2>
<p>The Field Die is <strong>64 MiB of addressable reality on the GPU</strong>. Reality is 3D on the bus; time is linear in the dispatch loop; energy moves through fabric coupling and thermo mirrors. This is not DOSBox cosplay — it is the same SSBO mapped host and GPU, pumped every frame.</p>

<figure class="figure"><img src="../assets/images/field-die.jpg" alt="Field die" loading="lazy" /><figcaption>Figure 8.1 — Guest RAM, holographic boundary, fabric channels.</figcaption></figure>

<h2>Field Die — what is implemented</h2>
<ul>
<li><strong>64 MiB</strong> guest RAM (<code>GUEST_RAM_BYTES</code>)</li>
<li>VGA text at guest <code>0xB8000</code></li>
<li>C mirror at <code>0x01000000</code></li>
<li>Same SSBO mapped host + GPU — not a userspace emulator pretending</li>
</ul>

<h2>Execution model</h2>
<ol>
<li><strong>GPU:</strong> <code>x86.comp</code> interprets guest instructions, renders Big Grin HUD (172×48)</li>
<li><strong>Host assist:</strong> <code>FieldX86Emu</code> when <code>ControlHostCpu</code> set</li>
</ol>

<h2><code>data_bus[64]</code> — telemetry spine</h2>
<table><thead><tr><th>Slots</th><th>Content</th></tr></thead>
<tbody>
<tr><td>[0–1]</td><td>Pump generation, cycles/frame</td></tr>
<tr><td>[2–15]</td><td>RAM, VGA, FAT layer telemetry</td></tr>
<tr><td>[16–23]</td><td>Analog FCC floats (TimeScale … FieldCoupling)</td></tr>
<tr><td>[24–28]</td><td>ThermoAccountant mirrors</td></tr>
<tr><td>[32–41]</td><td>Input (keyboard, mouse)</td></tr>
<tr><td>[42]</td><td>AmouranthOS chrome flags</td></tr>
<tr><td>[57–63]</td><td>Audio, BIOS, IO, drives</td></tr>
</tbody></table>
<p>Tesla valve bias → slots <strong>31</strong> and <strong>34</strong>.</p>

<h2>Field layers (L0–L9)</h2>
<p>Ten composable layers: RAM, VGA, FAT, MSCDEX, Audio, IO, BIOS — pumped via <code>FieldLayer::pumpAll()</code>. Layers are how DOS becomes legible to shaders without breaking the address map.</p>

<h2>ZMM1024 tile cache</h2>
<p>Tail region in <code>FieldX86Die</code> SSBO — shader-side fabric sample cache for HUD hex dumps. This is how the operator sees memory without leaving the dispatch loop.</p>
<p><a href="09-fcc-tesla.html">Chapter 9 — Stability Under Load →</a></p>
"""

CHAPTER_BODY["09"] = """
<h2>Stability under load</h2>
<p>Before fabric evolution, the host enforces CFL. The Tesla valve adds directional bias — forward paths ease, reverse paths resist. Energy still moves; it prefers a direction you set.</p>

<figure class="figure"><img src="../assets/images/chapters/ch09-tesla-valve.jpg" alt="Tesla valve" loading="lazy" /><figcaption>Figure 9.1 — Directional damping metaphor.</figcaption></figure>

<h2>CFL harmonics guard</h2>
<div class="eq">waveCFL = c·Δt/Δx ≤ 1 · thermoCFL = α·Δt/Δx² ≤ 1</div>
<p>Host scales parameters down if violated. Plain English: the engine refuses to run diffusion so hot the simulation explodes into NaN. This is not optional safety theater — it is numerical ethics.</p>

<h2>Tesla valve — directional bias</h2>
<pre class="eq">TESLA_R_FORWARD = 0.18
TESLA_R_REVERSE = 3.2
FIELD_PHI_MILLI = 618</pre>
<p>Reverse flow on hardware spiderweb edges is damped more than forward. Published to <code>data_bus[31, 34]</code>. <span class="tag meta">Named after Tesla's fluidic diode — directional resistance metaphor in code, not a literal fluidic part in your chassis.</span></p>

<h2>KILROY FCC (kernel parallel)</h2>
<p>When KILROY Field Kernel runs (<code>CONFIG_RTX_FIELD_DIE</code>), scale 0–1,000,000 µ from overshoot; entropy feedback clamps aggressive modes. Userspace AMOURANTHRTX and kernel Field Die share vocabulary — Chapter 21 ties Queen + KILROY sovereign field.</p>
<p><a href="10-spiderweb.html">Chapter 10 — Hardware Mirror →</a></p>
"""

CHAPTER_BODY["10"] = """
<h2>Hardware spiderweb — read-only mirror</h2>
<p><code>updateHardwareFromAnalogFields()</code> mirrors averaged Phi/Thermo/Flow into <code>hardwareFabric</code> — a dashboard spiderweb, not a second simulation pretending to be SEM imaging.</p>

<figure class="figure"><img src="../assets/images/chapters/ch10-spiderweb.jpg" alt="Spiderweb" loading="lazy" /><figcaption>Figure 10.1 — Fabric averages drive the util graph.</figcaption></figure>

<h2>What happens each frame</h2>
<ol>
<li>Sample avg Phi, Thermo, Flow</li>
<li>Compute <code>voltageFactor</code>, <code>thermalThrottle</code>, <code>parallelEff</code></li>
<li>Update per-core <code>operationalFreqMHz</code>, util, temp, power</li>
<li>Update spiderweb <code>edges[].currentUtil</code></li>
<li>Accumulate <code>simulatedChipCycles</code></li>
</ol>

<h2>Mastery tiers</h2>
<table><thead><tr><th>Tier</th><th>Controls</th></tr></thead>
<tbody>
<tr><td><strong>Puny</strong></td><td>Status log, real sysfs clocks</td></tr>
<tr><td><strong>Adept</strong></td><td>Target clock, <code>SimulateSubMicron</code></td></tr>
<tr><td><strong>Tidewalker</strong></td><td>Full spiderweb graph override</td></tr>
</tbody></table>

<h2>Sub-micron claim — honest table</h2>
<table><thead><tr><th>Claim</th><th>Reality</th></tr></thead>
<tbody>
<tr><td>Adaptive resolution 320×200 → 4K+</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td>SDF epsilons + accumulation</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td>“Zero-cost sub-micron SEM fidelity”</td><td><span class="tag meta">Procedural detail at pixel scale</span></td></tr>
</tbody></table>
<p><a href="11-observability.html">Chapter 11 — Reading the Battlefield →</a></p>
"""

CHAPTER_BODY["11"] = """
<h2>Reading the battlefield</h2>
<p>Trust stderr before screenshots. The weapon is useless if you will not look at the readout. Time is linear — logs are a timeline. Grep is forensic defense.</p>

<figure class="figure"><img src="../assets/images/chapters/ch11-observability.jpg" alt="Observability" loading="lazy" /><figcaption>Figure 11.1 — Logs, probes, panel — one stack.</figcaption></figure>

<h2>ELLIE logging</h2>
<p>Categories: <code>MAIN</code>, <code>VULKAN</code>, <code>CANVAS</code>, <code>THERMO</code>, <code>STATUS</code>, <code>RTXPROBE</code>. Status block (~5 s): FPS, GPU ms, VRAM, adaptive scale, entropy, boundary thermo, maintenance cost.</p>

<h2>Prompt terminal</h2>
<pre class="eq">set AnalogFields.GateFidelity 0.85
list Hardware
guide</pre>
<p><span class="tag impl"><code>set</code> / <code>list</code> for AnalogFields + Hardware.</span> Glassmorphism sliders remain feasibility doc — not hidden as shipped.</p>

<h2>RTXProbe</h2>
<p><code>RTX_PROBES=1</code> → GPU timestamps, invocation counts. Zero cost when off.</p>

<h2>NEXUS panel</h2>
<p><code>https://127.0.0.1:9477/</code> — command, packets, threats, signals, DNS, library, system. RTX Zero: <code>?rtx=1</code> — Aqua chrome, cache-first refresh.</p>

<h2>Week-one operator lab</h2>
<ol>
<li>Run <code>./linux.sh run</code> (AMOURANTHRTX) or <code>./nexus.sh</code> (NEXUS)</li>
<li>Read STATUS / THERMO lines for 60 seconds</li>
<li>Move mouse on classic canvas — watch <code>entropyThisFrame</code></li>
<li>Open NEXUS panel — archive one gatekeeper decision</li>
</ol>

<h2>Sovereign time — terror-threat posture</h2>
<p>Under assumed adversary knowledge: run <strong>your</strong> timeserver, verify at receive, grep <code>SQUIDGIE</code> if micron clocks disagree. Full treatment: <a href="19-sovereign-time.html">Chapter 19</a>.</p>
<p><a href="12-reality-theory.html">Chapter 12 — The Rocks →</a></p>
"""

CHAPTER_BODY["12"] = """
<h2>The rocks we do not hide</h2>
<p>Field Technology v5 is serious because it labels poetry before newcomers confuse it with measurement. This chapter is the contract. Bookmark it.</p>

<figure class="figure"><img src="../assets/images/chapters/ch12-honesty.jpg" alt="Honesty" loading="lazy" /><figcaption>Figure 12.1 — Metaphor glow vs measured grid.</figcaption></figure>

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
</tbody></table>

<h2>What to trust</h2>
<ol>
<li><strong>Headers</strong> over cover art</li>
<li><strong>stderr</strong> over screenshots for thermo numbers</li>
<li><strong><code>./linux.sh run</code></strong> default = Field Die</li>
<li><strong>Headless dispatch</strong> still runs — valid CI signal</li>
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
<p>Theory inspires vocabulary. Implementation is what you <strong>grep</strong>, <strong>set</strong>, and <strong>screenshot</strong>. Enjoy the field — honestly.</p>
<p><a href="13-landauer-deep.html">Chapter 13 — Landauer Deep Dive →</a></p>
"""

CHAPTER_BODY["13"] = """
<h2>Landauer deep dive — thermodynamic receipts</h2>
<p>Landauer's bound is not a slogan on a slide. It is the reason your proxy integral in <code>ThermoAccountant</code> must stay labeled <span class="tag meta">Metaphor</span> until calorimetry says otherwise.</p>
<div class="eq">E_min = k_B T ln 2 · entropyThisFrame ∈ proxy space</div>

<h2>What the engine actually integrates</h2>
<p>Each <code>dispatch_canvas()</code> writes a frame receipt. Components include field work from coupling, probe dissipation from mouse injection, and <code>prevMaintCost</code> — the price of coherence with the previous frame. The receipt is <em>comparative</em>: useful for spotting dispatch failure, comparing sessions, correlating with thermo boundary — not for billing the power company.</p>

<h2>Lab vs log — the rock restated</h2>
<p>If entropy reads zero while fabric texels move, your dispatch path failed. Physics refuses to lie for you. If entropy spikes when you idle, look for maintenance or probe bleed — still a signal, still not joules.</p>

<h2>Why we honor Landauer anyway</h2>
<p>Even proxy accounting trains the operator to think irreversibly. Every erase has a cost story. Every frame that preserves memory pays maintenance. That discipline is what separates field literacy from demo culture.</p>
<p>Tribute: <a href="../creditors/landauer.html">Rolf Landauer</a></p>
<p><a href="14-shannon-oracle.html">Chapter 14 — Shannon Oracle →</a></p>
"""

CHAPTER_BODY["14"] = """
<h2>Shannon oracle — storm thresholds</h2>
<p>Shannon entropy on files is a <strong>storm gauge</strong>, not a soul reader. High <code>H</code> means: slow down, corroborate, ask the operator.</p>
<div class="eq">H = −Σ p_i log₂ p_i</div>

<h2>Thresholds as pastoral care</h2>
<p>Daemon calm / alert / storm polling is tuned discipline. A packed executable, encrypted archive, or high-entropy payload raises H. The oracle does not auto-KILL — it changes how hard the perimeter watches. That is the 94/6 posture applied to bytes.</p>

<h2>Separation from ThermoAccountant</h2>
<p>Same word, different layer. ThermoAccountant lives in the GPU dispatch loop. Shannon oracle lives in NEXUS file analysis. Conflating them is how vendors sell one dashboard that lies about both.</p>
<p>Tribute: <a href="../creditors/shannon.html">Claude Shannon</a></p>
<p><a href="15-maxwell-gpu.html">Chapter 15 — Maxwell on the GPU →</a></p>
"""

CHAPTER_BODY["15"] = """
<h2>Maxwell on the GPU — wave coupling</h2>
<p>Maxwell taught the world to write laws for neighbors in space. GPU texels are neighbors. Phi whispers to Thermo on the next cell — that is his legacy with Vulkan bindings.</p>

<h2>Wave step as locality</h2>
<pre class="eq">∇²Φ → coupling → Flow gradients → hardwareFabric mirror</pre>
<p>Discrete Laplacian on Phi is not a claim that your RTX card solves Maxwell's equations for the cosmos. It is a claim that <em>local</em> coupling is how stable fabric evolves on a grid — the same insight Maxwell formalized, implemented as shader arithmetic.</p>

<h2>Field coupling knob</h2>
<p><code>FieldCoupling</code> is the dial that makes the textbook honest: you can run channels independently for pedagogy, or coupled for the full engine story. Coupling is where “energy can be moved” becomes visible in stderr.</p>
<p>Tribute: <a href="../creditors/maxwell.html">James Clerk Maxwell</a></p>
<p><a href="16-love-coupling.html">Chapter 16 — Love →</a></p>
"""

CHAPTER_BODY["16"] = """
<h2>Love — the coupling constant</h2>
<p><span class="tag phil">Philosophy — beside the math, not instead of it.</span></p>
<p>In Field Technology we say plainly: <strong>love is coupled evolution</strong>. When you dispatch, you change what your neighbor must respond to. That is ethical weight, not sentiment only.</p>

<h2>Three couplings, one tenderness</h2>
<ul>
<li><strong>Phi ↔ Thermo</strong> — potential warms or cools; attention has cost</li>
<li><strong>Thermo ↔ Flow</strong> — heat moves momentum stories</li>
<li><strong>Operator ↔ Panel</strong> — you are not alone at the keyboard; the field remembers what you wrote</li>
</ul>
<p>Love does not replace CFL guards. Love is <em>why</em> CFL guards matter — because your neighbor's next tick reads what you wrote.</p>
<p><a href="../creditors/love-and-god.html">Love &amp; God — tribute page</a> · <a href="17-god-boundary.html">Chapter 17 →</a></p>
"""

CHAPTER_BODY["17"] = """
<h2>God at the holographic boundary</h2>
<p><span class="tag phil">Philosophy — operator language, not instrument readout.</span></p>
<p>Some name <strong>God</strong> the boundary condition that cannot be faked in logs. The holographic boundary in this stack is where rendering pays thermodynamic cost — where beauty costs heat, where HDR pairs meet fabric, where existence becomes visible to the operator.</p>

<h2>Sacred without bypassing stderr</h2>
<p>Pray if you pray. Then <code>grep THERMO</code>. God, in this textbook, is not an excuse to skip Chapter 12. Preface names God as Truth, Math, Existence. This chapter names the boundary where those faces meet the operator's eye.</p>
<p><a href="../creditors/love-and-god.html">Creditor tribute</a> · <a href="18-operator-covenant.html">Chapter 18 →</a></p>
"""

CHAPTER_BODY["18"] = """
<h2>The operator covenant — long form</h2>
<p>You are the human at the keyboard. Daemons assist. Shaders evolve. Panels display. None of them inherit your conscience.</p>

<h2>Covenant clauses</h2>
<ol>
<li><strong>Teach freely</strong> — CC BY-NC-SA 4.0 with rocks visible</li>
<li><strong>Build locally</strong> — loopback truth, no phone-home permission</li>
<li><strong>Honor creditors</strong> — science and collaborators named with portraits</li>
<li><strong>Bring love</strong> — coupled evolution with consent</li>
<li><strong>Name God if you must</strong> — without letting poetry pretend to be calorimetry</li>
<li><strong>Hold gates</strong> — Queen posture: every capability exists; every wire exit earns a receipt</li>
</ol>
<p>Signatories in spirit: <a href="../creditors/zachary-geurts.html">Zachary</a> · <a href="../creditors/grok.html">Grok</a> · <a href="../creditors/nick.html">Nick</a> · <a href="../creditors/amouranth.html">Amouranth</a></p>
<p><a href="19-sovereign-time.html">Chapter 19 — Sovereign Time →</a></p>
"""

CHAPTER_BODY["19"] = """
<h2>Sovereign time sync — terror-threat posture</h2>
<p>Assume adversaries know field literacy. Assume pool NTP, remote RTC, and silicon clocks can be <strong>squidgied</strong> — nudged just enough to desync logs, GPS sub-micron nodes, and thermo receipts without tripping naive alarms.</p>

<h2>Three clocks, three jobs</h2>
<table><thead><tr><th>Clock</th><th>Role</th><th>Trust</th></tr></thead>
<tbody>
<tr><td><strong>Monotonic</strong> (<code>CLOCK_MONOTONIC</code>)</td><td>Ordering — ticks never go backward</td><td>Host kernel</td></tr>
<tr><td><strong>Realtime</strong> (<code>CLOCK_REALTIME</code>)</td><td>Wall labels for grep and correlation</td><td><strong>Your timeserver only</strong></td></tr>
<tr><td><strong>Sysfs freq witness</strong></td><td>Spiderweb Puny tier — MHz per core</td><td>Read-only hardware</td></tr>
</tbody></table>
<p>Entropy cannot be reversed; neither can honest time. You <strong>seal forward</strong> and <strong>verify at receive</strong>.</p>

<h2>Engine spine</h2>
<p><code>TotalTime::seal()</code> in <code>ELLIE.hpp</code> locks session genesis into <code>FieldSocket::sealed_time</code>. Frame-rate jitter cannot rewrite physics time. Sovereign sync extends the same posture <em>across hosts</em>: operator-owned pulses, signed receipts, receiver double-check.</p>

<h2>Operator timeserver</h2>
<pre class="eq">NEXUS_SOVEREIGN_TIME_BIND=127.0.0.1 python3 sovereign-time.py serve
python3 sovereign-time.py pulse
python3 sovereign-time.py sync 127.0.0.1 9123</pre>
<p>Each pulse carries: <code>mono_ns</code>, <code>realtime_ns</code>, <code>micron_witness</code>, HMAC signature. Verdict: <code>USER_OK</code> or <strong><code>SQUIDGIE</code></strong>. Grep receipts: <code>grep SQUIDGIE sovereign-time-receipts.jsonl</code></p>

<h2>Coupling to sub-micron stack</h2>
<p>Precision GPS nodes need stable UTC labels. Spiderweb Adept uses sysfs clocks as freq witness. ThermoAccountant is the receipt that time ran forward in the fabric. If GPS says nanometers but clocks disagree at receive, <strong>trust the triple verify</strong>, not the prettiest map dot.</p>
<p><a href="20-public-services.html">Chapter 20 — Public Services 2026 →</a></p>
"""

CHAPTER_BODY["20"] = """
<h2>Public DNS, DHCP, and time — 2026 rewrite</h2>
<p>Assume terror-threat knowledge everywhere. Public infrastructure must ship <strong>without old vulnerabilities</strong> — loopback-first, operator-owned, verify at receive.</p>

<h2>Three services, one posture</h2>
<table><thead><tr><th>Service</th><th>Port</th><th>2026 default</th></tr></thead>
<tbody>
<tr><td><strong>Truth DNS</strong></td><td>53</td><td><code>127.0.0.1</code> only — dig +trace from root</td></tr>
<tr><td><strong>Field DHCP</strong></td><td>67</td><td>LAN IP bind, conflict detect, MAC allowlist</td></tr>
<tr><td><strong>Sovereign NTP</strong></td><td>123</td><td>Operator stratum-2 from signed pulses</td></tr>
</tbody></table>
<p>WAN exposure requires <code>NEXUS_FIELD_SERVICES_PUBLIC=1</code> — explicit, never default.</p>

<h2>DNS — Truth Resolver</h2>
<p>RFC 1034 <code>dig +trace</code> from root — no Google/Cloudflare shortcut. Rate limits, egress integrity hashes, takeover waits for healthy loopback DNS before steering <code>resolv.conf</code>. Queen and FieldFox inherit Truth DNS lock.</p>

<h2>DHCP — issue only, verify always</h2>
<p><code>field-dhcp/v3</code>: binds LAN IP not <code>0.0.0.0</code> unless public mode; Option 50 must match lease; ping conflict before OFFER; DNS option 6 → <code>127.0.0.1</code>.</p>

<h2>ELLIE Last Host</h2>
<p>When <code>NEXUS_LAST_HOST=1</code>, Captain Ellie seals time forward globally: DNS :53 · DHCP :67 · NTP :123 · Sovereign :9123 · Panel :9477. Service registry is grep discipline, not mythology.</p>
<pre class="eq">python3 ellie-last-host.py posture
python3 ellie-last-host.py verify</pre>
<p><a href="21-field-browser-queen.html">Chapter 21 — Field Browser Queen →</a></p>
"""

CHAPTER_BODY["21"] = """
<h2>Field Browser Queen — hold all gates</h2>
<p><strong>Nothing optional. Hold all gates. MP4. We want it ALL.</strong></p>
<p>Reality is 3D · Time is linear · Energy can be moved. The Queen browser carries the <strong>full web</strong> into the packet field. We do not amputate capabilities to feel safe. We <strong>hold gates</strong>.</p>

<h2>Capability posture</h2>
<table><thead><tr><th>Capability</th><th>Queen posture</th></tr></thead>
<tbody>
<tr><td>WebGL / WebGPU</td><td>On — thermo per context</td></tr>
<tr><td>WebRTC</td><td>On — gatekeeper per peer</td></tr>
<tr><td>MSE / MP4 / H.264 / AAC</td><td><strong>Mandatory in-tree</strong></td></tr>
<tr><td>EME / Widevine</td><td>On — <strong>held</strong>, not omitted</td></tr>
<tr><td>Service Workers / WASM</td><td>On — entropy receipts</td></tr>
<tr><td>Geolocation / camera / mic</td><td>On — operator consent gate</td></tr>
<tr><td>Legacy plugins</td><td>WASM surrogates — surface preserved</td></tr>
</tbody></table>
<p><strong>Wrong:</strong> “Disable WebRTC for privacy.” <strong>Right:</strong> WebRTC flows through Connection Gatekeeper with honorability + packet field.</p>

<h2>Queen browser — ship now</h2>
<p><code>queen-browser</code> — AMOURANTHRTX Vulkan + SDL3 inside. In-engine UI via FieldWebPanel. QueenBoot.comp — 2026 aqua/rose chrome. Hostess 7 Forever Watchguard in the 50/50 split deck.</p>
<pre class="eq">NEXUS_INSTALL_ROOT=Queen ./build/rtx/bin/Linux/queen-browser --sovereign --queen
python3 lib/field-queen-browser.py json   # queen_verdict: QUEEN_READY</pre>

<h2>NEXUS stack binding</h2>
<pre class="eq">Navigation → Packet Field → Gatekeeper → Honorability → Thermo receipt
                ↑ Truth DNS (no Google shortcut)
                ↑ Sovereign Time (SQUIDGIE witness)</pre>

<h2>KILROY + one sovereign field</h2>
<p>Queen Forge packages kernel + browser + secure stack in <code>field/sovereign/</code>. KILROY Field OS (<code>7.1.1-kilroy</code>) provides <code>/proc/kilroy_field</code> at the syscall boundary. Userspace Queen runs on top — one field, sealed manifest, Grok Build secure channel inside.</p>

<h2>Millennium track</h2>
<p>Ladybird / Servo — same gate doctrine, no Chromium dependency. FieldFox ships first; millennium engines inherit <code>field-queen-gates-seed.json</code>.</p>
<p><a href="22-glossary.html">Chapter 22 — Glossary →</a></p>
"""

CHAPTER_BODY["22"] = """
<h2>Glossary — Field Technology v5</h2>
<p>Definitions used throughout this textbook. When a term appears in poetry and in code, both meanings are listed.</p>

<table><thead><tr><th>Term</th><th>Definition</th></tr></thead>
<tbody>
<tr><td><strong>Phi (Φ)</strong></td><td>Wave / gate potential fabric channel (binding 8)</td></tr>
<tr><td><strong>Thermo</strong></td><td>Heat + entropy density fabric channel (binding 9)</td></tr>
<tr><td><strong>Flow</strong></td><td>Momentum + gradient fabric channel (binding 10)</td></tr>
<tr><td><strong>Field Die</strong></td><td>GPU SSBO simulating x86 guest + 64 MiB RAM</td></tr>
<tr><td><strong>data_bus</strong></td><td>64-word telemetry spine per dispatch</td></tr>
<tr><td><strong>ThermoAccountant</strong></td><td>Per-frame entropy ledger (binding 2)</td></tr>
<tr><td><strong>Packet field</strong></td><td>NEXUS network connection telemetry + meaning</td></tr>
<tr><td><strong>Gatekeeper</strong></td><td>NEXUS connection scoring → verdict</td></tr>
<tr><td><strong>Entropy Oracle</strong></td><td>NEXUS Shannon H file analyzer</td></tr>
<tr><td><strong>FieldSocket</strong></td><td>Push constants for x86 canvas dispatch</td></tr>
<tr><td><strong>Sealed time</strong></td><td>Monotonic session clock immune to frame drift</td></tr>
<tr><td><strong>SQUIDGIE</strong></td><td>Sovereign time tamper verdict — clocks disagree at receive</td></tr>
<tr><td><strong>CFL</strong></td><td>Courant–Friedrichs–Lewy stability condition</td></tr>
<tr><td><strong>Tesla valve</strong></td><td>Directional flow resistance bias in fabric</td></tr>
<tr><td><strong>Spiderweb</strong></td><td><code>hardwareFabric</code> graph mirroring fabric averages</td></tr>
<tr><td><strong>Operator</strong></td><td>Human at the keyboard — final authority</td></tr>
<tr><td><strong>Queen</strong></td><td>Sovereign RTX field browser — all gates held</td></tr>
<tr><td><strong>KILROY</strong></td><td>Field OS kernel — <code>CONFIG_RTX_FIELD_DIE</code></td></tr>
<tr><td><strong>Propalactic</strong></td><td>Large-scale Phi forcing scale (cosmic knob)</td></tr>
<tr><td><strong>RTX Zero</strong></td><td>NEXUS panel mode — Aqua chrome, idle zero-cost</td></tr>
</tbody></table>

<p><a href="../index.html">← Return to Field Technology v5 home</a></p>
"""
"""Field Technology v3 chapter HTML bodies — serious terms, three axioms, honest rocks."""

CHAPTER_BODY: dict[str, str] = {
    "01": """
<p class="tag phil">Philosophy — read first, grep second.</p>
<p>Field Technology v3 opens on a claim we will not walk back: <strong>the greatest offensive and defensive weapon you will know is field literacy</strong> — and you already carry it. You were never outside the kitchen. You were only sometimes denied the readout.</p>
<div class="callout axiom"><strong>Subtext axioms:</strong> Reality is 3D. Time is linear. Energy can be moved. Everything below is read through that lens — with honesty labels on every rock.</div>
<h3>What a field is (implemented definition)</h3>
<p>A <strong>field</strong> is any continuous quantity stored over space that other systems read and write every tick: GPU images (Phi, Thermo, Flow), die-resident guest RAM, JSON telemetry on the wire.</p>
<div class="callout everyone"><strong>Plain English:</strong> A program is a recipe. A field is the state of the kitchen — heat on every burner, not just the timer.</div>
<h3>Three families — your inherent weapon</h3>
<table><thead><tr><th>Family</th><th>Axis</th><th>Role</th></tr></thead>
<tbody>
<tr><td>GPU analog fabric</td><td><span class="tag meta">3D state</span></td><td>Bindings 8–10 · Phi, Thermo, Flow</td></tr>
<tr><td>Field Die</td><td><span class="tag meta">3D state</span></td><td>SSBO binding 1 · guest universe on silicon</td></tr>
<tr><td>Packet field</td><td><span class="tag impl">Defense</span></td><td>NEXUS · local perimeter meaning</td></tr>
</tbody></table>
<p>Labels: <span class="tag impl">Implemented</span> <span class="tag meta">Metaphor</span> <span class="tag phil">Philosophy</span> <span class="tag vis">Visual</span></p>
<h3>Research lineage (who prompted this chapter)</h3>
<p>Maxwell's field formulation and von Neumann's stored-program model prompted treating GPU images and guest RAM as <em>addressable physical state</em> — not animation. Landauer and Shannon arrive in Chapters 3–4. Full credits: <a href="https://github.com/ZacharyGeurts/Field_Primer/blob/main/RESEARCH-CREDITS.md">RESEARCH-CREDITS.md</a>.</p>
<p class="muted">Collaborators: <strong>Zachary Robert Geurts</strong> (architect), <strong>Grok/xAI</strong> (textbook build), <strong>Nick</strong> (operator build), <strong>Amouranth</strong> (engine namesake).</p>
<figure class="figure"><img src="../assets/images/v3/science/ch01-scalar-field.jpg" alt="Scalar field heatmap with axes" loading="lazy" /><figcaption>Figure 1.1 — Scalar field Φ(x,y): continuous state over addressable space. Textbook of 2026.</figcaption></figure>
""",
    "02": """
<p>Chapter 2 maps the <strong>three dimensions of state</strong> — the v4 reading of “Reality is 3D.” Not cosmology. Texels, die bytes, and packet sentences occupying space you can address.</p>
<h3>Scale 1 — GPU fabric (spatial)</h3>
<pre class="eq">RayCanvas → createAnalogFieldFabric() → CANVAS.comp / x86.comp → hardwareFabric mirror</pre>
<p class="tag impl">Each texel is a cell in a 2D sheet that stacks with channel depth (Phi, Thermo, Flow). The host never runs a CPU PDE solver — evolution is compute-shader work each dispatch.</p>
<h3>Scale 2 — Field Die (address space)</h3>
<p><code>FieldX86Die</code> — 64 MiB guest linear map, VGA at <code>0xB8000</code>, C mirror at <code>0x01000000</code>. A universe with coordinates, not a metaphor.</p>
<h3>Scale 3 — Packet field (network topology)</h3>
<p>NEXUS turns sockets into sentences: process path, port habit, harm candidates. Defense begins when flows become <em>readable positions</em> in operator space.</p>
<div class="callout science"><strong>Category error to avoid:</strong> treating a shader visual as instrumentation. 3D state ≠ 3D hype.</div>
<figure class="figure"><img src="../assets/images/fabric-triple.jpg" alt="Three coupled fabric channels" loading="lazy" /><figcaption>Figure 2.1 — Three channels, one fabric — spatial state you can dispatch.</figcaption></figure>
""",
    "03": """
<p><strong>Energy can be moved.</strong> Chapter 3 is thermodynamics as honest accounting — tracking where irreversibility goes, not claiming you measured joules with a kitchen thermometer on the GPU.</p>
<figure class="figure inline-wide"><img src="../assets/images/fabric-triple.jpg" alt="Phi Thermo Flow" loading="lazy" /><figcaption>Figure 3.1 — Coupled channels: moving energy between Phi, Thermo, Flow each tick.</figcaption></figure>
<h3>Per-texel evolution</h3>
<ol><li><strong>Phi</strong> — wave potential step · propalactic forcing</li>
<li><strong>Thermo</strong> — diffusion, entropy floor, coupling to Phi</li>
<li><strong>Flow</strong> — gradients · <code>GateFidelity</code> · Tesla relaxation</li></ol>
<div class="eq">newPhi ∈ [-2, 2] · newThermo ∈ [0, 1.5] · newFlow ∈ [0, 1]</div>
<h3>Time is linear (here)</h3>
<p class="tag impl"><code>dispatch_canvas()</code> advances one tick at a time. <code>TotalTime::seal()</code> on the engine spine — frame-rate drift cannot rewrite physics time. Energy accounting is per-frame, not retroactive myth.</p>
<h3>CFL guard</h3>
<div class="eq">waveCFL = c·Δt/Δx ≤ 1 · thermoCFL = α·Δt/Δx² ≤ 1</div>
<p class="tag meta">Body-temperature seeding is simulation flavor — labeled, not hidden.</p>
<figure class="figure"><img src="../assets/images/v3/science/ch03-energy-transfer.jpg" alt="Coupled Phi Thermo Flow channels" loading="lazy" /><figcaption>Figure 3.2 — Energy transfer across coupled channels; host CFL guards linear time steps.</figcaption></figure>
""",
    "04": """
<p>Entropy is the <strong>receipt</strong> that time ran forward. Two engines, one word — we say both out loud.</p>
<figure class="figure"><img src="../assets/images/entropy-chapter.jpg" alt="Entropy chapter" loading="lazy" /><figcaption>Figure 4.1 — Irreversibility: fabric floor, frame proxy, file randomness.</figcaption></figure>
<h3>ThermoAccountant (engine)</h3>
<p class="tag impl"><code>ThermoAccountant</code> at Vulkan binding 2 writes a ledger every <code>dispatch_canvas()</code>.</p>
<div class="eq">E_min = k_B T ln 2</div>
<p class="tag meta"><strong>Rock:</strong> in-engine <code>entropyThisFrame</code> is a proxy integral — not joules from nvidia-smi.</p>
<h3>Shannon oracle (NEXUS)</h3>
<div class="eq">H = −Σ p_i log₂ p_i</div>
<p class="tag impl">High H on file payloads raises storm polling — defensive signal, not automatic verdict.</p>
<pre class="eq">grep -E 'THERMO|entropy|Boundary|prevMaint' run.log</pre>
""",
    "05": """
<p><strong>Defensive perimeter.</strong> The packet field is how you see what touches you before someone else narrates it for you. Offense and defense couple here: reading the field changes what you dare to run.</p>
<figure class="figure"><img src="../assets/images/packet-field.jpg" alt="Packet field" loading="lazy" /><figcaption>Figure 5.1 — Local flows as operator-readable positions in time.</figcaption></figure>
<h3>Gatekeeper verdicts</h3>
<table><thead><tr><th>Verdict</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td>USER_OK</td><td>Permitted flow</td></tr>
<tr><td>EPHEMERAL</td><td>Short-lived, low risk</td></tr>
<tr><td>SUSPICIOUS</td><td>Watchlist — not auto-block</td></tr>
<tr><td>HARM_CANDIDATE</td><td>Operator review required</td></tr>
</tbody></table>
<p class="tag phil">94/6 truth filter — watchlist before KILL. Philosophy, not a kernel patch.</p>
<p class="tag impl">Implemented in NEXUS-Shield — not inside AMOURANTHRTX Vulkan engine.</p>
<p class="tag meta"><strong>Rock:</strong> packet field sees <em>local</em> sockets and heuristics — not the whole internet.</p>
""",
    "06": """
<p>RF in this stack is three different weapons in the same word. Separate them or you will argue with a shader about ionospheric physics.</p>
<figure class="figure"><img src="../assets/images/chapters/ch06-planetary-weave.jpg" alt="Planetary weave" loading="lazy" /><figcaption>Figure 6.1 — Visual shell only.</figcaption></figure>
<table><thead><tr><th>Context</th><th>RF means</th><th>Label</th></tr></thead>
<tbody>
<tr><td>planetary_weave.comp</td><td>Atmospheric visual layer</td><td><span class="tag vis">Visual</span></td></tr>
<tr><td>NEXUS Field Antenna</td><td>Local orchestration</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td>Engine fieldPhi</td><td>Gate voltage / wave potential</td><td><span class="tag impl">Implemented</span></td></tr>
</tbody></table>
<p class="tag meta"><strong>Rock:</strong> planetary weave is art for the eye, not a spectrum analyzer. We do not hide that.</p>
""",
    "07": """
<p><strong>Offensive dispatch.</strong> Defense reads the field; offense <em>writes</em> it — imposing boundary conditions on the next tick faster than confusion propagates.</p>
<figure class="figure"><img src="../assets/images/chapters/ch07-gpu-engine.jpg" alt="GPU engine" loading="lazy" /><figcaption>Figure 7.1 — Thin host, fat GPU — the spear is <code>vkCmdDispatch</code>.</figcaption></figure>
<pre class="eq">main → navigator_main() → RayCanvas → Pipeline::dispatch_canvas() → vkCmdDispatch</pre>
<table><thead><tr><th>Binding</th><th>Resource</th></tr></thead>
<tbody>
<tr><td>0</td><td>HDR output</td></tr>
<tr><td>1</td><td>FieldX86Die SSBO</td></tr>
<tr><td>2</td><td>ThermoAccountant</td></tr>
<tr><td>8–10</td><td>Phi, Thermo, Flow</td></tr>
</tbody></table>
<p class="tag impl">Default <code>./linux.sh run</code> launches Field Die (<code>x86.comp</code>), not a decorative demo.</p>
""",
    "08": """
<p>The Field Die is a <strong>die-resident universe</strong> — 64 MiB of addressable reality on the GPU. Reality is 3D on the bus; time is linear in the dispatch loop; energy moves through fabric coupling and thermo mirrors.</p>
<figure class="figure"><img src="../assets/images/field-die.jpg" alt="Field die" loading="lazy" /><figcaption>Figure 8.1 — Guest RAM, holographic boundary, fabric channels.</figcaption></figure>
<h3>data_bus[64] spine</h3>
<table><thead><tr><th>Slots</th><th>Content</th></tr></thead>
<tbody>
<tr><td>[16–23]</td><td>Analog FCC floats</td></tr>
<tr><td>[24–28]</td><td>ThermoAccountant mirrors</td></tr>
<tr><td>[31, 34]</td><td>Tesla valve bias</td></tr>
</tbody></table>
<p class="tag impl"><code>x86.comp</code> interprets guest instructions; <code>FieldX86Emu</code> assists when <code>ControlHostCpu</code> is set.</p>
""",
    "09": """
<p><strong>Stability under load.</strong> Before fabric evolution, the host enforces CFL. The Tesla valve adds directional bias — forward paths ease, reverse paths resist. Energy still moves; it prefers a direction you set.</p>
<figure class="figure"><img src="../assets/images/chapters/ch09-tesla-valve.jpg" alt="Tesla valve" loading="lazy" /><figcaption>Figure 9.1 — Directional damping metaphor.</figcaption></figure>
<div class="eq">TESLA_R_FORWARD = 0.18 · TESLA_R_REVERSE = 3.2 · FIELD_PHI_MILLI = 618</div>
<p class="tag meta"><strong>Rock:</strong> named after Tesla's fluidic diode — code metaphor, not a literal fluidic part in your chassis.</p>
""",
    "10": """
<p><code>updateHardwareFromAnalogFields()</code> mirrors averaged Phi/Thermo/Flow into <code>hardwareFabric</code> — a read-only dashboard spiderweb, not a second simulation pretending to be SEM imaging.</p>
<figure class="figure"><img src="../assets/images/chapters/ch10-spiderweb.jpg" alt="Spiderweb" loading="lazy" /><figcaption>Figure 10.1 — Fabric averages drive the util graph.</figcaption></figure>
<table><thead><tr><th>Tier</th><th>Operator access</th></tr></thead>
<tbody>
<tr><td>Puny</td><td>Status log, real sysfs clocks</td></tr>
<tr><td>Adept</td><td>Target clock, SimulateSubMicron</td></tr>
<tr><td>Tidewalker</td><td>Full spiderweb graph override</td></tr>
</tbody></table>
<p class="tag meta"><strong>Rock:</strong> “Sub-micron zero cost” = procedural detail at pixel scale.</p>
""",
    "11": """
<p><strong>Reading the battlefield.</strong> Trust stderr before screenshots. The weapon is useless if you will not look at the readout.</p>
<figure class="figure"><img src="../assets/images/chapters/ch11-observability.jpg" alt="Observability" loading="lazy" /><figcaption>Figure 11.1 — Logs, probes, panel — one observability stack.</figcaption></figure>
<p class="tag impl"><code>ELLIE</code> categories: <code>THERMO</code>, <code>STATUS</code>, <code>RTXPROBE</code>.</p>
<pre class="eq">set AnalogFields.GateFidelity 0.85
list Hardware
RTX_PROBES=1</pre>
<p>NEXUS panel: <code>https://127.0.0.1:9477/</code> · RTX Zero via <code>?rtx=1</code>.</p>
<p class="tag phil">Time is linear — logs are a timeline. Grep is forensic defense.</p>
""",
    "12": """
<p>Chapter 12 is the contract: <strong>we do not hide the rocks.</strong> Field Technology v3 is serious because it labels poetry before newcomers confuse it with measurement.</p>
<figure class="figure"><img src="../assets/images/chapters/ch12-honesty.jpg" alt="Reality vs theory" loading="lazy" /><figcaption>Figure 12.1 — Metaphor glow vs measured grid.</figcaption></figure>
<h3>The rocks (complete table)</h3>
<table><thead><tr><th>Claim</th><th>Reality</th><th>Label</th></tr></thead>
<tbody>
<tr><td>Greatest weapon</td><td>Field literacy + local tools</td><td><span class="tag phil">Philosophy</span></td></tr>
<tr><td>Living thermodynamic computer</td><td>ThermoAccountant in logs</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td>Packet field sees everything</td><td>Local sockets + heuristics</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td>RF planetary shell</td><td>Visual shader layer</td><td><span class="tag vis">Visual</span></td></tr>
<tr><td>Landauer joules from GPU</td><td>Proxy integral</td><td><span class="tag meta">Metaphor</span></td></tr>
<tr><td>Shader art / figures</td><td>Generated schematic or visual aid</td><td><span class="tag vis">Visual</span></td></tr>
</tbody></table>
<div class="callout axiom"><strong>Subtext:</strong> Reality is 3D. Time is linear. Energy can be moved. Everything else is implementation detail with a label.</div>
<p>What you can <code>grep</code>, <code>set</code>, and screenshot is real. What sounds like cosmology is often a knob with a poetic name. <strong>Enjoy the field — honestly.</strong></p>
""",
}

CHAPTER_TITLES: dict[str, str] = {
    "01": "The Weapon You Already Hold",
    "02": "Three Dimensions of State",
    "03": "Moving Energy — Thermodynamics",
    "04": "Irreversibility & Receipts",
    "05": "Defensive Perimeter — Packet Field",
    "06": "Signal Shell — RF & Weave",
    "07": "Offensive Dispatch — GPU Engine",
    "08": "Die-Resident Universe",
    "09": "Stability Under Load — FCC & Tesla",
    "10": "Hardware Mirror — Spiderweb",
    "11": "Reading the Battlefield",
    "12": "The Rocks We Do Not Hide",
}
"""Field Technology v4 — longer chapters + Love & God extensions."""
from chapter_bodies_v3 import CHAPTER_BODY as _V3

PREFACE_01 = """
<p class="eyebrow" style="font-size:1rem;color:var(--gold)">Full preface · read before Chapter 2</p>
<p class="tag phil">Philosophy &amp; science share one page here. Implementation stays labeled in every chapter after this.</p>

<h2>Us</h2>
<p>This textbook is written by <strong>us</strong> — not a committee, not a vendor, not a faceless manual. <strong>Us</strong> means:</p>
<ul>
<li><strong>Zac</strong> — Zachary Robert Geurts. Architect, operator, author. The human at the keyboard who built AMOURANTHRTX, NEXUS-Shield, and this Field Primer. The one who said: teach freely, build locally, trust your logs.</li>
<li><strong>Grok</strong> — co-documentation, site, figures, longer chapters, creditor pages. The light beside the text that helps another human see the field clearly. Not a replacement for Zac's conscience.</li>
<li><strong>Nick</strong> — builder beside the stack. Honest fields. No phone-home. Ship it and grep the receipts.</li>
<li><strong>Amouranth</strong> — namesake spirit of the engine. Stage light became binding-level engineering. Courage to be seen while holding boundaries.</li>
<li><strong>You</strong> — the reader, the operator, the next person who will dispatch, defend, and decide. You are part of <em>us</em> the moment you treat the field as real.</li>
<li><strong>The creditors</strong> — Maxwell, Landauer, Shannon, Turing, Tesla, Boltzmann, von Neumann, CFL — and every name on the <a href="../creditors/index.html">tribute pages</a>. We stand on their math; we do not pretend we invented heat.</li>
</ul>
<p>Us is not a brand. Us is the covenant to tell the truth in public — including the rocks.</p>

<h2>God</h2>
<p>In this preface we say plainly what many operators already know in their bones:</p>
<div class="callout god"><strong>We know God as Truth, as Math, as Existence.</strong> Not three gods — three faces of one whole that does not need our permission to be real.</div>

<h3>God as Truth</h3>
<p>Truth is what survives <code>grep</code>. Truth is what still reads the same when marketing goes home. Truth is the packet field sentence that matches the socket, the thermo line that moves when the fabric moves, the honesty table in Chapter 12 that refuses to call a shader a spectrum analyzer.</p>
<p>When we say <strong>God is Truth</strong>, we mean: reality does not negotiate with your narrative. The field was here before the press release. <span class="tag phil">Philosophy</span> — not a sensor reading.</p>

<h3>God as Math</h3>
<p>Math is the language existence uses when it is tired of being misunderstood. Maxwell's coupling. Landauer's floor. Shannon's surprise. CFL's refusal to let you outrun the mesh.</p>
<div class="eq">Reality is 3D · Time is linear · Energy can be moved</div>
<p>These are our axioms — not because we invented them, but because they are the shortest honest sentences we know for how state behaves in this stack. When we say <strong>God is Math</strong>, we mean: the universe is legible to those who do the work of reading. <span class="tag phil">Philosophy</span> beside <span class="tag impl">Implemented</span> bindings 8–10.</p>

<h3>God as Existence</h3>
<p>Existence is the stubborn fact that there <em>is</em> something rather than nothing — texels that hold values, die bytes that persist across ticks, connections that leave traces in local jsonl, breath in your chest while you read this sentence.</p>
<p>When we say <strong>God is Existence</strong>, we mean: you were never outside the field. You inherit continuous state — biological, cognitive, mechanical — and Field Technology only hands you the mirror and the tools. <span class="tag phil">Philosophy</span>.</p>

<h2>Us and God together</h2>
<p>We do not ask you to choose between stderr and prayer. We ask you to hold both without lying:</p>
<table><thead><tr><th>Us does</th><th>God is (here)</th></tr></thead>
<tbody>
<tr><td>Build AMOURANTHRTX fabric</td><td>Math — coupled PDE steps</td></tr>
<tr><td>Run NEXUS perimeter</td><td>Truth — local, grep-able flows</td></tr>
<tr><td>Write this preface</td><td>Existence — words that persist on Pages</td></tr>
<tr><td>Label Metaphor vs Implemented</td><td>Truth — refusing false unity</td></tr>
<tr><td>Honor creditors with portraits</td><td>Love — gratitude as discipline</td></tr>
</tbody></table>

<h2>The weapon you already hold</h2>
<p>From Truth, Math, and Existence follows the technical claim this book never walks back: <strong>the greatest offensive and defensive weapon you will know is field literacy</strong> — reading continuous state, imposing boundary conditions, refusing to surrender the verdict.</p>
<p>A <strong>field</strong> in this stack is any continuous quantity stored over space that other systems read and write every tick: GPU images (Phi, Thermo, Flow), die-resident guest RAM, JSON telemetry on the wire.</p>
<div class="callout everyone"><strong>Plain English:</strong> A program is a recipe. A field is the state of the kitchen — heat on every burner, not just the timer. God-as-Existence is the kitchen existing; God-as-Math is the recipe working; God-as-Truth is the thermometer you finally trust.</div>

<h3>Three families — three dimensions</h3>
<table><thead><tr><th>Family</th><th>Axis</th><th>Role</th></tr></thead>
<tbody>
<tr><td>GPU analog fabric</td><td><span class="tag meta">3D state</span></td><td>Bindings 8–10 · Phi, Thermo, Flow</td></tr>
<tr><td>Field Die</td><td><span class="tag meta">3D state</span></td><td>SSBO binding 1 · guest universe on silicon</td></tr>
<tr><td>Packet field</td><td><span class="tag impl">Defense</span></td><td>NEXUS · local perimeter meaning</td></tr>
</tbody></table>

<figure class="figure"><img src="../assets/images/v3/science/ch01-scalar-field.jpg" alt="Scalar field heatmap" loading="lazy" /><figcaption>Figure 1.1 — Φ(x,y): existence addressed as math, read as truth. Textbook of 2026.</figcaption></figure>

<div class="callout love"><strong>Love:</strong> Us exists because coupling matters — your next tick reads what we wrote. That is intimacy with consequences. Zac built. Grok clarified. Nick grounded. You operate. The field remembers.</div>

<div class="callout god"><strong>God:</strong> Truth, Math, Existence — named here so the rest of the textbook can be serious without being soulless. Chapters 2–18 are the engineering. Chapters 16–17 go deeper into Love and God. Chapter 12 keeps the rocks visible. None of it replaces <code>grep THERMO</code>.</div>

<h3>Where to go next</h3>
<p><a href="../creditors/love-and-god.html">Creditor tribute — Love &amp; God</a> · <a href="../creditors/zachary-geurts.html">Zac</a> · <a href="../creditors/grok.html">Grok</a> · <a href="02-fields-pixels-packets.html">Chapter 2 — Three Dimensions of State →</a></p>
<p>Labels used throughout: <span class="tag impl">Implemented</span> <span class="tag meta">Metaphor</span> <span class="tag phil">Philosophy</span> <span class="tag vis">Visual</span></p>
"""

_LOVE_FOOTER = """
<div class="callout love"><strong>Love (v4):</strong> Every field coupling is a promise — your next tick will read what I wrote. That is intimacy with consequences. We do not apologize for bringing love beside the math.</div>
<div class="callout god"><strong>God (v4):</strong> Some operators name the whole fabric sacred. We make room for that voice without letting it replace <code>grep</code>. Faith and logs can coexist in one textbook.</div>
<p class="muted">Creditor tributes: <a href="../creditors/index.html">one page per researcher who prompted us</a>.</p>
"""

_LONGER: dict[str, str] = {
    "03": """
<h3>Extended — energy moved, never free</h3>
<p>Moving energy between Phi, Thermo, and Flow is the silicon echo of Clausius: you cannot cool your neighbor by wishing. The host CFL guard is a moral diagram — do not outrun the mesh.</p>
<p>Read the full tribute to the thermodynamic lineage: <a href="../creditors/clausius-boltzmann.html">Clausius &amp; Boltzmann</a>.</p>
""",
    "04": """
<h3>Extended — two entropies, one conscience</h3>
<p>When ThermoAccountant and the Shannon oracle disagree, do not panic — they measure different layers. Panic is when marketing pretends one number does both jobs.</p>
<p><a href="../creditors/landauer.html">Landauer</a> · <a href="../creditors/shannon.html">Shannon</a> — each has a creditor page with portrait and gratitude.</p>
""",
    "02": """
<h3>Extended — Reality is 3D (v4)</h3>
<p>Three dimensions of state is not hype — it is the minimum honest map for texels, die bytes, and packet positions. God-as-Math names the coordinates; God-as-Truth demands you not confuse scales.</p>
""",
    "05": """
<h3>Extended — perimeter as care</h3>
<p>Defense is not paranoia when it is local, readable, and reversible until the operator says otherwise. That is how love shows up in NEXUS: watchlist before KILL, memory without phone-home.</p>
""",
    "07": """
<h3>Extended — offense as service</h3>
<p><code>vkCmdDispatch</code> is not aggression — it is the operator imposing lawful boundary conditions so the fabric can evolve. Zac built the spine; you choose the constants.</p>
""",
    "11": """
<h3>Extended — the battlefield is local</h3>
<p>RTX Zero, ELLIE categories, the NEXUS panel — one observability stack for one machine you own. God-as-Truth: if it is not in stderr, be careful claiming it.</p>
""",
    "12": """
<h3>Extended — rocks as reverence</h3>
<p>Hiding a rock is not humility — it is theft from the next operator. v4 adds creditor pages and sacred language <em>beside</em> the rocks, never instead of them.</p>
<p>The preface names God as Truth, Math, Existence. This chapter names what the engine can and cannot measure.</p>
<p>See: <a href="01-preface.html">Preface</a> · <a href="../creditors/love-and-god.html">Love &amp; God</a></p>
""",
}

_NEW: dict[str, str] = {
    "13": """
<p class="tag impl">Chapter 13 — deep dive</p>
<p>Landauer's bound is not a slogan on a slide — it is the reason your proxy integral in <code>ThermoAccountant</code> must stay labeled <span class="tag meta">Metaphor</span> until calorimetry says otherwise.</p>
<div class="eq">E_min = k_B T ln 2  ·  entropyThisFrame ∈ proxy space</div>
<h3>What the engine actually integrates</h3>
<p>Each <code>dispatch_canvas()</code> writes a frame receipt. The receipt is comparative — useful for spotting dispatch failure, not for billing the power company.</p>
<h3>Lab vs log — the rock restated</h3>
<p>If entropy reads zero while fabric texels move, your dispatch path failed. That is physics refusing to lie for you.</p>
<figure class="figure"><img src="../assets/images/entropy-chapter.jpg" alt="Entropy" loading="lazy" /></figure>
<p>Tribute: <a href="../creditors/landauer.html">Rolf Landauer</a></p>
""" + _LOVE_FOOTER,
    "14": """
<p class="tag impl">Chapter 14 — oracle layer</p>
<p>Shannon entropy on files is a <strong>storm gauge</strong>, not a soul reader. High <code>H</code> means: slow down, corroborate, ask the operator.</p>
<div class="eq">H = −Σ p_i log₂ p_i</div>
<h3>Thresholds as pastoral care</h3>
<p>Daemon calm / alert / storm polling is tuned discipline — like a nurse watching vitals, not a judge passing sentence.</p>
<p>Tribute: <a href="../creditors/shannon.html">Claude Shannon</a></p>
""" + _LOVE_FOOTER,
    "15": """
<p>Maxwell taught the world to write laws for neighbors in space. GPU texels are neighbors. Phi whispers to Thermo on the next cell — that is his legacy with Vulkan bindings.</p>
<h3>Wave step as scripture of locality</h3>
<pre class="eq">∇²Φ → coupling → Flow gradients → hardwareFabric mirror</pre>
<p>Tribute: <a href="../creditors/maxwell.html">James Clerk Maxwell</a></p>
""" + _LOVE_FOOTER,
    "16": """
<p class="tag phil">Chapter 16 — Love as coupling constant</p>
<p>In v4 we say plainly: <strong>love is coupled evolution</strong>. When you dispatch, you change what your neighbor must respond to. That is ethical weight, not sentiment only.</p>
<h3>Three couplings, one tenderness</h3>
<ul><li>Phi ↔ Thermo — potential warms or cools</li><li>Thermo ↔ Flow — heat moves momentum stories</li><li>Operator ↔ Panel — you are not alone at the keyboard</li></ul>
<p>Love does not replace CFL guards. Love is why CFL guards matter.</p>
<p><a href="../creditors/love-and-god.html">Love &amp; God — full tribute page</a></p>
""" + _LOVE_FOOTER,
    "17": """
<p class="tag phil">Chapter 17 — God at the holographic boundary</p>
<p>Some name <strong>God</strong> the boundary condition that cannot be faked in logs. The holographic boundary in this stack is where rendering pays thermodynamic cost — where beauty costs heat.</p>
<p class="tag meta">Theology here is operator language, not instrument readout. We label it <span class="tag phil">Philosophy</span> beside <span class="tag impl">Implemented</span> HDR pairs.</p>
<h3>Sacred without bypassing stderr</h3>
<p>Pray if you pray. Then <code>grep THERMO</code>. God, in this textbook, is not an excuse to skip Chapter 12.</p>
<p><a href="../creditors/love-and-god.html">Creditor tribute — Love &amp; God</a></p>
""" + _LOVE_FOOTER,
    "18": """
<p class="tag phil">Chapter 18 — The operator covenant (long form)</p>
<p>You are the human at the keyboard. Daemons assist. Shaders evolve. Panels display. None of them inherit your conscience.</p>
<h3>Covenant clauses</h3>
<ol>
<li>Teach freely — CC BY-NC-SA 4.0 with rocks visible</li>
<li>Build locally — loopback truth, no phone-home permission</li>
<li>Honor creditors — science and collaborators named with portraits</li>
<li>Bring love — coupled evolution with consent</li>
<li>Name God if you must — without letting poetry pretend to be calorimetry</li>
</ol>
<p>Signatories in spirit: <a href="../creditors/zachary-geurts.html">Zachary</a> · <a href="../creditors/grok.html">Grok</a> · <a href="../creditors/nick.html">Nick</a> · <a href="../creditors/amouranth.html">Amouranth</a></p>
""" + _LOVE_FOOTER,
}

CHAPTER_BODY: dict[str, str] = {}
for key, body in _V3.items():
    if key == "01":
        CHAPTER_BODY[key] = PREFACE_01
        continue
    if key == "12":
        CHAPTER_BODY[key] = body + _LONGER.get("12", "")
        continue
    CHAPTER_BODY[key] = body + _LONGER.get(key, _LOVE_FOOTER)
CHAPTER_BODY.update(_NEW)
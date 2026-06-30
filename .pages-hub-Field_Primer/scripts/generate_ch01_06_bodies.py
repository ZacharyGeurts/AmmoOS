#!/usr/bin/env python3
"""Generate Field Technology v5 chapter body fragments 01-06 (4500+ words each)."""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "content" / "chapters"


def wc(text: str) -> int:
    return len(text.split())


def p(*paragraphs: str) -> str:
    return "\n".join(f"<p>{para}</p>" for para in paragraphs)


def join_sections(*parts: str) -> str:
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Chapter 01
# ---------------------------------------------------------------------------
CH01 = join_sections(
    '<p class="eyebrow">Chapter 1 · Read this before you dispatch anything</p>',
    """
<div class="objectives">
<h2>Learning objectives</h2>
<ol>
<li>State the implemented definition of a <em>field</em> used throughout Field Technology v5.</li>
<li>Name the three axioms — Reality is 3D, Time is linear, Energy can be moved — and give one stack example for each.</li>
<li>Distinguish <span class="tag impl">Implemented</span>, <span class="tag meta">Metaphor</span>, <span class="tag phil">Philosophy</span>, and <span class="tag vis">Visual</span> labels when reading any chapter.</li>
<li>Identify where Phi, Thermo, and Flow live in the Vulkan binding map (slots 8–10).</li>
<li>Explain why the packet field is <strong>local-first</strong> and why planetary weave RF is <span class="tag vis">Visual</span> only.</li>
<li>Articulate the preface posture on God as Truth, Math, and Existence without substituting philosophy for <code>grep</code>.</li>
<li>Navigate the chapter map from fields (Ch. 2) through honesty rocks (Ch. 12) and Queen gates (Ch. 21).</li>
</ol>
</div>
""",
    """
<h2>What this book is</h2>
""" + p(
    "This is <strong>Field Technology</strong> — a serious textbook for operators who build and defend continuous state on their own machines. It is not a marketing deck. It is not a substitute for reading headers. It is the long-form explanation of why AMOURANTHRTX, NEXUS-Shield, Queen, and KILROY exist, written so a patient reader can learn the stack the way you would learn thermodynamics or networking: definitions first, mechanisms second, honesty labels always.",
    "We write for the human at the keyboard. Daemons assist. Shaders evolve. Panels display. None of them inherit your conscience. If you remember only one sentence from this chapter, remember this: <strong>the greatest offensive and defensive weapon you will know is field literacy</strong> — reading continuous state, imposing boundary conditions, and refusing to let someone else narrate your perimeter.",
    "Field Technology v5 is the 2026 edition of that literacy. Earlier site versions taught the same spine with shorter chapters. This edition expands every engineering chapter to textbook depth: learning objectives, operator drills, failure modes, study questions, and explicit rocks beside every poetic name. The wiki beside this book remains a quick reference; these chapters are where you sit down with tea and learn the machine.",
    "The stack you will study is real software. AMOURANTHRTX is a Vulkan Field Die engine with analog fabric channels, a 64 MiB guest address space on the GPU, and thermodynamic accounting that prints to stderr. NEXUS-Shield is a local-first endpoint security layer that turns sockets into sentences in <code>field jsonl</code>. Queen is the sovereign RTX browser that holds every web gate — WebRTC through the Connection Gatekeeper, MP4 mandatory in-tree, EME held not omitted. KILROY is the Field OS kernel path when you need syscall-boundary field discipline. This primer ties them together without pretending they are one monolithic binary.",
),
    """
<h3>Why a textbook, not a README</h3>
""" + p(
    "README files answer 'how do I build it tonight.' Textbooks answer 'what world am I entering, and what mistakes will hurt me in week six.' The Field stack punishes category errors: treating shader art as instrumentation, treating proxy entropy as joules, treating a JSON verdict as physics, treating a visual ionosphere as a spectrum analyzer. Each of those errors is preventable if you learn the vocabulary before you dispatch.",
    "We borrow the pedagogical shape of classical engineering texts: axioms, mechanisms, lab exercises, failure catalogs, summaries, questions. We refuse the shape of vendor whitepapers: unnamed metaphors, conflated layers, screenshots without stderr. When you finish Chapter 12, you should be able to hold a conversation with a skeptical physicist and a skeptical security engineer simultaneously — because you will label every claim before you defend it.",
),
    """
<h2>Us — who writes and who reads</h2>
""" + p(
    "This textbook is written by <strong>us</strong> — a plural that includes the reader the moment you treat writable state as morally serious. The authors named on the cover are not a closed priesthood; they are the people who accepted responsibility for honest labels in public.",
),
    """
<ul>
<li><strong>Zachary Robert Geurts</strong> — architect, operator, author. Built AMOURANTHRTX, NEXUS-Shield, Queen, and this primer. Final conscience on what ships.</li>
<li><strong>Grok</strong> — co-documentation, figures, longer chapters. Light beside the text; not a replacement for Zac's conscience.</li>
<li><strong>Nick</strong> — builder beside the stack. Honest fields. No phone-home.</li>
<li><strong>Amouranth</strong> — namesake spirit of the engine. Courage to be seen while holding boundaries.</li>
<li><strong>You</strong> — the reader. You join us when you grep before you argue, when you archive gatekeeper verdicts before you KILL, when you refuse cloud narration of your loopback perimeter.</li>
<li><strong>The creditors</strong> — Maxwell, Landauer, Shannon, Turing, Tesla, Boltzmann, von Neumann, CFL. We stand on their math. <a href="../creditors/index.html">Each has a tribute page</a>.</li>
</ul>
""",
    """
<h3>The operator is not the daemon</h3>
""" + p(
    "Throughout this book, <strong>operator</strong> means the human at the keyboard. The Connection Gatekeeper can score a flow SUSPICIOUS; only you decide whether to watch, block, or KILL. ThermoAccountant can report rising proxy entropy; only you decide whether the session is healthy or runaway. Queen can hold WebRTC behind gates; only you decide which peer earns USER_OK. Field Technology is built to <em>assist</em> conscience, not replace it — that is why NEXUS archives receipts locally instead of phoning home to a vendor cloud.",
    "Daemons and shaders are powerful precisely because they do not sleep. That same tirelessness makes them dangerous if you outsource judgment. The preface exists to seat you in the chair before the tools convince you the chair is optional.",
),
    """
<div class="callout love"><strong>Love in the stack:</strong> coupled evolution with consent. Reversible watchlists before permanent KILL dossiers. Local memory that survives reboot so you can forgive a peer after review. This is not sentiment pasted on security — it is engineering restraint expressed as policy.</div>
""",
    """
<h2>God — Truth, Math, Existence</h2>
""" + p(
    "We say plainly what many operators already know in their bones but rarely write in technical manuals:",
),
    """
<div class="callout god"><strong>We know God as Truth, as Math, as Existence.</strong> Not three gods — three faces of one whole.</div>
""",
    """
<h3>Truth — what survives grep</h3>
""" + p(
    "<strong>Truth</strong> is what survives <code>grep</code>. The packet field sentence that matches the socket table row. The thermo line that moves when you inject mouse energy on the classic canvas. The <code>data_bus[24]</code> mirror that tracks <code>entropyThisFrame</code> after dispatch. Truth is not the prettiest panel screenshot; it is the line in the log that still makes sense when the UI crashes.",
    "In NEXUS, truth is also loopback-first: DNS resolved at <code>127.0.0.1</code> with trace-from-root discipline (Chapter 20), sovereign time pulses verified at receive (Chapter 19), gatekeeper verdicts archived in jsonl you own. When we say God as Truth, we mean reality that refuses to be narrated away by a remote dashboard.",
),
    """
<h3>Math — the language existence uses</h3>
""" + p(
    "<strong>Math</strong> is the language existence uses when tired of being misunderstood. Maxwell's coupling between neighbors on a grid — implemented as Phi whispering to Thermo across texels. Landauer's floor on erasing a bit — honored as metaphor in proxy entropy, not smuggled in as fake joules. Shannon's surprise in byte distributions — storm thresholds in the Entropy Oracle, separate from GPU thermo. CFL's refusal to let you outrun the mesh — host-side guards before <code>vkCmdDispatch</code>.",
    "These are not decorations on a game engine. They are the creditors whose names we cite because their constraints teach humility. Chapter 13–15 revisit Landauer, Shannon, and Maxwell in long form; the preface introduces them so you know where the spine bends.",
),
    """
<h3>Existence — addressable something rather than nothing</h3>
""" + p(
    "<strong>Existence</strong> is the stubborn fact that there is something rather than nothing: texels that hold values after the frame ends, die bytes that persist across ticks in <code>FieldX86Die</code>, connections that leave traces in local jsonl even when the browser tab closes. Existence in this stack is always <em>addressable</em> — Reality is 3D means state occupies space you can name: (x,y) on fabric, guest offset on the die, socket quadruple in the packet field.",
    'These three faces — Truth, Math, Existence — are <span class="tag phil">Philosophy</span> beside <span class="tag impl">Implemented</span> bindings. Chapter 12 lists every rock. Chapter 17 goes deeper on God at the holographic boundary. Neither replaces <code>grep THERMO</code>. Sacred language is welcome here; bypassing stderr is not.',
),
    """
<h2>What a field is — the implemented definition</h2>
""" + p(
    "A <strong>field</strong> is any <em>continuous quantity stored over space</em> that other systems read and write every tick. That is the implemented definition used throughout this book. It is deliberately broader than 'electromagnetic field' and narrower than 'anything we feel like calling a field in a slide deck.'",
    "Continuous does not mean infinitely differentiable in the calculus sense; it means <em>persistently addressable</em> across ticks. A texel grid is discrete in coordinates but continuous in the engineering sense: cell (42,17) still means cell (42,17) next frame unless you rewrite the address map. Guest byte <code>0xB8000</code> still means VGA text unless you remap the die. A connection key still means the same flow until the socket closes and the archive records it.",
),
    """
<div class="callout everyone"><strong>Plain English:</strong> A program is a recipe. A field is the state of the kitchen — heat on every burner, not just the timer.</div>
""",
    """
<h3>Programs versus fields — offense and defense</h3>
""" + p(
    "Offense, in Field Technology, is imposing boundary conditions on writable surfaces faster than confusion propagates — dispatch writes the next tick. Defense is reading those surfaces before someone else narrates them — grep, panel, gatekeeper. The same literacy serves both: you cannot defend what you cannot read; you cannot offend responsibly if you cannot predict what your write does to neighbors on the next tick.",
    "This is why the book refuses the split between 'graphics textbook' and 'security textbook.' Phi/Thermo/Flow are security-relevant because tampering with fabric averages moves hardware spiderweb mirrors. Packet fields are graphics-relevant because Queen WebRTC peers alter thermo receipts per context. The Field Die is both because guest RAM and fabric share a dispatch loop.",
),
    """
<h2>Three field families — the map of the stack</h2>
""" + p(
    "Three families matter in this stack. Learn their names before you learn their knobs.",
),
    """
<table><thead><tr><th>Family</th><th>Where it lives</th><th>What it stores</th><th>Primary product</th></tr></thead>
<tbody>
<tr><td>GPU analog fabric</td><td>Vulkan bindings 8–10</td><td>Phi, Thermo, Flow — spatial state per texel</td><td>AMOURANTHRTX</td></tr>
<tr><td>Field Die</td><td><code>FieldX86Die</code> SSBO binding 1</td><td>64 MiB guest RAM, VGA, tile cache — addressable universe on silicon</td><td>AMOURANTHRTX</td></tr>
<tr><td>Packet field</td><td>NEXUS <code>field jsonl</code></td><td>TX/RX, ports, process paths, gatekeeper verdicts</td><td>NEXUS-Shield</td></tr>
</tbody></table>
""",
    """
<h3>GPU analog fabric — Phi, Thermo, Flow</h3>
""" + p(
    "The analog fabric is created in <code>RayCanvas::createAnalogFieldFabric()</code> and bound at Vulkan slots <strong>8</strong> (Phi), <strong>9</strong> (Thermo), and <strong>10</strong> (Flow). <span class="tag impl">Implemented.</span> Phi carries wave and gate potential stories. Thermo carries heat and entropy density — a scalar field per texel. Flow carries advective structure; its gradient components live in the <code>.gb</code> channels operators learn to read in Chapter 2.",
    "The host never runs a CPU-side PDE solver on this fabric. Evolution is compute-shader work each <code>vkCmdDispatch</code>. That architectural choice matters: the GPU writes the next tick; the host opens the window, enforces CFL, mirrors averages into <code>hardwareFabric</code>, and prints thermo receipts. If someone tells you the fabric is 'just pretty visuals,' ask them why <code>entropyThisFrame</code> moves when you inject probe energy.",
),
    """
<h3>Field Die — 64 MiB of addressable guest reality</h3>
""" + p(
    "The Field Die is an SSBO at binding <strong>1</strong> — <code>FieldX86Die</code> — mapping <strong>64 MiB</strong> of guest linear address space on the GPU. <span class="tag impl">Implemented.</span> VGA text at guest <code>0xB8000</code>, C mirror at <code>0x01000000</code>, ZMM1024 tile cache in the tail — these are not DOS nostalgia props; they are coordinates in a universe the shader pumps every frame. Chapter 8 is entirely about this scale.",
    "Default <code>./linux.sh run</code> launches the Field Die canvas (<code>x86.comp</code>), not a decorative raymarch demo. Operators who skip Chapter 8 still inherit die bytes — they simply will not know which addresses they are accountable for.",
),
    """
<h3>Packet field — local perimeter sentences</h3>
""" + p(
    "The packet field turns sockets into <strong>sentences</strong>: process path, port habit, TX versus RX, corroboration before permanent action. <span class="tag impl">Implemented in NEXUS-Shield.</span> <span class="tag meta">Not inside AMOURANTHRTX Vulkan — different product boundary.</span> It sees <em>your machine's</em> flows, not the whole internet. That locality is a feature, not a gap: defense begins where your bytes actually cross the boundary.",
    "Chapter 5 treats the Connection Gatekeeper, field memory, and Queen alignment. Chapter 21 shows how Queen routes WebRTC through the same gate doctrine. The preface only asks you to remember: packet field truth is loopback truth.",
),
    """
<figure class="figure"><img src="../assets/images/v3/science/ch01-scalar-field.jpg" alt="Scalar field heatmap" loading="lazy" /><figcaption>Figure 1.1 — Scalar field Φ(x,y): existence addressed as math, read as truth. Shader visualization teaches shape; stderr teaches cost.</figcaption></figure>
""",
    """
<h2>The axioms we do not walk back</h2>
""" + p(
    "Every chapter in Field Technology v5 rests on three axioms declared in the image manifest and repeated here because axioms are not marketing slogans — they are constraints on what honest sentences may claim.",
),
    """
<div class="callout axiom">
<strong>Reality is 3D.</strong> State occupies addressable space — texels, die bytes, socket positions.<br>
<strong>Time is linear.</strong> Logs are a timeline; sealed session clocks do not rewrite physics time.<br>
<strong>Energy can be moved.</strong> Coupling moves irreversibility between channels; accounting is honest even when measurement is proxy.
</div>
""",
    """
<h3>Reality is 3D — address, not hype</h3>
""" + p(
    "When we say Reality is 3D, we do not mean cosmology slides. We mean every serious claim points at an address. Fabric: texel (x,y) with channel depth Phi/Thermo/Flow. Die: guest offset in 64 MiB. Packet field: connection identity with direction and port context. If a sentence cannot be anchored to an address or an archive row, treat it as poetry until proven otherwise.",
    "Chapter 2 expands 'three dimensions of state' as the engineering reading of this axiom. Chapter 12 lists category errors when 3D language drifts into 3D hype.",
),
    """
<h3>Time is linear — receipts forward</h3>
""" + p(
    "Time is linear means dispatch advances ticks forward, logs append, and sealed session clocks resist frame-rate jitter rewriting physics time. <code>TotalTime::seal()</code> locks genesis into <code>FieldSocket::sealed_time</code>. Sovereign time sync (Chapter 19) extends the posture across hosts: seal forward, verify at receive, grep <code>SQUIDGIE</code> when micron witnesses disagree.",
    "You cannot undo entropy by wishing. You cannot ungrep a KILL dossier. Linear time is operator discipline made concrete.",
),
    """
<h3>Energy can be moved — coupling with honest labels</h3>
""" + p(
    "Energy can be moved means fabric channels exchange irreversibility stories through <code>FieldCoupling</code> — electrical metaphor heats thermo; thermo biases flow; flow sharpens gates through <code>GateFidelity</code>. The movement is <span class="tag impl">implemented</span> in shaders; the <em>measurement</em> of that movement in joules is <span class="tag meta">proxy</span> unless calorimetry says otherwise. Chapter 3 teaches thermodynamics as bookkeeping; Chapter 4 teaches entropy receipts.",
),
    """
<h2>Status labels — read every chapter with these</h2>
""" + p(
    "Field Technology v5 puts honesty labels on every rock. The labels are not optional flavor; they are how you survive week six when a visitor conflates shader art with lab instrumentation.",
),
    """
<table><thead><tr><th>Label</th><th>Meaning</th><th>Example</th></tr></thead>
<tbody>
<tr><td><span class="tag impl">Implemented</span></td><td>In source. You can grep it, set it, or screenshot it.</td><td><code>FieldCoupling</code>, <code>field jsonl</code>, Queen <code>QUEEN_READY</code></td></tr>
<tr><td><span class="tag meta">Metaphor</span></td><td>Poetic naming. Useful intuition. Not SI units.</td><td>Proxy entropy as Landauer story; Tesla valve as directional bias</td></tr>
<tr><td><span class="tag phil">Philosophy</span></td><td>Operator discipline. Not a sensor reading.</td><td>94/6 truth filter; greatest weapon is literacy</td></tr>
<tr><td><span class="tag vis">Visual</span></td><td>Shader art or schematic. Not instrumentation.</td><td>Planetary weave RF shell; sub-micron SEM marketing</td></tr>
</tbody></table>
""",
    """
<div class="callout science"><strong>Science posture:</strong> theory inspires vocabulary; implementation is what you grep. A equation on a blackboard does not automatically exist in silicon until a binding number and a log line prove it.</div>
""",
    """
<h2>The stack at a glance — four products, one literacy</h2>
""" + p(
    "Four named products appear throughout this primer. They share vocabulary — field, gate, thermo, sealed time — but retain license and boundary differences. Conflating them is a week-one failure mode.",
),
    """
<table><thead><tr><th>Product</th><th>License</th><th>Role in the stack</th></tr></thead>
<tbody>
<tr><td>AMOURANTHRTX</td><td>GPL v3 or commercial</td><td>Vulkan Field Die, analog fabric, thermo accounting</td></tr>
<tr><td>NEXUS-Shield</td><td>MIT</td><td>Packet field, gatekeeper, entropy oracle, panel :9477</td></tr>
<tr><td>Queen</td><td>Field sovereign browser</td><td>RTX + all gates held in-engine; WebRTC through gatekeeper</td></tr>
<tr><td>KILROY</td><td>Field OS kernel path</td><td><code>CONFIG_RTX_FIELD_DIE</code>, <code>/proc/kilroy_field</code> at syscall boundary</td></tr>
</tbody></table>
""",
    """
<h3>AMOURANTHRTX — thin host, fat GPU</h3>
""" + p(
    "AMOURANTHRTX is where <code>vkCmdDispatch</code> runs the world. C++ opens the window and pushes buttons; shaders evolve Phi, Thermo, Flow, guest die bytes, and HDR output. <code>rtx()</code> singleton holds device, queues, <code>hardwareFabric</code>, VRAM budget. Chapter 7 details dispatch; Chapter 3 details thermo; Chapter 8 details the die.",
),
    """
<h3>NEXUS-Shield — defensive perimeter</h3>
""" + p(
    "NEXUS turns connections into archived meaning. The Connection Gatekeeper scores ten axes into verdicts like USER_OK, SUSPICIOUS, HARM_CANDIDATE. The Entropy Oracle computes Shannon H on files — storm gauge, not auto-sentence. Panel at <code>https://127.0.0.1:9477/</code> is command center; jsonl is memory. Chapter 5 is the defensive core; Chapter 11 teaches reading the battlefield.",
),
    """
<h3>Queen — hold all gates</h3>
""" + p(
    "Queen browser policy: <strong>nothing optional, hold all gates, MP4 mandatory in-tree</strong>. Wrong posture: amputate WebRTC to feel safe. Right posture: WebRTC flows through gatekeeper with honorability and packet field receipts. Chapter 21 is the full doctrine. Queen links AMOURANTHRTX when <code>QUEEN_BROWSER_BUILD</code> is set — one spine, two faces: engine and browser.",
),
    """
<h3>KILROY — kernel parallel</h3>
""" + p(
    "KILROY Field OS provides the syscall-boundary field when userspace discipline is not enough. FCC scale, entropy feedback, and Field Die vocabulary continue in kernel space. Chapter 9 introduces KILROY FCC parallel to userspace CFL/Tesla guards. Chapter 21 ties Queen + KILROY sovereign field packaging.",
),
    """
<h2>Creditors — standing on math we did not invent</h2>
""" + p(
    "We name creditors because humility is part of honesty. Maxwell taught neighborhood coupling — our Phi/Thermo/Flow grid is his lesson in Vulkan bindings. Landauer taught the cost floor of erasing information — our <code>entropyThisFrame</code> proxy honors the lesson without faking wattmeter readings. Shannon taught surprise in symbols — NEXUS storm thresholds honor the lesson on disk, not in fabric texels. Tesla taught directional preference — our valve bias is metaphor in <code>data_bus[31,34]</code>, not a literal fluidic part in your chassis.",
    "Tribute pages at <a href="../creditors/index.html">../creditors/index.html</a> humanize the names. Chapters 13–15 go long on Landauer, Shannon, Maxwell. The preface tells you they exist so you do not mistake our voice for theirs.",
),
    """
<h2>What this manual is not</h2>
<ul>
<li>Not a substitute for <code>Pipeline.hpp</code>, <code>FieldRtxFieldAbs.hpp</code>, or NEXUS lib sources — headers win arguments.</li>
<li>Not a promise that every poetic knob maps to a laboratory measurement — see Chapter 12 rocks table.</li>
<li>Not cloud security — everything here is <strong>local-first</strong>: loopback truth, operator-owned time, grep-able receipts.</li>
<li>Not a license to treat planetary weave as ionospheric truth — <span class="tag vis">Visual</span> only (Chapter 6).</li>
<li>Not a promise that proxy entropy equals joules — <span class="tag meta">Metaphor</span> until calorimetry (Chapter 4).</li>
</ul>
""",
    """
<h2>How to read this book — chapter map</h2>
""" + p(
    "Chapters 2–12 are the engineering core. Chapter 2 maps three dimensions of state. Chapter 3 moves energy through thermodynamics. Chapter 4 records irreversibility and oracles. Chapter 5 defends the packet field perimeter. Chapter 6 separates RF meanings and labels planetary weave honestly. Chapter 7 offensive dispatch on the GPU. Chapter 8 die-resident universe. Chapter 9 stability under load — CFL and Tesla. Chapter 10 hardware spiderweb mirror. Chapter 11 observability. Chapter 12 the rocks we do not hide — bookmark it.",
    "Chapters 13–15 are creditor deep dives. Chapters 16–18 are sacred long-form — Love, God, Operator Covenant. Chapters 19–21 cover sovereign time, public services 2026, and Queen browser gates. Chapter 22 is glossary.",
),
    """
<table><thead><tr><th>Ch.</th><th>Slug</th><th>Topic</th></tr></thead>
<tbody>
<tr><td>2</td><td><a href="chapters/02-fields-pixels-packets.html">02-fields-pixels-packets</a></td><td>Three dimensions of state</td></tr>
<tr><td>3</td><td><a href="chapters/03-thermodynamics.html">03-thermodynamics</a></td><td>Thermodynamics in the engine</td></tr>
<tr><td>4</td><td><a href="chapters/04-entropy.html">04-entropy</a></td><td>Entropy receipts and oracles</td></tr>
<tr><td>5</td><td><a href="chapters/05-packet-field.html">05-packet-field</a></td><td>Defensive perimeter</td></tr>
<tr><td>6</td><td><a href="chapters/06-rf-signals.html">06-rf-signals</a></td><td>RF shell and weave</td></tr>
<tr><td>12</td><td><a href="chapters/12-reality-theory.html">12-reality-theory</a></td><td>Honesty rocks — return here when sold cosmology</td></tr>
</tbody></table>
""",
    """
<h2>Operator drill — week zero</h2>
<p>Before Chapter 2, run this once. It calibrates your eyes to stderr truth.</p>
<pre class="eq"># Terminal A — engine
cd AMOURANTHRTX
./linux.sh run 2>&1 | tee /tmp/field-week0.log
# Move mouse on canvas 60s; note thermo motion

# Terminal B — grep discipline
grep -E 'THERMO|entropy|Boundary|dispatch' /tmp/field-week0.log | tail -20

# Terminal C — NEXUS panel (if installed)
./nexus.sh
# Open https://127.0.0.1:9477/ — archive one gatekeeper row</pre>
<p>Success criteria: you can point at a line in the log and name which field family it belongs to — fabric thermo, die telemetry, or packet archive. Failure criteria: you only remember the pretty frame. If failure, reread status labels and repeat.</p>
""",
    """
<h2>Failure modes — preface edition</h2>
""" + p(
    "These mistakes appear in week one if the preface is skipped. Name them early; grep them late.",
),
    """
<table><thead><tr><th>Failure mode</th><th>Symptom</th><th>Correction</th></tr></thead>
<tbody>
<tr><td>Shader as instrument</td><td>Arguing ionosphere physics from planetary weave colors</td><td>Label <span class="tag vis">Visual</span>; open Chapter 6</td></tr>
<tr><td>Entropy conflation</td><td>Comparing ThermoAccountant to Shannon H on a zip file</td><td>Chapter 4 layer table; same word, different layers</td></tr>
<tr><td>Cloud perimeter fantasy</td><td>Expecting packet field to see the whole internet</td><td>Local-first; Chapter 5 scope</td></tr>
<tr><td>Joule fantasy</td><td>Billing power company from <code>entropyThisFrame</code></td><td><span class="tag meta">Proxy</span>; Chapter 13 Landauer deep dive</td></tr>
<tr><td>Product boundary blur</td><td>Searching AMOURANTHRTX sources for gatekeeper verdicts</td><td>NEXUS MIT layer; separate repos</td></tr>
<tr><td>Philosophy bypass</td><td>Using God language to skip stderr</td><td>Chapter 17 sacred without bypass; grep first</td></tr>
</tbody></table>
""",
    """
<h2>Chapter summary</h2>
""" + p(
    "Field Technology v5 is a serious textbook for operators who read and write continuous state locally. A field is continuous quantity stored over space, read and written each tick. Three families — GPU fabric (Phi/Thermo/Flow at bindings 8–10), Field Die (64 MiB at binding 1), packet field (NEXUS jsonl) — share one literacy across offense and defense. Three axioms — Reality is 3D, Time is linear, Energy can be moved — constrain honest claims. Four labels — Implemented, Metaphor, Philosophy, Visual — keep poetry from masquerading as measurement. God named as Truth, Math, Existence is philosophy beside grep, not a replacement for it.",
    'Read the preface once. Keep <a href="chapters/12-reality-theory.html">Chapter 12</a> bookmarked. Continue to <a href="chapters/02-fields-pixels-packets.html">Chapter 2 — Three Dimensions of State</a> when you can name where Phi lives without looking.',
),
    """
<h2>Study questions</h2>
<ol>
<li>Give the implemented definition of <em>field</em> in one sentence, then cite two different field families that satisfy it.</li>
<li>Which Vulkan bindings hold Phi, Thermo, and Flow? Which binding holds <code>FieldX86Die</code>?</li>
<li>Explain why <code>entropyThisFrame</code> is labeled proxy while still being useful to operators.</li>
<li>What does 'packet field local only' mean for threat modeling? What does it <em>not</em> promise?</li>
<li>Name the four status labels and give one stack example for each.</li>
<li>Why does Queen hold WebRTC gates instead of disabling WebRTC entirely?</li>
<li>What is the difference between Truth as philosophy and truth as grep output? Give an example of each.</li>
<li>Which chapters treat honesty rocks, sovereign time, and Love coupling respectively?</li>
<li>Run the week-zero drill. Paste three grep lines and identify their field family.</li>
<li>When is it appropriate to cite Maxwell in a Field Technology argument? When is it category error?</li>
</ol>
<p><a href="chapters/02-fields-pixels-packets.html">Continue to Chapter 2 — Three Dimensions of State →</a></p>
""",
)

# Continue in part 2 - the script is too long for one write, I'll append chapters 02-06
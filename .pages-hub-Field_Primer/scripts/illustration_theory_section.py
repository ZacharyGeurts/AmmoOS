"""Illustration theory block for Chapter 01 — returns HTML fragment."""

ILLUSTRATION_THEORY_HTML = """
<h2>Illustration theory — how many pictures hold interest without lying</h2>
<p>This textbook is deliberately illustrated. Not wallpaper — <strong>signaled mechanism figures</strong> placed where cognitive science says dual channels help: roughly one visual anchor every thousand words, each tied to a claim you can grep.</p>

<h3>Leonardo — drawing is thinking (<em>disegno</em>)</h3>
<p>Leonardo da Vinci’s notebooks are not doodle margins. They are laboratory records: bird flight beside force arrows, heart valves beside pulse questions, city plans beside hydraulic riddles. He interleaved <em>word and image blocks</em> because some truths do not survive prose alone — spatial relations, flows, proportions. Walter Isaacson’s reading of the codices matches what operators see in AMOURANTHRTX: you do not understand the Field Die until you have drawn the bus slots once.</p>
<p>Leonardo’s lesson for v5: <strong>one sketch per idea worth remembering</strong>. Not one stock photo per page. Not decoration. A figure should answer a question the paragraph posed. His sheets rarely exceed three major diagrams per spread — density without chaos.</p>

<h3>Dürer and the print tradition — reproducible truth</h3>
<p>Albrecht Dürer carried <em>disegno</em> into reproducible plates: perspective machines, proportion grids, rhinoceros from second-hand reports labeled honestly. The lesson for Field Technology: a figure must survive copy-paste into slides, wiki, and mobile reader without losing the mechanism. Vector clarity where possible; when we use generated art, captions carry the grep hook the pixels cannot.</p>

<h3>Arnheim — perception is cognition</h3>
<p>Rudolf Arnheim argued we think in shapes, tensions, and maps — not as illustration of thought, but as thought itself. Textbooks that strip all pictures force the visual channel to reconstruct diagrams from prose, spending working memory on decoding instead of organizing. Field Technology gives you the map when the map is honest: fabric triple, die linear address strip, gatekeeper axis table with a perimeter figure beside it.</p>

<h3>Paivio — dual coding before Mayer</h3>
<p>Allan Paivio’s dual coding theory (1971) predates modern multimedia experiments: verbal and nonverbal codes are separate but linked. When both encode the <em>same</em> concept — “binding 2 ThermoAccountant” in text beside a labeled SSBO strip — recall and transfer improve. When they encode different things — pretty nebula beside entropy prose — the link breaks. v5 captions exist to weld the codes together.</p>

<h3>Sweller — cognitive load and the density ceiling</h3>
<p>John Sweller’s cognitive load theory names three loads: <strong>intrinsic</strong> (the idea itself), <strong>extraneous</strong> (bad layout), and <strong>germane</strong> (schema-building effort). Decorative figures are pure extraneous load — they steal capacity from the mechanism you came to learn. That is why the hard ceiling in our table is one signaled figure per ~600 words: beyond that, even honest diagrams compete for attention on a phone screen.</p>

<h3>Kosslyn — how diagrams must be built</h3>
<p>Stephen Kosslyn’s rules for effective graphics: salience matches importance, labels sit near what they name, complexity grows in layers (overview first, detail second). Field Primer figures follow this — perimeter map before jsonl grammar; fabric triple before coupling PDE intuition. A figure that needs a paragraph to find its subject fails the Kosslyn test.</p>

<h3>Tufte — data-ink and chartjunk</h3>
<p>Edward Tufte’s <em>data-ink ratio</em> is Chapter 12 in design form: every pixel should earn its place toward the truth. Chartjunk — gratuitous grids, mystery gradients, 3D chrome — is the visual cousin of unlabeled metaphor. Our <span class="tag vis">Visual</span> tag is Tufte-compliant honesty: the ink is beautiful, the caption admits it is not instrumentation.</p>

<h3>Mayer — dual channel, coherence, signaling</h3>
<p>Richard Mayer’s multimedia learning research (UC San Diego) synthesizes the experiments into guardrails:</p>
<ul>
<li><strong>Dual channel:</strong> eyes and inner voice process pictures and words in parallel — when they <em>align</em>, retention rises.</li>
<li><strong>Limited capacity:</strong> too many figures per screen compete — extraneous load (Sweller) wins.</li>
<li><strong>Coherence:</strong> weed decorative images; every figure must serve a learning objective.</li>
<li><strong>Signaling:</strong> captions name the mechanism and the honesty label — not “pretty GPU.”</li>
<li><strong>Spatial contiguity:</strong> labels on the figure, not in a distant sidebar — critical on mobile reader.</li>
<li><strong>Segmenting:</strong> one figure per conceptual beat, not one giant poster per chapter.</li>
</ul>
<p>Mayer’s seductive-details warning is Chapter 12’s rock in visual form: ionosphere beauty on planetary weave is interesting but irrelevant to instrumentation — label <span class="tag vis">Visual</span> and move on.</p>
<figure class="figure"><img src="../assets/images/chapters/ch01-dual-channel.jpg" alt="Dual channel alignment diagram" loading="lazy" /><figcaption>Figure 1.2a — Paivio/Mayer dual channel: visual and verbal codes must encode the same mechanism.</figcaption></figure>

<h3>Queen robot brain — Hostess 7 folds prose to SDF imaging</h3>
<p><span class="tag meta">Metaphor.</span> Field Browser Queen carries an in-process <strong>robot-brain architecture</strong> (operator shorthand — not a government program deliverable); Hostess 7 Forever Watchguard is the angel layer that <strong>owns self data storage</strong>. She ingests each 1000–1200 word Mayer beat, renders an SDF brain-imaging plate (distance-field topology, not bitmap rent), and decides: integrate with shortened caption, reimage via imagine-learn, toss when the plate fully encodes the beat, SDL-store grep blocks for the Graphics window, or keep dual-channel prose+plate. Series-of-series neural nets (perception → truth gates → fusion) recall plates through vision OCR — brain imaging as Super Intelligence doctrine, not fMRI.</p>

<h3>Ware and modern visualization — glance versus study</h3>
<p>Colin Ware separates <em>at-a-glance</em> features (color hue for category) from <em>study</em> features (fine text, exact numbers). Textbook figures here are study figures — you lean in, grep the caption, cross-check stderr. That is why we favor 16:9 mechanism plates over icon salad.</p>

<h3>Field Technology v5 density standard</h3>
<p>Homework condensed from the stack above: Leonardo and Dürer set craft; Arnheim, Paivio, and Kosslyn set structure; Sweller and Mayer set limits; Tufte sets honesty. The numbers below are how v5 applies them to a grep-first engineering book at ~250–300 words per printed page.</p>
<table><thead><tr><th>Metric</th><th>Target</th><th>Rationale</th></tr></thead>
<tbody>
<tr><td>Words per signaled figure</td><td>900–1,200</td><td>~1 figure per 3–4 printed pages; holds interest without clutter</td></tr>
<tr><td>Figures per ~5,000-word chapter</td><td>4–6 interior + 1 on-the-way hero</td><td>Dual coding without seductive overload</td></tr>
<tr><td>Figures per printed page</td><td>0.25–0.35 (max 0.5)</td><td>~1 figure every 3–4 pages; Mayer segmenting on paper</td></tr>
<tr><td>Maximum density</td><td>1 figure / 600 words</td><td>Hard ceiling — beyond this, extraneous load wins (Sweller)</td></tr>
<tr><td>Minimum density</td><td>1 figure / 1,500 words</td><td>Below this, wall-of-text fatigue on mobile reader</td></tr>
<tr><td>Caption rule</td><td>Mechanism + label</td><td>“Figure 7.2 — Binding 2 ThermoAccountant” not “Cool tech”</td></tr>
<tr><td>Spread rule</td><td>≤3 major diagrams</td><td>Leonardo notebook discipline — more becomes chartjunk (Tufte)</td></tr>
</tbody></table>
<div class="callout science"><strong>Operator translation:</strong> At 5,000 words you should meet 4–6 mechanism figures you can cite in stderr homework; the on-the-way hero is orientation, not one of the six. If a chapter falls under 1 figure per 1,500 words, add a signaled plate. If it exceeds 1 per 600, split the section or demote decoration.</div>
<p>Figures in this edition mix creditor lineage (Maxwell’s neighborhood on a grid), generated mechanism art (coupling, perimeter, sovereign time), and photographs of honest labels. When a figure is <span class="tag vis">Visual</span> only, the caption says so before your eyes sell you cosmology.</p>
<figure class="figure"><img src="../assets/images/chapters/ch01-illustration-theory.jpg" alt="Leonardo notebook meets field grid" loading="lazy" /><figcaption>Figure 1.2b — <em>Disegno</em> meets dispatch: sketch and prose interleaved; mechanism figures beside grep receipts.</figcaption></figure>
"""


def inject_illustration_theory(body: str, key: str) -> str:
    if key != "01" or "Illustration theory" in body:
        return body
    marker = '</div>'
    idx = body.find('class="objectives"')
    if idx == -1:
        return ILLUSTRATION_THEORY_HTML.strip() + "\n\n" + body
    close = body.find(marker, idx)
    if close == -1:
        return body
    insert_at = close + len(marker)
    return body[:insert_at] + "\n\n" + ILLUSTRATION_THEORY_HTML.strip() + "\n\n" + body[insert_at:]
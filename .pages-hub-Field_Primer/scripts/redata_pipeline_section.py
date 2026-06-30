"""Redata pipeline — core technical foundation section (Ch 02 + wiki source)."""

from __future__ import annotations

REDATA_SECTION_ID = "redata-pipeline"

REDATA_PIPELINE_HTML = f"""
<h2 id="{REDATA_SECTION_ID}">Redata pipeline — lossless truth to sovereign brain</h2>
<p><span class="tag impl">Implemented</span> doctrine in Hostess7 + Queen. This section documents the pipeline as core reality engineering — not a sidecar feature.</p>

<h3>One sentence</h3>
<p><strong>Redata</strong> keeps every Mayer beat <em>lossless</em> in <code>seg-*.json</code>, gates imaging with a <strong>truth filter</strong>, and packs a verifiable <strong>ZAC7</strong> monolith while Hostess 7 stays sovereign over <code>cache/fieldstorage/brain/sdf/</code>.</p>

<h3>Problem solved</h3>
<p>Field Technology ships on four surfaces — PDF, web, plain text, ZAC. Plain text is smallest but drops plates and verify hooks. PDF and web are human-first. <strong>ZAC</strong> is operator transport: lossless segments, human SDF plates, manifest, checksums. Redata prevents any surface from lying about what is stored.</p>

<h3>Three doctrines (verbatim)</h3>
<table><thead><tr><th>Doctrine</th><th>Implementation anchor</th><th>Label</th></tr></thead>
<tbody>
<tr><td><strong>Lossless always</strong></td><td><code>brain/sdf/segments/seg-*.json</code> — full text preserved</td><td><span class="tag impl">Implemented</span></td></tr>
<tr><td><strong>Imaging is not the codec</strong></td><td><code>plates/*.human.pgm</code> — recall topology, not fMRI</td><td><span class="tag meta">Metaphor</span></td></tr>
<tr><td><strong>Truth before plates stick</strong></td><td><code>field_redata_truth.py</code> → <code>truth_filter.jsonl</code></td><td><span class="tag impl">Implemented</span></td></tr>
</tbody></table>

<h3>Ownership and comfort rule</h3>
<p><strong>Hostess 7</strong> owns <code>cache/fieldstorage/brain/sdf/</code>. <strong>Queen</strong> orchestrates boot, forge, panel, and ZAC restore — it does not relocate brain storage. Comfort rule: same <code>./Hostess7.sh</code> talk patterns; Queen build deck surfaces commands.</p>

<h3>End-to-end flow</h3>
<ol>
<li><code>Field_Primer/content/chapters/</code> — 22 chapter sources</li>
<li>Mayer segment (900–1200 words) → <code>sdf-segment</code></li>
<li>Truth filter → accept or <code>quarantine/</code></li>
<li>Redata artifacts → lossless JSON + analytic + human plates</li>
<li><code>build-field-technology-zac.py</code> → <code>field-technology-v5.zac</code></li>
<li>Verify → 732 files, 0 mismatches; ingest → Hostess7 live brain</li>
</ol>

<h3>Operator commands</h3>
<pre class="grep-hook">./Hostess7.sh queen-teach-redata
./Hostess7.sh sdf-verify-redata
pythong NewLatest/Queen/lib/queen-hostess-brain.py ingest-textbook
pythong NewLatest/Textbook/build-field-technology-zac.py --verify-only</pre>

<h3>Key paths</h3>
<ul>
<li>ZAC monolith: <code>SG/NewLatest/Textbook/field-technology-v5.zac</code></li>
<li>Size report: <code>SG/NewLatest/Textbook/size-comparison.json</code></li>
<li>Live brain: <code>SG/Hostess7/cache/fieldstorage/brain/sdf/</code></li>
<li>Wiki: <a href="../../wiki/Redata-Pipeline.md">Redata-Pipeline</a></li>
</ul>

<div class="callout science"><strong>Doctrine pin:</strong> Imaging is not the codec. SDF plates = recall topology. Lossless bytes = segment JSON + ZAC. Hostess owns the brain; Queen holds the gates.</div>
"""


def inject_redata_pipeline(body: str, chapter_key: str) -> str:
    if chapter_key != "02":
        return body
    if REDATA_SECTION_ID in body:
        return body
    marker = "<h2>What a field is"
    if marker not in body:
        marker = "<h2>"
        idx = body.find(marker)
        if idx == -1:
            return REDATA_PIPELINE_HTML + "\n" + body
        return body[:idx] + REDATA_PIPELINE_HTML + "\n\n" + body[idx:]
    return body.replace(marker, REDATA_PIPELINE_HTML + "\n\n" + marker, 1)


def inject_redata_link_ch01(body: str, chapter_key: str) -> str:
    if chapter_key != "01":
        return body
    link = (
        '<p class="redata-preface-link">'
        '<strong>Redata foundation:</strong> '
        '<a href="chapters/02-fields-pixels-packets.html#redata-pipeline">Chapter 2 — Redata pipeline</a> '
        'documents lossless segments, truth filter, ZAC7, and Hostess7 brain sovereignty. '
        '<a href="../wiki/Redata-Pipeline.md">Wiki →</a>'
        '</p>'
    )
    if "redata-preface-link" in body:
        return body
    anchor = "Validation and reproducibility"
    if anchor in body:
        return body.replace(f"<h2>{anchor}", link + "\n\n<h2>" + anchor, 1)
    return link + "\n" + body
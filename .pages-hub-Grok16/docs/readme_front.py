#!/usr/bin/env python3
"""Render repository README.md as GitHub Pages index (front page)."""
from __future__ import annotations

import html
import re
from pathlib import Path

REPO = "https://github.com/ZacharyGeurts/Grok16"
WIKI = f"{REPO}/wiki"


def _rewrite_links(md: str) -> str:
    md = re.sub(r"\]\(docs/", "](", md)
    md = re.sub(r"\]\(RELEASE-[^)]+\.md\)", "](release.html)", md)
    md = re.sub(
        r"\]\(wiki/([^)/]+)\.md\)",
        lambda m: f"]({WIKI}/{m.group(1).replace('_', '-').title().replace('-', '-')})",
        md,
    )
    md = md.replace("](wiki/Speed-Bench.md)", f"]({WIKI}/Speed-Bench)")
    md = md.replace("](wiki/", f"]({WIKI}/")
    for name in (
        "ARCHITECTURE.md",
        "PERFORMANCE.md",
        "CREDITS.md",
        "NOTICE",
        "LICENSE",
    ):
        md = md.replace(f"]({name})", f"]({REPO}/blob/main/{name})")
    md = md.replace("](mcp/README.md)", f"]({REPO}/blob/main/mcp/README.md)")
    return md


def _inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def _parse_table(lines: list[str], start: int) -> tuple[str, int]:
    rows: list[list[str]] = []
    i = start
    while i < len(lines) and "|" in lines[i]:
        row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        if row and not all(re.match(r"^[-:]+$", c) for c in row):
            rows.append(row)
        i += 1
    if not rows:
        return "", start
    head = rows[0]
    body = rows[1:]
    out = ["<table>", "<tr>" + "".join(f"<th>{_inline(c)}</th>" for c in head) + "</tr>"]
    for row in body:
        out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in row) + "</tr>")
    out.append("</table>")
    return "\n".join(out), i


def markdown_to_html(md: str) -> str:
    md = _rewrite_links(md)
    lines = md.splitlines()
    parts: list[str] = []
    i = 0
    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    list_kind: str | None = None

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            parts.append(f"</{list_kind}>")
            list_kind = None

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            if in_code:
                lang = code_lang.lower()
                body = "\n".join(code_buf)
                if lang == "mermaid":
                    parts.append(f'<pre class="mermaid">{html.escape(body)}</pre>')
                else:
                    parts.append(f"<pre><code>{html.escape(body)}</code></pre>")
                in_code = False
                code_buf = []
                code_lang = ""
            else:
                close_list()
                in_code = True
                code_lang = line[3:].strip()
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if line.strip() == "---":
            close_list()
            parts.append("<hr />")
            i += 1
            continue

        if line.startswith("|"):
            close_list()
            tbl, i = _parse_table(lines, i)
            if tbl:
                parts.append(tbl)
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            close_list()
            level = len(m.group(1))
            parts.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        if line.startswith("> "):
            close_list()
            parts.append(f"<blockquote><p>{_inline(line[2:])}</p></blockquote>")
            i += 1
            continue

        img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line.strip())
        if img:
            close_list()
            alt, src = img.group(1), img.group(2)
            parts.append(f'<p><img src="{html.escape(src)}" alt="{html.escape(alt)}" loading="lazy" /></p>')
            i += 1
            continue

        ul = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        if ul:
            if list_kind != "ul":
                close_list()
                parts.append("<ul>")
                list_kind = "ul"
            parts.append(f"<li>{_inline(ul.group(2))}</li>")
            i += 1
            continue

        ol = re.match(r"^(\s*)\d+\.\s+(.*)$", line)
        if ol:
            if list_kind != "ol":
                close_list()
                parts.append("<ol>")
                list_kind = "ol"
            parts.append(f"<li>{_inline(ol.group(2))}</li>")
            i += 1
            continue

        if not line.strip():
            close_list()
            i += 1
            continue

        close_list()
        parts.append(f"<p>{_inline(line)}</p>")
        i += 1

    close_list()
    if in_code and code_buf:
        parts.append(f"<pre><code>{html.escape(chr(10).join(code_buf))}</code></pre>")
    return "\n".join(parts)


def v5_front_body(*, distro: str, g16: str, report: str) -> str:
    """Grok16 5.0 home — written from code/doctrine, not README."""
    md = f"""# Grok16 {distro} — Version One

**5.0 is a clean start** (v1.0 operator framing). Self-hosted `g16` @ **{g16}**. One belt (`belt_2_0`). One 2D platform. No field files.

> **DO NOT CREATE FIELD FILES** — they heat neighboring fields. Placement on the [field platform](field-platform.html) *is* field at depth 0.

## Benchmarks (Speed Bench {report})

| Result | Value |
|--------|-------|
| Fastest execution | **102.8M ops/s** — C++ g16 belt_2_0 |
| Belt triad | [performance.html#triad](performance.html#triad) |
| Full table | [speed-bench.html](speed-bench.html) |

## Start

```bash
git clone https://github.com/ZacharyGeurts/Grok16.git
cd Grok16 && git checkout v{distro}
export G16_PREFIX="$(pwd)" G16_BELT_PROFILE=belt_2_0
./scripts/grok16-toolchain.sh rebuild && ./scripts/grok16-toolchain.sh verify
```

Binary: `grok16-{distro}-linux-x86_64.tar.gz` → `source grok16-env.sh` → `./share/ammocode/ammocode`

## Docs

- [Field platform](field-platform.html) — 2D auto-field, **no field files**
- [ZNetwork connect](znetwork-connect.html) — field wire, identity without phone
- [Safety](safety.html) · [Release {distro}](release.html)
"""
    content = markdown_to_html(md)
    return f"""
  <figure class="fig-wide readme-charts">
    <img src="assets/speed-bench-chart.svg" alt="Speed bench compile vs execution" width="920" height="280" loading="eager" />
    <figcaption>Speed bench report v{report} · distro {distro} · <a href="speed-bench.html">full manual →</a></figcaption>
  </figure>
  <div class="figure-row readme-charts-row">
    <figure class="fig-card">
      <img src="assets/triad-chart.svg" alt="Belt triad comparison" width="640" height="280" loading="lazy" />
      <figcaption><a href="performance.html#triad">bench-triad</a></figcaption>
    </figure>
    <figure class="fig-card">
      <img src="assets/compare-chart.svg" alt="Field vs host compare" width="640" height="280" loading="lazy" />
      <figcaption><a href="performance.html">bench-compare</a></figcaption>
    </figure>
  </div>
  <article class="readme-prose">
{content}
  </article>
"""


def readme_body(*, distro: str, report: str) -> str:
    return v5_front_body(distro=distro, g16="16.2.0", report=report)


def _legacy_readme_body(*, distro: str, report: str) -> str:
    readme_path = Path(__file__).resolve().parent.parent / "README.md"
    md = readme_path.read_text(encoding="utf-8")
    content = markdown_to_html(md)
    return f"""
  <figure class="fig-wide readme-charts">
    <img src="assets/speed-bench-chart.svg" alt="Speed bench compile vs execution" width="920" height="280" loading="eager" />
    <figcaption>Speed bench report v{report} · distro {distro} · <a href="speed-bench.html">full manual →</a></figcaption>
  </figure>
  <div class="figure-row readme-charts-row">
    <figure class="fig-card">
      <img src="assets/triad-chart.svg" alt="Belt triad comparison" width="640" height="280" loading="lazy" />
      <figcaption><a href="performance.html#triad">bench-triad</a></figcaption>
    </figure>
    <figure class="fig-card">
      <img src="assets/compare-chart.svg" alt="Field vs host compare" width="640" height="280" loading="lazy" />
      <figcaption><a href="performance.html">bench-compare</a></figcaption>
    </figure>
  </div>
  <article class="readme-prose">
{content}
  </article>
"""


def write_index(page_fn, *, distro: str, g16: str, report: str) -> None:
    body = v5_front_body(distro=distro, g16=g16, report=report)
    out = page_fn("Home", body)
    out = out.replace(
        'href="https://zacharygeurts.github.io/Grok16/home.html"',
        'href="https://zacharygeurts.github.io/Grok16/"',
    )
    Path(__file__).resolve().parent.joinpath("index.html").write_text(out, encoding="utf-8")
    print("wrote index.html (Grok16 5.0 v1.0 front page)")
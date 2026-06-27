#!/usr/bin/env python3
"""Rebuild AmmoOS GitHub Pages manual (docs/)."""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
VER_DOC = REPO_ROOT / "data" / "ammoos-version.json"
PLAT_DOC = REPO_ROOT / "data" / "ammoos-platform-release.json"
CACHE = "v2"

VER = "1.0.1-beta"
SURFACES: dict[str, str] = {}
if VER_DOC.is_file():
    v = json.loads(VER_DOC.read_text(encoding="utf-8"))
    VER = v.get("version", VER)
    SURFACES = v.get("surfaces", {})

NAV = [
    ("index.html", "Home"),
    ("getting-started.html", "Getting Started"),
    ("launch-surfaces.html", "Launch Surfaces"),
    ("combinatronic.html", "Combinatronic"),
    ("platforms.html", "Platforms"),
    ("io.html", "Field I/O"),
    ("queen-browser.html", "Queen Browser"),
    ("architecture.html", "Architecture"),
]


def head(title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>AmmoOS — {title}</title>
  <meta name="description" content="AmmoOS {VER} beta manual — field OS, browser surfaces, combinatronic engine." />
  <link rel="canonical" href="https://zacharygeurts.github.io/AmmoOS/{'index.html' if title == 'Home' else title.lower().replace(' ', '-') + '.html'}" />
  <link rel="stylesheet" href="manual.css?v{CACHE}" />
</head>
<body>
"""


def nav() -> str:
    links = "\n".join(
        f'      <a href="{h}"{" aria-current=\"page\"" if h == "index.html" else ""}>{l}</a>'
        for h, l in NAV
    )
    return f"""  <nav>
    <div class="nav-top">
      <div class="nav-brand">
        <strong>AmmoOS</strong>
        <span class="nav-version">{VER} beta</span>
      </div>
    </div>
    <div class="nav-links">
{links}
      <a href="https://github.com/ZacharyGeurts/AmmoOS">GitHub</a>
    </div>
  </nav>
"""


def foot() -> str:
    return f"""  <footer>
    <a href="index.html">Home</a> ·
    <a href="https://github.com/ZacharyGeurts/AmmoOS/releases/tag/v{VER}">Release v{VER}</a> ·
    <a href="https://github.com/ZacharyGeurts/AmmoOS">GitHub</a>
    <p class="footer-meta">AmmoOS {VER} · field OS beta · GPLv3</p>
  </footer>
</body>
</html>
"""


def page(title: str, body: str) -> str:
    return head(title) + nav() + body + foot()


def readme_html(md: str) -> str:
    lines = md.splitlines()
    parts: list[str] = []
    in_code = False
    buf: list[str] = []
    for line in lines:
        if line.startswith("```"):
            if in_code:
                parts.append(f"<pre><code>{''.join(buf)}</code></pre>")
                buf, in_code = [], False
            else:
                in_code, buf = True, []
            continue
        if in_code:
            buf.append(line + "\n")
            continue
        if line.startswith("|") and "|" in line[1:]:
            continue
        if m := re.match(r"^#{1,6}\s+(.*)$", line):
            lvl = len(m.group(0).split()[0])
            parts.append(f"<h{lvl}>{m.group(1)}</h{lvl}>")
        elif line.strip().startswith("!["):
            parts.append(f"<p>{line}</p>")
        elif line.strip():
            parts.append(f"<p>{line}</p>")
    return "\n".join(parts)


def platform_table() -> str:
    if not PLAT_DOC.is_file():
        return "<tr><td colspan=\"4\">See data/ammoos-platform-release.json</td></tr>"
    doc = json.loads(PLAT_DOC.read_text(encoding="utf-8"))
    rows = []
    for p in doc.get("platforms", []):
        boot = p.get("bootstrap", {})
        boot_s = ", ".join(f"<code>{k}</code>" for k in boot)
        rows.append(
            f"    <tr><td><code>{p['id']}</code></td><td>{p['os']}</td>"
            f"<td>{p['arch']}</td><td>{boot_s}</td></tr>"
        )
    return "\n".join(rows)


def surface_rows() -> str:
    rows = []
    labels = {
        "host_desktop": "Host desktop",
        "field_command": "Field command",
        "queen_browser": "Queen Browser",
        "underlay_f9": "Underlay F9",
        "training_viewer": "Training viewer",
    }
    for key, url in SURFACES.items():
        rows.append(f"    <tr><td>{labels.get(key, key)}</td><td><code>{url}</code></td><td>Browser</td></tr>")
    rows.append(
        '    <tr><td>Queen shell</td><td><code>Queen/build/rtx/bin/Linux/queen-browser</code></td><td>Native</td></tr>'
    )
    rows.append('    <tr><td>Dev launcher</td><td><code>./nexus.sh</code></td><td>Native</td></tr>')
    return "\n".join(rows)


def write_pages() -> None:
    readme_path = REPO_ROOT / "README-AMMOOS.md"
    readme_body = ""
    if readme_path.is_file():
        readme_body = f"""
  <article class="readme-prose">
{readme_html(readme_path.read_text(encoding="utf-8"))}
  </article>
"""

    pages = {
        "index.html": (
            "Home",
            f"""
  <img class="hero-img" src="images/hero-banner.svg" width="1200" height="320" alt="AmmoOS field OS banner" />
  <h1>AmmoOS Programmer &amp; Operator Manual</h1>
  <p class="lead"><strong>AmmoOS {VER}</strong> — field operating system beta. Every component launches in your <strong>browser</strong> or as a <strong>native program</strong>. Combinatronic rebalance wires the engine before boot.</p>
  <div class="workflow">
    <a href="getting-started.html"><strong>1 Install</strong>Linux / Windows / macOS</a>
    <a href="launch-surfaces.html"><strong>2 Launch</strong>Browser + native paths</a>
    <a href="combinatronic.html"><strong>3 Combinatronic</strong>Rebalance pipeline</a>
    <a href="platforms.html"><strong>4 Platforms</strong>10 target families</a>
    <a href="io.html"><strong>5 Field I/O</strong>Panel HTTP API</a>
  </div>
{readme_body}
""",
        ),
        "getting-started.html": (
            "Getting Started",
            f"""
  <h1>Getting Started</h1>
  <p>AmmoOS <strong>{VER}</strong> installs from source. Production deploy uses <code>install-all.sh</code>; development uses <code>nexus.sh</code>.</p>
  <h2>Linux x86_64</h2>
  <pre><code>git clone https://github.com/ZacharyGeurts/AmmoOS.git
cd AmmoOS
sudo ./install-all.sh</code></pre>
  <p>Browser opens <code>{SURFACES.get('host_desktop', 'http://127.0.0.1:9477/field')}</code> on start.</p>
  <h2>Development tree</h2>
  <pre><code>export SG_ROOT=/path/to/SG
./scripts/ammoos-beta-pipeline.sh
./nexus.sh</code></pre>
  <h2>Windows</h2>
  <pre><code># PowerShell (see stealth.ps1 in release assets)
# Or WSL2:
tar -xzf ammooos-{VER}-source.tar.gz && cd ammooos-{VER}
sudo ./install-all.sh</code></pre>
  <h2>Verify</h2>
  <pre><code>./scripts/ammoos-launch-verify.sh</code></pre>
""",
        ),
        "launch-surfaces.html": (
            "Launch Surfaces",
            f"""
  <h1>Launch surfaces</h1>
  <p>Policy: <strong>browser or native program</strong> — no orphan components.</p>
  <table>
    <tr><th>Surface</th><th>Path</th><th>Kind</th></tr>
{surface_rows()}
  </table>
  <h2>Verify registry</h2>
  <pre><code>./scripts/ammoos-launch-verify.sh
cat .nexus-state/ammoos-launch-registry.json</code></pre>
""",
        ),
        "combinatronic.html": (
            "Combinatronic",
            """
  <h1>Combinatronic integration</h1>
  <p>Before pack and release, AmmoOS runs the <strong>g16 combinatronic optimal</strong> cycle:</p>
  <ol>
    <li><strong>Growth scan</strong> — file combinatorics, optimal width</li>
    <li><strong>Dimensions consolidate</strong> — plate width × length</li>
    <li><strong>Combinamatrix</strong> — leaf pack</li>
    <li><strong>Steel neural plates</strong> — deep connection management</li>
    <li><strong>Sequence + AmmoLang</strong> — gapless universal sequence</li>
    <li><strong>Rebalance</strong> — chip + program batteries</li>
    <li><strong>Condense + Combine + Connect</strong> — universal panel wiring</li>
    <li><strong>Spider wire</strong> — ironclad outward lanes</li>
  </ol>
  <pre><code>./scripts/ammoos-beta-pipeline.sh
pythong lib/g16-combinatronic-rebalance.py optimal</code></pre>
  <p>Witness: <code>.nexus-state/ammoos-combinatronic-optimal.json</code></p>
  <p>Plates: <code>Queen/AmmoOS/net/FieldNetCore.fld</code>, <code>FieldNetGate.fld</code>, <code>FieldNetDos.fld</code></p>
""",
        ),
        "platforms.html": (
            "Platforms",
            f"""
  <h1>Platform matrix</h1>
  <p>AmmoOS <strong>{VER}</strong> ships source bootstrap per platform family.</p>
  <table>
    <tr><th>ID</th><th>OS</th><th>Arch</th><th>Bootstrap</th></tr>
{platform_table()}
  </table>
  <p>Release assets: <code>ammoos-{VER}-platforms.json</code> · <code>ammoos-{VER}-PLATFORMS.md</code></p>
""",
        ),
        "io.html": (
            "Field I/O",
            f"""
  <h1>Field I/O</h1>
  <p>Panel HTTP serves all browser surfaces on loopback <code>:9477</code>. Queen world on <code>:9481</code>.</p>
  <figure class="figure">
    <img src="images/io-architecture.svg" width="920" height="420" alt="AmmoOS architecture" />
    <figcaption>Panel ↔ daemon ↔ state ↔ Queen browser</figcaption>
  </figure>
  <h2>Key routes</h2>
  <table>
    <tr><th>Route</th><th>Role</th></tr>
    <tr><td><code>/field</code></td><td>Host desktop</td></tr>
    <tr><td><code>/command</code></td><td>Threat panel + training</td></tr>
    <tr><td><code>/underlay-f9</code></td><td>Tristate installer</td></tr>
    <tr><td><code>/api/chips/combinatronic</code></td><td>Chip combinatronic status</td></tr>
    <tr><td><code>/api/g16/universal-combinatronic</code></td><td>Universal combinatronic panel</td></tr>
    <tr><td><code>/api/program/combinatronic</code></td><td>Program combinatronic boil</td></tr>
  </table>
  <p>Module: <code>lib/threat-panel-http.py</code></p>
""",
        ),
        "queen-browser.html": (
            "Queen Browser",
            f"""
  <h1>Queen Browser</h1>
  <p>Queen Browser embeds the field OS inside the Start tab. URL: <code>{SURFACES.get('queen_browser', 'http://127.0.0.1:9481/world/browser.html')}</code></p>
  <p>Native RTX shell: <code>Queen/build/rtx/bin/Linux/queen-browser</code> — built via <code>queen-forge.py run live_build_field</code>.</p>
  <p>FIELDC v4 compiles <code>.fld</code> inside the AmmoOS shell path. Guest net plates live in <code>Queen/AmmoOS/net/</code>.</p>
""",
        ),
        "architecture.html": (
            "Architecture",
            """
  <h1>Architecture</h1>
  <pre><code>Host browser (:9477)
  ├─ /field        → host desktop
  ├─ /command      → C2 + training
  └─ /underlay-f9  → Tristate

Queen Browser (:9481)
  └─ /world/browser.html

Combinatronic engine
  ├─ g16-combinatronic-rebalance.py
  ├─ field-program-combinatronic.py
  └─ field-g16-universal-combinatronic.py

SG stack (wired via wire-stack.sh)
  Grok16 · Queen · Hostess7 · KILROY · ZOCR · World_Redata</code></pre>
""",
        ),
    }

    for name, (title, body) in pages.items():
        (ROOT / name).write_text(page(title, body), encoding="utf-8")
        print(f"wrote {name}")


def main() -> int:
    write_pages()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
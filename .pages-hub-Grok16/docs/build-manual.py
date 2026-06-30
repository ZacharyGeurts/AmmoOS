#!/usr/bin/env pythong
"""Rebuild Grok16 GitHub Pages manual (docs/) for distro 5.1.0 — stack fabric."""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from readme_front import write_index as write_readme_index
DISTRO = "5.2.0"
G16 = "16.2.0"
CACHE = "v16"
BENCH_REPORT = "5.0.0"
BENCH_SUITE = "speed_demo"
BENCH_SUITE_VER = "1.1.0"

NAV = [
    ("index.html", "Home"),
    ("field-platform.html", "Field Platform"),
    ("safety.html", "Safety"),
    ("znetwork-connect.html", "ZNetwork"),
    ("speed-bench.html", "Speed Bench"),
    ("performance.html", "Performance"),
    ("release.html", "Release 5.2"),
    ("platforms.html", "Platforms"),
    ("c64.html", "C64"),
    ("c64-classic.html", "C64 Classic"),
    ("c64-ultimate.html", "C64 Ultimate"),
    ("mcp.html", "MCP"),
    ("single-fabric.html", "Single Fabric"),
    ("getting-started.html", "Getting Started"),
    ("architecture.html", "Architecture"),
    ("batteries.html", "Batteries"),
    ("toolkits.html", "Toolkits"),
    ("linker.html", "Linker"),
    ("profiles.html", "Profiles"),
    ("performance.html", "Performance"),
    ("integration.html", "Integration"),
    ("concepts.html", "Concepts"),
    ("master-coder.html", "Master Coder"),
    ("field-primer.html", "Field Primer"),
    ("field-research.html", "Field Research"),
    ("reference.html", "Reference"),
]


def load_bench() -> dict:
    path = ROOT / "field-exec-full-bench.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def load_triad() -> dict:
    path = ROOT.parent / "data" / "bench" / "triad-latest.json"
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def triad_table_html(data: dict) -> str:
    cases = {c["id"]: c for c in data.get("cases", [])}
    rows = []
    for kid, prof in (("host_gcc", "-O3 -march=native"), ("belt_1_0", "belt_1_0"), ("belt_2_0", "belt_2_0")):
        c = cases.get(kid)
        if not c:
            continue
        tool = "g++" if kid == "host_gcc" else "g16"
        rows.append(
            f"    <tr><td>{'host' if kid == 'host_gcc' else ''} <code>{tool}</code></td>"
            f"<td><code>{prof}</code></td>"
            f"<td>{c.get('compile_ms', '—')}</td>"
            f"<td>{c.get('run_wall_ms', '—')}</td>"
            f"<td>{c.get('binary_bytes', '—'):,}</td></tr>"
        )
    return "\n".join(rows) if rows else "    <tr><td colspan=\"5\">Run bench-triad</td></tr>"


def fmt_ops(v: float | int | None) -> str:
    if v is None:
        return "—"
    v = float(v)
    if v >= 1_000_000:
        return f"{v / 1_000_000:,.2f}M"
    return f"{v:,.0f}"


def bench_table_html(data: dict, *, compact: bool = False) -> str:
    rows = []
    for r in sorted(data.get("rows", []), key=lambda x: -(x.get("ops_per_sec") or 0)):
        compile_ms = "—" if not r.get("compile_ms") else f"{r['compile_ms']:,.0f}"
        ops = r.get("ops_per_sec", 0)
        if compact:
            rows.append(
                f"    <tr><td>{r['label']}</td><td>{compile_ms}</td>"
                f"<td><strong>{ops:,.2f}</strong></td></tr>"
            )
        else:
            bytes_col = "—" if not r.get("binary_bytes") else f"{r['binary_bytes']:,}"
            rows.append(
                f"    <tr><td>{r['label']}</td><td>{compile_ms}</td>"
                f"<td>{r.get('runner_wall_ms', 0):,.0f}</td>"
                f"<td><strong>{ops:,.2f}</strong></td><td>{bytes_col}</td></tr>"
            )
    colspan = "3" if compact else "5"
    return "\n".join(rows) if rows else f"    <tr><td colspan=\"{colspan}\">Run field-exec-full-bench.py</td></tr>"


def _bench_version_doc() -> dict:
    path = ROOT.parent / "data" / "grok16-speed-bench-version.json"
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def bench_meta(data: dict) -> dict:
    v = data.get("versions", {})
    ver_doc = _bench_version_doc()
    w = data.get("winners", {})
    pm = data.get("plate_meld") or {}
    ctx = pm.get("context") or {}
    best_exec = w.get("best_execution") or {}
    fast_compile = w.get("fastest_compile") or {}
    best_py = (w.get("best_per_language") or {}).get("python") or {}
    amort = w.get("best_amortized_first_run") or {}
    return {
        "bench_at": data.get("bench_at", "—"),
        "host": data.get("host", "—"),
        "target_sec": data.get("target_sec", 3),
        "report": ver_doc.get("report_version") or v.get("report_version", BENCH_REPORT),
        "distro": ver_doc.get("distro_version") or v.get("distro_version", DISTRO),
        "suite": ver_doc.get("bench_suite") or v.get("bench_suite", BENCH_SUITE),
        "suite_ver": ver_doc.get("bench_suite_version") or v.get("bench_suite_version", BENCH_SUITE_VER),
        "best_exec_label": best_exec.get("label", "—"),
        "best_exec_ops": fmt_ops(best_exec.get("ops_per_sec")),
        "fast_compile_label": fast_compile.get("label", "—"),
        "fast_compile_ms": f"{fast_compile.get('compile_ms', 0):,.0f}" if fast_compile.get("compile_ms") else "—",
        "best_py_ops": fmt_ops(best_py.get("ops_per_sec")),
        "amort_label": amort.get("label", "—"),
        "amort_ops": fmt_ops(amort.get("amortized_ops_per_sec")),
        "runners_tested": data.get("runners_tested", len(data.get("rows", []))),
        "schema": ver_doc.get("bench_schema") or data.get("schema", "grok16-field-exec-full-bench/v4"),
        "meld_gen": ctx.get("meld_generation", "—"),
        "meld_plates": ctx.get("plates_fused", "—"),
        "sense_profile": ctx.get("sense_profile", "—"),
        "sense_reason": ctx.get("sense_reason", "—"),
        "sense_vs_belt2": pm.get("sense_vs_belt_2_ops_ratio", "—"),
        "meld_helps": "yes" if pm.get("meld_helps_profile") else "no",
        "meld_compile_delta": pm.get("sense_vs_belt_2_compile_delta_ms"),
        "meld_ops_ratio": pm.get("sense_vs_belt_2_ops_ratio"),
        "bench_all_n": len(data.get("bench_all_profiles") or []),
    }


def head(title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>Grok16 — {title}</title>
  <meta name="description" content="Grok16 {DISTRO} programmer manual — unified g16 @ {G16}, batteries, linker, profiles." />
  <link rel="canonical" href="https://zacharygeurts.github.io/Grok16/{title.lower().replace(' ', '-')}.html" />
  <script>
  (function (d) {{
    try {{
      var t = localStorage.getItem("g16-theme");
      if (t !== "dark" && t !== "light" && t !== "queen") t = "queen";
      d.documentElement.setAttribute("data-theme", t);
    }} catch (e) {{
      d.documentElement.setAttribute("data-theme", "queen");
    }}
  }})(document);
  </script>
  <script src="manual-theme.js?{CACHE}"></script>
  <script src="manual-search.js?{CACHE}"></script>
  <script src="manual-layout.js?{CACHE}"></script>
  <link rel="stylesheet" href="manual.css?{CACHE}" />
</head>
<body>
"""


def nav() -> str:
    links = "\n".join(f'      <a href="{href}">{label}</a>' for href, label in NAV)
    return f"""  <nav>
    <div class="nav-top">
      <div class="nav-brand">
        <strong>Grok16</strong>
        <span class="nav-version">distro {DISTRO}</span>
        <span class="nav-g16">g16 @ {G16}</span>
      </div>
      <div class="nav-controls" aria-label="Display preferences">
        <div class="control-chip">
          <label class="control-label" for="g16-font-scale">Size</label>
          <select id="g16-font-scale" class="g16-select" aria-label="Font size">
            <option value="0.875">S</option>
            <option value="1" selected>M</option>
            <option value="1.125">L</option>
            <option value="1.25">XL</option>
          </select>
        </div>
        <div class="theme-switch" role="group" aria-label="Color theme">
          <button type="button" class="g16-seg" id="g16-theme-queen" data-theme="queen" aria-pressed="false">Queen</button>
          <button type="button" class="g16-seg" id="g16-theme-light" data-theme="light" aria-pressed="false">Light</button>
          <button type="button" class="g16-seg" id="g16-theme-dark" data-theme="dark" aria-pressed="false">Dark</button>
        </div>
      </div>
    </div>
    <div class="nav-links">
{links}
    </div>
  </nav>
"""


def foot() -> str:
    return f"""  <footer>
    <a href="index.html">Home</a> ·
    <a href="release.html">Release {DISTRO}</a> ·
    <a href="https://github.com/ZacharyGeurts/Grok16">GitHub</a> ·
    <a href="https://github.com/ZacharyGeurts/Grok16/wiki">Wiki</a>
    <p class="footer-meta">Grok16 {DISTRO} · g16 @ {G16} · GPLv3</p>
  </footer>
</body>
</html>
"""


def page(title: str, body: str) -> str:
    return head(title) + nav() + body + foot()


def pages_dict() -> dict[str, tuple[str, str]]:
    bench = load_bench()
    triad = load_triad()
    meta = bench_meta(bench)
    table = bench_table_html(bench)
    table_compact = bench_table_html(bench, compact=True)
    triad_table = triad_table_html(triad)
    return {
    "speed-bench.html": (
        "Speed Bench",
        f"""
  <h1>Speed bench — report v{meta['report']}</h1>
  <p>Distro <strong>{meta['distro']}</strong> · suite <code>{meta['suite']}</code> @ <code>{meta['suite_ver']}</code> · schema <code>{meta['schema']}</code></p>

  <aside class="callout callout-accent">
    <strong>Version stamps:</strong> Every run writes <code>docs/field-exec-full-bench.json</code> with distro, g16, suite, and report versions. Doctrine: <code>data/grok16-speed-bench-version.json</code>
  </aside>

  <figure class="fig-wide">
    <img src="assets/speed-bench-chart.svg" alt="Speed bench bar chart" width="920" height="280" />
    <figcaption>Execution ops/s by runner — {meta['bench_at']} on <code>{meta['host']}</code></figcaption>
  </figure>

  <h2 id="winners">Winners</h2>
  <div class="winner-grid">
    <div class="winner-card"><strong>Fastest execution</strong><span class="val">{meta['best_exec_ops']}</span><span class="sub">{meta['best_exec_label']}</span></div>
    <div class="winner-card"><strong>Fastest compile</strong><span class="val">{meta['fast_compile_ms']} ms</span><span class="sub">{meta['fast_compile_label']}</span></div>
    <div class="winner-card"><strong>Best Python</strong><span class="val">{meta['best_py_ops']}</span><span class="sub">interpreter — no compile</span></div>
    <div class="winner-card"><strong>Amortized first-run</strong><span class="val">{meta['amort_ops']}</span><span class="sub">{meta['amort_label']}</span></div>
  </div>

  <h2 id="results">Full results ({meta['target_sec']}s window)</h2>
  <table>
    <tr><th>Runner</th><th>Compile (ms)</th><th>Exec wall (ms)</th><th>ops/s</th><th>Binary bytes</th></tr>
{table}
  </table>

  <h2 id="plate-meld">Plate meld analysis</h2>
  <p>Cycle: <code>field-plate-meld.py fuse</code> + <code>g16-compiler-sense-plate.py cycle</code> before compiles. Doctrine: <code>data/grok16-plate-meld-bench-doctrine.json</code></p>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Meld generation</td><td>{meta['meld_gen']}</td></tr>
    <tr><td>Plates fused</td><td>{meta['meld_plates']}</td></tr>
    <tr><td>Compiler sense profile</td><td><code>{meta['sense_profile']}</code> ({meta['sense_reason']})</td></tr>
    <tr><td>Sense vs belt_2_0 exec ratio</td><td>{meta['sense_vs_belt2']}</td></tr>
    <tr><td>Meld helps profile ladder</td><td><strong>{meta['meld_helps']}</strong></td></tr>
  </table>
  <aside class="callout callout-accent">
    <strong>Professional verdict:</strong> Plate meld does not block the ELF hot path. On this host, compiler-sense compile was <strong>{meta['meld_compile_delta']} ms</strong> vs static <code>belt_2_0</code>; sense execution ratio <strong>{meta['meld_ops_ratio']}</strong>. Profile ladder unlocks when meld generation ≥ {meta['meld_gen']}.
  </aside>

  <h2 id="bench-all">bench-all cross-reference</h2>
  <p>{meta['bench_all_n']} profile runs from <code>data/bench/latest.json</code> (field-nexus-bench). Run: <code>./scripts/grok16-toolchain.sh bench-all</code></p>

  <h2 id="doctrine">Doctrine</h2>
  <ul>
    <li><strong>Dev / uncompiled:</strong> Python at interpreter speed (~0.75–0.78M ops/s). C/C++ rely on chamber compile ahead.</li>
    <li><strong>Plate meld:</strong> Fuses sense plates → compiler-sense profile ladder before wave-convert.</li>
    <li><strong>Compare axis:</strong> <code>field_execution_ops_per_sec</code> on identical <code>speed_demo</code> kernel.</li>
  </ul>
  <p>See <a href="uncompiled.html">Uncompiled execution</a> · <a href="cmake-linking.html">CMake &amp; linking</a></p>

  <h2 id="reproduce">Reproduce (comprehensive)</h2>
  <pre><code>cd Grok16
git checkout v{DISTRO}
export G16_PREFIX="$(pwd)"
export GROK16_SG_ROOT=/path/to/SG
export NEXUS_STATE_DIR=$GROK16_SG_ROOT/NewLatest/state
G16_PLATE_MELD_CMD=fuse SPEED_DEMO_TARGET_SEC=3 ./scripts/grok16-toolchain.sh exec-comprehensive-bench
./scripts/grok16-toolchain.sh exec-compare</code></pre>
  <p>JSON: <a href="https://github.com/ZacharyGeurts/Grok16/blob/main/docs/field-exec-full-bench.json">field-exec-full-bench.json</a> · MD: <a href="https://github.com/ZacharyGeurts/Grok16/blob/main/docs/SPEED-BENCH-REPORT.md">SPEED-BENCH-REPORT.md</a></p>
""",
    ),
    "uncompiled.html": (
        "Uncompiled",
        f"""
  <h1>Uncompiled execution</h1>
  <p>Grok16 <strong>{DISTRO}</strong> — dev runs at normal speed; compile is chamber-organized and <strong>ahead</strong>, not on every click.</p>

  <figure class="fig-wide">
    <img src="assets/uncompiled-chamber-flow.svg" alt="Uncompiled chamber flow diagram" width="880" height="320" />
    <figcaption>Python stays interpreted · native siblings wave-convert once into plane cache</figcaption>
  </figure>

  <aside class="callout callout-cyan">
    <strong>Not compiling C/C++:</strong> There is no C/C++ REPL. Chamber organization presents a bin-like run — reuse staged binary (~0.2 ms copy) or compile once into plane cache (318 ms – 2.5 s first run).
  </aside>

  <h2 id="lanes">Execution lanes</h2>
  <table>
    <tr><th>Lane</th><th>Dev behavior</th><th>speed_demo @ {meta['target_sec']}s</th></tr>
    <tr><td><strong>Python</strong></td><td>True interpreter (CPython / gpy-16 GrokVM)</td><td>~{meta['best_py_ops']} ops/s</td></tr>
    <tr><td><strong>C / C++</strong></td><td>Chamber <strong>compile ahead</strong> — no line-by-line interpreter</td><td>~87–95M ops/s after plane cache</td></tr>
    <tr><td><strong>CMake</strong></td><td>Configure + build once; bin reused</td><td>~93M ops/s</td></tr>
  </table>
  <p>Doctrine: <code>data/field-exec-uncompiled-doctrine.json</code></p>

  <h2 id="chamber">Queen .launch chamber</h2>
  <ol>
    <li><strong>Folder mirror</strong> — compartment code in <code>.launch</code> chamber</li>
    <li><strong>Trim excess</strong> — strip README, lockfiles, build cruft on singular plane</li>
    <li><strong>Pick runner</strong> — Python entry stays interpreted; native sibling wave-converts</li>
    <li><strong>Cache</strong> — fingerprinted <code>launch-singular-plane/&lt;hash&gt;/plane-&lt;stem&gt;</code></li>
    <li><strong>Run like a bin</strong> — execution timed; <code>convert_ms</code> excluded after cache hit</li>
  </ol>
  <p>Module: <code>Queen/lib/queen-launch-singular-field.py</code></p>

  <h2 id="commands">Commands</h2>
  <pre><code># Uncompiled Python via chamber
QUEEN_LAUNCH_SINGULAR_FIELD=0 python3 Queen/lib/queen-launch-chamber.py run examples/speed-demo/speed-demo.launch

# Singular plane (compile ahead + cache)
python3 Queen/lib/queen-launch-singular-field.py run examples/speed-demo/

# Full versioned bench
SPEED_DEMO_TARGET_SEC=3 ./scripts/grok16-toolchain.sh exec-full-bench</code></pre>
  <p><a href="speed-bench.html">Speed bench manual</a> · <a href="cmake-linking.html">CMake &amp; linking</a></p>
""",
    ),
    "cmake-linking.html": (
        "CMake & Link",
        f"""
  <h1>CMake and linking</h1>
  <p>Canonical Grok16 Field CMake + <code>g16-ld</code> mandate for <code>speed_demo</code> and all field targets.</p>

  <figure class="fig-wide">
    <img src="assets/cmake-link-pipeline.svg" alt="CMake configure build link pipeline" width="920" height="300" />
    <figcaption>Configure → g16 compile → g16-ld link with field mandate flags</figcaption>
  </figure>

  <h2 id="speed-demo">speed_demo CMake project</h2>
  <p><code>examples/speed-demo/CMakeLists.txt</code> builds <code>grok16_speed_demo</code> from <code>speed_demo.cpp</code>.</p>

  <h3>Host plane</h3>
  <pre><code>cmake -S examples/speed-demo -B build/host \\
  -DCMAKE_CXX_COMPILER=$(which g++) \\
  -DGROK16_HOST_PLANE=ON
cmake --build build/host -j$(nproc)</code></pre>

  <h3>G16 belt plane</h3>
  <pre><code>cmake -S examples/speed-demo -B build/g16 \\
  -DCMAKE_TOOLCHAIN_FILE=$G16_PREFIX/cmake/grok16-toolchain.cmake \\
  -DGROK16_PROFILE=belt_2_0
cmake --build build/g16 -j$(nproc)</code></pre>

  <h2 id="toolchain">Toolchain file</h2>
  <p><code>cmake/grok16-toolchain.cmake</code> sets:</p>
  <ul>
    <li><code>CMAKE_C_COMPILER</code> / <code>CMAKE_CXX_COMPILER</code> → <code>g16</code></li>
    <li>Profile flags from <code>data/grok16-profiles.json</code></li>
    <li>Linker wrapper → <code>g16-ld</code></li>
  </ul>

  <h2 id="mandate">Linking mandate</h2>
  <table>
    <tr><th>File</th><th>Role</th></tr>
    <tr><td><code>cmake/g16-linker-mandate.cmake</code></td><td>Field link flags, <code>-pie</code>, shared rules</td></tr>
    <tr><td><code>cmake/g16-field-mandate.cmake</code></td><td><code>G16_FIELD_SAFETY_MANDATE_v1</code> on field targets</td></tr>
    <tr><td><code>forge/g16-linker.py</code></td><td><code>g16-ld</code> backend — 16 target families</td></tr>
  </table>
  <p>Full linker manual: <a href="linker.html">Linker</a></p>

  <h2 id="bench">Bench with CMake row</h2>
  <pre><code>SPEED_DEMO_TARGET_SEC=3 ./scripts/grok16-toolchain.sh exec-full-bench
./scripts/field-exec-stage.py</code></pre>
  <p>CMake runner included in speed bench report v{meta['report']}. Versions: <code>data/grok16-speed-bench-version.json</code></p>
""",
    ),
    "release.html": (
        f"Release {DISTRO}",
        f"""
  <h1>Release {DISTRO}</h1>
  <p>Grok16 <strong>{DISTRO}</strong> — C64 Ultimate hardware pair, 17-target bootstrap matrix, AmmoLang adaptive ship timing. Compiler <strong>g16 @ {G16}</strong>. Tag <code>v{DISTRO}</code>.</p>

  <aside class="callout callout-warn">
    <strong>Field platform:</strong> <a href="field-platform.html">Do not create field files</a> — use the 2D auto-field plane.
  </aside>

  <h2 id="shipped">What ships in {DISTRO}</h2>
  <ul>
    <li><strong>C64 catalog split</strong> — <a href="c64-classic.html">classic 6510</a> · <a href="c64-ultimate.html">C64 Ultimate pair</a> · g16 does <strong>not</strong> run on breadbin silicon</li>
    <li><strong>17 bootstrap platforms</strong> — <a href="platforms.html">Platform matrix</a> (Linux, Android, Darwin, iOS, Windows, bare-ELF, RISC-V)</li>
    <li><strong>AmmoLang ship</strong> — <code>grok16_ship.aml</code> timing ledger · hang guard</li>
    <li><strong>Stack fabric G1–G15</strong> — receipts, MCP stdio, truth gate, ZNetwork wire</li>
    <li><strong>belt_2_0</strong> single fabric · <strong>field_physics</strong> safety · binary package lane</li>
    <li><strong>Speed bench v{meta['report']}</strong> — best exec <strong>{meta['best_exec_ops']}</strong> ops/s</li>
  </ul>

  <h2 id="checkout">Checkout</h2>
  <pre><code>git clone https://github.com/ZacharyGeurts/Grok16.git
cd Grok16 && git checkout v{DISTRO}
export G16_PREFIX="$(pwd)" G16_BELT_PROFILE=belt_2_0
./scripts/grok16-toolchain.sh rebuild
./scripts/grok16-toolchain.sh verify
./scripts/grok16-toolchain.sh test-battery-belt
./scripts/grok16-toolchain.sh bench-refresh</code></pre>

  <h2 id="binary">Binary package</h2>
  <pre><code>./scripts/grok16-toolchain.sh binary-package
tar xzf dist/grok16-{DISTRO}-linux-x86_64.tar.gz
cd grok16-{DISTRO}-linux-x86_64 && source grok16-env.sh
./share/ammocode/ammocode</code></pre>

  <h2 id="charts">Benchmarks</h2>
  <pre><code>./scripts/grok16-toolchain.sh bench-triad
./scripts/grok16-toolchain.sh exec-full-bench</code></pre>
  <p><a href="platforms.html">Platforms</a> · <a href="c64.html">C64</a> (<a href="c64-classic.html">classic</a> · <a href="c64-ultimate.html">Ultimate</a>) · <a href="speed-bench.html">Speed Bench</a> · <a href="performance.html">Performance</a></p>
""",
    ),
    "platforms.html": (
        "Platforms",
        f"""
  <h1>Platform bootstrap matrix — {DISTRO}</h1>
  <p>Grok16 ships <strong>source + forge</strong>. Build <code>g16</code> locally on each target (or cross from Linux x86_64). Doctrine: <code>data/grok16-platform-release.json</code>.</p>
  <p><strong>17 bootstrap platforms</strong> (g16 builds locally or cross). Every GitHub release attaches <code>grok16-{{version}}-platforms.json</code> and <code>PLATFORMS.md</code>.</p>
  <h2 id="families">Bootstrap families</h2>
  <table>
    <tr><th>Family</th><th>IDs</th></tr>
    <tr><td>Linux GNU</td><td><code>linux-gnu-x86_64</code>, <code>i386</code>, <code>aarch64</code>, <code>arm</code>, <code>riscv64</code></td></tr>
    <tr><td>Android NDK</td><td><code>android-aarch64</code>, <code>arm</code>, <code>x86_64</code></td></tr>
    <tr><td>Apple</td><td><code>darwin-x86_64</code>, <code>darwin-aarch64</code>, <code>ios-aarch64</code></td></tr>
    <tr><td>Windows</td><td><code>win32-x86_64</code>, <code>win32-aarch64</code></td></tr>
    <tr><td>Bare ELF</td><td><code>bare-elf-x86_64</code>, <code>aarch64</code>, <code>riscv64</code></td></tr>
  </table>
  <h2 id="pairs">Hardware pairs (g16 does not run here)</h2>
  <p><a href="c64-ultimate.html">Commodore 64 Ultimate</a> — <code>pair-c64-ultimate</code>. Grok16 stays on your host; the new FPGA C64 runs PRG/media. <a href="c64-classic.html">Classic breadbin 6510</a> is Queen CHIPS only — <strong>not</strong> a g16 target.</p>
  <h2 id="quick">Quick start (Linux x86_64)</h2>
  <pre><code>tar xzf grok16-{DISTRO}-src.tar.gz && cd grok16-{DISTRO}-src
export G16_PREFIX=$(pwd) G16_PKGVERSION=Grok16-{G16}
./scripts/grok16-toolchain.sh bootstrap
./scripts/grok16-toolchain.sh rebuild
./scripts/grok16-launch-verify.sh</code></pre>
  <p>See <a href="linker.html">Linker</a> · <a href="getting-started.html">Getting Started</a> · <a href="release.html">Release</a></p>
""",
    ),
    "c64.html": (
        "Commodore 64 — catalog",
        f"""
  <h1>Commodore 64 — two catalog lanes</h1>
  <p>Grok16 <strong>{DISTRO}</strong> keeps classic and Ultimate hardware in separate Dewey books and Queen Game Room tiles.</p>
  <aside class="callout callout-warn">
    <strong>g16 does not run on MOS 6510 silicon.</strong> Neither lane is a Grok16 bootstrap target.
  </aside>
  <table>
    <tr><th>Lane</th><th>Hardware</th><th>Queen</th><th>CHIPS stack</th></tr>
    <tr><td><a href="c64-classic.html">Classic C64</a></td><td>1982 breadbin · MOS 6510</td><td><code>c64</code> · <code>CHIPS/C64</code></td><td><code>retro_c64</code></td></tr>
    <tr><td><a href="c64-ultimate.html">C64 Ultimate</a></td><td>2025–2026 FPGA · Artix-7</td><td><code>c64_ultimate</code> · <code>pair/C64Ultimate</code></td><td><code>c64_ultimate_fpga</code></td></tr>
  </table>
  <p><a href="platforms.html">Bootstrap platforms</a> · <a href="batteries.html">Batteries</a></p>
""",
    ),
    "c64-classic.html": (
        "Commodore 64 Classic",
        f"""
  <h1>Commodore 64 (classic) — Queen CHIPS</h1>
  <p>1982 breadbin Commodore 64 — MOS <strong>6510</strong>, VIC-II, SID, dual CIA. Catalog: <code>004-computers/c64</code> · stack <code>retro_c64</code>.</p>
  <aside class="callout callout-warn">
    <strong>Not a g16 target.</strong> Queen emulates via CHIPS scaffold; Grok16 builds on your host only.
  </aside>
  <h2 id="silicon">Silicon stack</h2>
  <ul>
    <li><code>c64_6510</code> — MOS 6510 CPU</li>
    <li><code>c64_vic2</code> · <code>c64_sid6581</code> / <code>c64_sid8580</code> · <code>c64_cia1</code> / <code>c64_cia2</code></li>
    <li>Queen game room <code>app_id: C64</code> · <code>CHIPS/C64</code></li>
  </ul>
  <p>See also <a href="c64-ultimate.html">C64 Ultimate</a> (separate FPGA hardware pair).</p>
""",
    ),
    "c64-ultimate.html": (
        "C64 Ultimate Pair",
        f"""
  <h1>Commodore 64 Ultimate — hardware pair</h1>
  <p>Pair ID <code>pair-c64-ultimate</code> · Grok16 <strong>{DISTRO}</strong> · catalog <code>004-computers/c64_ultimate</code>.</p>

  <aside class="callout callout-warn">
    <strong>g16 does not run on classic 6510 breadbin.</strong> This page documents pairing with the <em>new</em> FPGA machines from <a href="https://commodore.net/computer/">commodore.net</a> only.
  </aside>

  <h2 id="new-c64">The new C64 (2025–2026)</h2>
  <table>
    <tr><th>Model</th><th>Form</th><th>Core</th></tr>
    <tr><td><strong>Commodore 64 Ultimate</strong> (c64u)</td><td>Breadbin · 2025</td><td rowspan="2">AMD Xilinx Artix-7 FPGA · dual SID sockets + 8 FPGA SIDs</td></tr>
    <tr><td><strong>Commodore 64C Ultimate</strong> (c64cu)</td><td>Slimline · late 2026</td></tr>
  </table>
  <p>Media on the C64: <code>.PRG</code> <code>.D64</code> <code>.TAP</code> etc. — loaded on the machine, not compiled by <code>g16</code>.</p>

  <h2 id="grok16-role">What Grok16 does</h2>
  <ul>
    <li>Build <code>g16</code> on normal host platforms (<a href="platforms.html">Linux, macOS, Windows…</a>)</li>
    <li><code>c64_ultimate_fpga</code> chip battery for Queen pairing</li>
    <li>Queen game room <code>c64_ultimate</code> · <code>app_id: C64U</code> · <code>pair/C64Ultimate</code></li>
  </ul>
  <pre><code>export G16_PREFIX=$(pwd) G16_BELT_PROFILE=belt_2_0
./scripts/grok16-toolchain.sh rebuild   # on your Linux/macOS/Windows host</code></pre>
  <p><a href="c64-classic.html">Classic C64</a> · <a href="platforms.html">Bootstrap platforms</a> · <a href="batteries.html">Batteries</a></p>
""",
    ),
    "field-platform.html": (
        "Field Platform",
        f"""
  <h1>2D field platform</h1>
  <p>Grok16 <strong>{DISTRO}</strong> — flat operator plane. Everything on the plane is <strong>auto-field</strong> at depth 0.</p>

  <aside class="callout callout-warn">
    <strong>DO NOT CREATE FIELD FILES.</strong> Standalone <code>.field</code>, depth-field, or subfield JSON heats neighboring fields on the fabric. Gates flatten stray depth, but thermo debt hits adjacent dies first. Place entities on the 2D platform instead.
  </aside>

  <h2 id="rule">Platform rule</h2>
  <table>
    <tr><th>Axis</th><th>Policy</th></tr>
    <tr><td>Plane</td><td>Flat <code>(x, y)</code> — placement implies field</td></tr>
    <tr><td>Depth</td><td><code>max_field_depth: 0</code> always</td></tr>
    <tr><td>Belt</td><td><code>belt_2_0</code> — 8192 redata chunk, 512 die slots</td></tr>
    <tr><td>Production</td><td><code>field_physics</code> — thermal guard, no fast-math</td></tr>
  </table>
  <p>Doctrine: <code>data/grok16-field-platform-doctrine.json</code></p>

  <h2 id="modules">Code modules</h2>
  <table>
    <tr><th>Role</th><th>Path</th></tr>
    <tr><td>Plate amplitude</td><td><code>NewLatest/lib/field-plate-field.py</code></td></tr>
    <tr><td>Panel truth</td><td><code>NewLatest/lib/field-panel-field.py</code></td></tr>
    <tr><td>Depth singularizer</td><td><code>NewLatest/lib/field-depth-singularizer.py</code></td></tr>
    <tr><td>Field sanity</td><td><code>Grok16/forge/g16-field-sanity.py</code></td></tr>
    <tr><td>AmmoCode instill</td><td><code>lib/g16-ammocode-field-instill.py</code></td></tr>
  </table>

  <h2 id="ammocode">AmmoCode</h2>
  <p>AmmoCode is a flat field — no subfields. Resting on a fielded host → <strong>defield</strong>. <code>data/g16-ammocode-field-doctrine.json</code></p>
  <p><a href="safety.html">Safety</a> · <a href="single-fabric.html">Single Fabric</a></p>
""",
    ),
    "znetwork-connect.html": (
        "ZNetwork Connect",
        f"""
  <h1>ZNetwork — secure connect (design)</h1>
  <p>Doctrine: <code>data/grok16-znetwork-field-wire-doctrine.json</code> · status: <strong>design review</strong></p>

  <h2 id="verdict">Verdict</h2>
  <table>
    <tr><th>Question</th><th>Answer</th></tr>
    <tr><td>Connect everyone securely?</td><td><strong>Yes in layers</strong> — not one open global directory today</td></tr>
    <tr><td>Name + address, no phone?</td><td><strong>Wire-point tokens</strong> + sovereign receipts + invites</td></tr>
    <tr><td>Fake accounts?</td><td><strong>Truth gate</strong> + gatekeeper — no username registry</td></tr>
    <tr><td>Address theft?</td><td><strong>No central DB</strong> — local friends list, beacon pins</td></tr>
    <tr><td>Both field computers?</td><td><strong>Direct belt talk</strong> — convert at egress, deconvert at ingress</td></tr>
  </table>

  <h2 id="field-wire">Field expansion down the wire</h2>
  <pre><code>[Field A] → field-io packet (sealed) → wire → verify + deconvert → [Field B]</code></pre>
  <p>Never ship raw field files on the wire. Modules: <code>field-io-packet.py</code>, <code>packet-field.py</code>, <code>connection-gatekeeper.py</code>.</p>

  <h2 id="identity">Identity without cellphone</h2>
  <ul>
    <li><strong>Display name</strong> — public label only, not root of trust</li>
    <li><strong>Wire-point</strong> — opaque HMAC token, rotates with sovereign receipt</li>
    <li><strong>LAN beacon</strong> — polite discovery (AmmoCode port 9555)</li>
    <li><strong>Invite URL</strong> — one-time collab token (WS :9556)</li>
    <li><strong>USB sovereign key</strong> — optional physical anchor (no SMS)</li>
  </ul>

  <h2 id="safety">Safety concerns</h2>
  <table>
    <tr><th>Risk</th><th>Mitigation</th></tr>
    <tr><td>Field files on wire</td><td>Sealed envelopes only; depth 0 at ingress</td></tr>
    <tr><td>Central directory scrape</td><td>No shared plaintext address book</td></tr>
    <tr><td>Sybil operators</td><td>Truth gate + block rating &lt; 25</td></tr>
    <tr><td>Sustained wire heat</td><td><code>field_physics</code> + per-peer token bucket</td></tr>
    <tr><td>ZNetwork ACTIVE early</td><td><code>REVIEW_ONLY</code> default; human checklist</td></tr>
    <tr><td>MITM on open net</td><td>beacon_pin before tunnel_connect</td></tr>
  </table>
  <p>ZNetwork modes: <code>REVIEW_ONLY</code> (default) · <code>SHADOW</code> · <code>ACTIVE</code> (gated). AmmoCode: attach-only.</p>
  <p><a href="field-platform.html">Field Platform</a> · <a href="safety.html">Safety</a></p>
""",
    ),
    "getting-started.html": (
        "Getting Started",
        """
  <h1>Getting Started</h1>
  <p>Grok16 <strong>{DISTRO}</strong> ships a unified <code>g16</code> driver. One binary compiles C and C++; backends live in <code>libexec/grok16/</code>. <code>g++16</code> is a compat symlink.</p>

  <h2>Requirements</h2>
  <ul>
    <li>Linux x86_64</li>
    <li>Host <code>gcc</code>/<code>g++</code>, <code>git</code>, <code>cmake</code>, Python 3 / GPY-16</li>
    <li>GCC build deps (gmp, mpfr, mpc, flex, bison)</li>
    <li>~6 GB disk for <code>vendor/</code>, <code>build/</code>, prefix</li>
  </ul>

  <h2 id="bootstrap">Bootstrap</h2>
  <pre><code>git clone https://github.com/ZacharyGeurts/Grok16.git
cd Grok16
git checkout v{DISTRO}
export G16_PREFIX="$(pwd)"

./scripts/grok16-toolchain.sh bootstrap
./scripts/grok16-toolchain.sh rebuild
./scripts/grok16-toolchain.sh verify</code></pre>

  <h2 id="rebuild">Rebuild modes</h2>
  <table>
    <tr><th>Mode</th><th>Env</th><th>Use when</th></tr>
    <tr><td>Fast (default)</td><td><code>G16_FAST_REBUILD=1</code></td><td>Day-to-day iteration</td></tr>
    <tr><td>Full</td><td><code>G16_FULL_REBUILD=1</code></td><td>distclean + 3-stage bootstrap</td></tr>
    <tr><td>Release</td><td><code>G16_RELEASE_PROFILE=1</code></td><td>Production prefix — LTO + PGO + field_opt</td></tr>
  </table>
  <pre><code>./scripts/grok16-toolchain.sh rebuild
G16_RELEASE_PROFILE=1 ./scripts/grok16-toolchain.sh rebuild</code></pre>

  <h2 id="verify">Verify &amp; gate</h2>
  <pre><code>./scripts/grok16-toolchain.sh verify
./scripts/grok16-toolchain.sh test-battery-expert
./scripts/grok16-toolchain.sh test-battery-release
./scripts/grok16-toolchain.sh test-battery-belt</code></pre>
  <p>See <a href="batteries.html">Batteries</a> for tier breakdown.</p>

  <h2 id="bench">Benchmarks</h2>
  <pre><code>export G16_BELT_PROFILE=belt_2_0
./scripts/grok16-toolchain.sh bench-triad
./scripts/grok16-toolchain.sh field-bench
./scripts/grok16-toolchain.sh bench-all</code></pre>
""".format(DISTRO=DISTRO, G16=G16),
    ),
    "architecture.html": (
        "Architecture",
        """
  <h1>Architecture</h1>
  <figure class="fig-wide">
    <img src="assets/g16-arch-visual.png" alt="Grok16 layer architecture" width="960" height="540" loading="lazy" />
  </figure>

  <h2 id="forge-flow">Forge pipeline</h2>
  <pre><code>forge/grok16-forge.py run gcc_fetch
forge/grok16-forge.py run gcc_configure   # host gcc
forge/grok16-forge.py run gcc_build
forge/grok16-forge.py run gcc_rebuild     # self-host with g16</code></pre>

  <h2 id="unified-driver">Unified driver</h2>
  <table>
    <tr><th>Artifact</th><th>Path</th><th>Role</th></tr>
    <tr><td><code>g16</code></td><td><code>bin/g16</code></td><td>Discern C/C++/Python/ASM + delegate</td></tr>
    <tr><td><code>g16-cc</code></td><td><code>libexec/grok16/g16-cc</code></td><td>C backend (gnu17)</td></tr>
    <tr><td><code>g16-cxx</code></td><td><code>libexec/grok16/g16-cxx</code></td><td>C++ backend (gnu++26)</td></tr>
    <tr><td><code>g16-ld</code></td><td><code>bin/g16-ld</code></td><td>Field linker wrapper → <code>forge/g16-linker.py</code></td></tr>
  </table>

  <h2 id="directories">Directory layout</h2>
  <table>
    <tr><th>Path</th><th>Contents</th></tr>
    <tr><td><code>vendor/gcc</code></td><td>Upstream gcc-15, BASE-VER {G16}</td></tr>
    <tr><td><code>build/gcc</code></td><td>Object files, stage builds</td></tr>
    <tr><td><code>bin/</code></td><td>Installed tools (gitignored until bootstrap)</td></tr>
    <tr><td><code>forge/</code></td><td>Python forge — fetch, build, linker, ironclad</td></tr>
    <tr><td><code>data/</code></td><td>Profiles, doctrines, manifests, bench JSON</td></tr>
  </table>

  <h2 id="selfhost">Self-host stamp</h2>
  <p>Successful rebuild writes <code>SELFHOST.json</code> at repo root with compiler version and timestamp.</p>
""".format(G16=G16),
    ),
    "batteries.html": (
        "Batteries",
        """
  <h1>Battery validation</h1>
  <p>Grok16 {DISTRO} gates releases through layered batteries. Run locally before tagging or deploying a prefix.</p>

  <figure class="fig-wide">
    <img src="assets/battery-gate.svg" alt="Battery tier diagram" width="920" height="200" />
  </figure>

  <h2 id="smoke">Smoke — <code>test-battery</code></h2>
  <pre><code>./scripts/grok16-toolchain.sh test-battery</code></pre>
  <p>paths · discern · status · verify · manifest · ironclad sanity · hostess gate</p>

  <h2 id="expert">Expert — <code>test-battery-expert</code></h2>
  <pre><code>./scripts/grok16-toolchain.sh test-battery-expert</code></pre>
  <p>Smoke + ironclad verify + linker verify + RTX gate + <code>expert</code> profile compile</p>

  <h2 id="heavy">Heavy — <code>test-battery-heavy</code></h2>
  <pre><code>G16_RELEASE_PROFILE=1 ./scripts/grok16-toolchain.sh test-battery-heavy</code></pre>
  <p>Expert chain + <code>profile=heavy</code> bench + field-bench under release profile</p>

  <h2 id="release">Release — <code>test-battery-release</code></h2>
  <pre><code>G16_RELEASE_PROFILE=1 ./scripts/grok16-toolchain.sh test-battery-release</code></pre>
  <table>
    <tr><th>Step</th><th>What it proves</th></tr>
    <tr><td>heavy</td><td>Release-profile compile + bench</td></tr>
    <tr><td>py-battery</td><td><code>tests/test_g16_battery.py</code></td></tr>
    <tr><td>forever-battery</td><td>Hostess7 forever profile contract</td></tr>
    <tr><td>binutils-battery</td><td>g16-as / g16-ld / g16-objdump</td></tr>
    <tr><td>verify</td><td>Full verify incl. linker link smoke</td></tr>
  </table>

  <h2 id="belt">Belt — <code>test-battery-belt</code> (2.0)</h2>
  <pre><code>./scripts/grok16-toolchain.sh test-battery-belt</code></pre>
  <p>Doctrine <code>data/grok16-single-fabric-doctrine.json</code> · profiles <code>belt_1_0</code> / <code>belt_2_0</code> · <code>tests/test_g16_belt_battery.py</code> · triad artifact optional.</p>

  <h2 id="triage">Failure triage</h2>
  <ul>
    <li><strong>Linker / libgcc_s</strong> — ensure <code>file lib64/libgcc_s.so.1</code> shows <em>shared object</em>, not PIE executable</li>
    <li><strong>LTO</strong> — profile flags normalize <code>-flto=thin</code> per compiler capability</li>
    <li><strong>PGO</strong> — use flags only when <code>data/pgo/*.gcda</code> exist</li>
    <li><strong>g16-ld missing</strong> — <code>./scripts/grok16-binutils.sh install</code></li>
  </ul>
""".format(DISTRO=DISTRO),
    ),
    "toolkits.html": (
        "Toolkits",
        """
  <h1>In-tree toolkits</h1>
  <p>Grok16 {DISTRO} carries rebuilt toolkits in-tree. Manifest: <code>data/grok16-toolkits.json</code>. No sibling-repo bootstrap required for core languages.</p>

  <h2 id="gpy16">GPY-16 (built-in)</h2>
  <table>
    <tr><th>Item</th><th>Path</th></tr>
    <tr><td>Tree</td><td><code>python/</code> — GrokVM</td></tr>
    <tr><td>Driver</td><td><code>bin/gpy-16</code> (from <code>scripts/gpy-16</code>)</td></tr>
    <tr><td>Discern</td><td><code>g16 foo.py</code> auto-routes to GPY-16</td></tr>
  </table>

  <h2 id="binutils">Field binutils</h2>
  <pre><code>./scripts/grok16-binutils.sh bootstrap
./scripts/grok16-binutils.sh install
./scripts/grok16-binutils.sh verify</code></pre>
  <p>Tools: <code>g16-as</code>, <code>g16-ld</code>, <code>g16-objdump</code>, <code>g16-ar</code>, <code>g16-nm</code>, …</p>

  <h2 id="languages">Language drivers</h2>
  <p>Install language wrappers to prefix:</p>
  <pre><code>./scripts/grok16-languages.sh install
./scripts/grok16-languages.sh discern
./scripts/grok16-languages.sh hostess-gate</code></pre>
  <p>Rust/Go/Zig/Fortran/D/Ada/ObjC drivers link through <code>g16-ld</code> where applicable.</p>
""".format(DISTRO=DISTRO),
    ),
    "linker.html": (
        "Linker",
        """
  <h1>G16 field linker</h1>
  <p><code>g16-ld</code> is a bash wrapper around <code>forge/g16-linker.py</code>. BFD backend: <code>libexec/grok16/g16-ld-bfd</code>. Doctrine: <code>data/g16-linker-doctrine.json</code> — 16 active targets.</p>

  <figure class="fig-wide">
    <img src="assets/linker-flow.svg" alt="Linker pass flow" width="880" height="220" />
  </figure>

  <h2 id="verify">Verify</h2>
  <pre><code>./scripts/grok16-toolchain.sh verify   # includes linker smoke
pythong forge/g16-linker.py targets
pythong forge/g16-linker.py json</code></pre>

  <h2 id="mandate">ELF mandate flags</h2>
  <table>
    <tr><th>Link kind</th><th>Injected flags</th></tr>
    <tr><td>Executable</td><td><code>-pie -zrelro -znow -znoexecstack</code></td></tr>
    <tr><td><code>-shared</code></td><td><code>-zrelro -znow -znoexecstack</code> — <strong>no -pie</strong> (1.0)</td></tr>
    <tr><td><code>-r</code> / <code>-static</code></td><td>none</td></tr>
  </table>

  <h2 id="targets">Target families</h2>
  <p>linux-gnu (x86_64, aarch64, arm, riscv), android (NDK), darwin/ios (mach-o), win32 (PE), bare-elf. <a href="c64-ultimate.html">C64 Ultimate</a> is a hardware pair — not a linker backend. <a href="c64-classic.html">Classic C64</a> is Queen CHIPS only.</p>
  <p>Env overrides: <code>G16_LINK_TARGET</code>, <code>ANDROID_NDK_ROOT</code>, <code>G16_CROSS_PREFIX</code>.</p>
""",
    ),
    "single-fabric.html": (
        "Single Fabric",
        """
  <h1>Single fabric (2.0)</h1>
  <p><strong>Single fabric</strong> is the Grok16 2.0 technology: fixed-size <strong>knowing</strong> on one belt die — not nested fields, not monolithic blast.</p>
  <p>Doctrine: <code>data/grok16-single-fabric-doctrine.json</code> · Citation: <code>ironclad:field_sanity:5</code></p>

  <h2 id="rules">Rules</h2>
  <table>
    <tr><th>Layer</th><th>Rule</th></tr>
    <tr><td>Belt</td><td><code>belt_2_0</code> — 8192 redata chunk, wave-massive, <strong>single-location reads</strong></td></tr>
    <tr><td>Field</td><td>One amplitude at depth 0 — parallel I/O fans in, truth stays single</td></tr>
    <tr><td>Time</td><td>Linear sovereign clock — <code>ironclad:time:1</code>, not geometry <code>t</code></td></tr>
    <tr><td>Safety</td><td>Depth-field creation <strong>forbidden</strong> — stripped at every gate</td></tr>
  </table>

  <h2 id="profiles">Belt profiles</h2>
  <table>
    <tr><th>Profile</th><th>Role</th></tr>
    <tr><td><code>belt_1_0</code></td><td>1.0 baseline (aliases <code>field_opt</code>) — triad compare</td></tr>
    <tr><td><code>belt_2_0</code></td><td><strong>2.0 production</strong> — single fabric dispatch, 512 die slots</td></tr>
  </table>
  <pre><code>export G16_BELT_PROFILE=belt_2_0
./scripts/grok16-toolchain.sh bench-triad</code></pre>
  <p>See <a href="profiles.html#belt">Profiles</a> · <a href="performance.html#triad">Belt triad</a> · <a href="safety.html">Safety</a></p>
""",
    ),
    "safety.html": (
        "Safety",
        f"""
  <h1>Safety — Grok16 {DISTRO}</h1>

  <aside class="callout callout-warn">
    <strong>DO NOT CREATE FIELD FILES.</strong> They heat neighboring fields. Use the <a href="field-platform.html">2D field platform</a> — placement is auto-field at depth 0.
  </aside>

  <h2 id="depth">Depth fields sealed and destroyed</h2>
  <table>
    <tr><th>Gate</th><th>Behavior</th></tr>
    <tr><td><code>field-depth-singularizer</code></td><td>Seal and destroy <code>field_depth</code>, zero nested layers, ledger violations</td></tr>
    <tr><td>Queen field-net</td><td><code>depth_field_impossible: true</code> on classify</td></tr>
    <tr><td>Queen browser</td><td>Navigate strips depth before tab persist</td></tr>
    <tr><td>NEXUS HTTP</td><td>302 redirect when <code>?field_depth=</code> present</td></tr>
  </table>
  <p><strong>Rule:</strong> one field, depth zero always. Creation cannot persist.</p>

  <h2 id="ironclad">Ironclad meld</h2>
  <ul>
    <li><code>data/g16-ironclad-meld.json</code> — time linear, single fabric, field sanity verses</li>
    <li><code>g16-ironclad-sanity</code> gate in forge and batteries</li>
    <li><code>G16_FIELD_SAFETY_MANDATE_v1</code> on field targets</li>
  </ul>

  <h2 id="time">Sovereign time</h2>
  <p>Time is linear (<code>ironclad:time:1</code>). G1ID meld uses <code>linear_ns</code> only — <code>t</code> forbidden in geometry.</p>

  <h2 id="field-physics">field_physics profile</h2>
  <table>
    <tr><th>Profile</th><th>-ffast-math</th><th>Thermal guard</th></tr>
    <tr><td>belt_2_0 / field_opt</td><td>yes</td><td>bench throughput</td></tr>
    <tr><td><strong>field_physics</strong></td><td><strong>no</strong></td><td><strong>production NEXUS/CANVAS</strong></td></tr>
  </table>

  <h2 id="integrate">Integrate</h2>
  <pre><code>./scripts/grok16-integrate.sh</code></pre>
  <p>See <a href="integration.html">Integration</a> · <a href="znetwork-connect.html">ZNetwork</a></p>
""",
    ),
    "performance.html": (
        "Performance",
        f"""
  <h1>Performance</h1>
  <p>Measured: Linux x86_64, <code>g16 (Grok16-{G16}) {G16}</code>, gnu++26. Repo: <code>PERFORMANCE.md</code>.</p>

  <h2 id="speed-bench">Speed bench (report v{meta['report']})</h2>
  <p>Suite <code>{meta['suite']}</code> @ <code>{meta['suite_ver']}</code> — compile ms + execution ops/s. Full manual: <a href="speed-bench.html">Speed Bench</a>.</p>
  <pre><code>SPEED_DEMO_TARGET_SEC=3 ./scripts/grok16-toolchain.sh exec-full-bench
./scripts/grok16-toolchain.sh exec-compare</code></pre>
  <table>
    <tr><th>Runner</th><th>Compile (ms)</th><th>ops/s</th></tr>
{table_compact}
  </table>

  <figure class="fig-wide">
    <img src="assets/triad-chart.svg" alt="Belt triad compile and run comparison" width="920" height="280" loading="lazy" />
    <figcaption>bench-triad — host gcc vs belt_1_0 vs belt_2_0</figcaption>
  </figure>

  <h2 id="triad">Belt triad (bench-triad)</h2>
  <p>Workload: <code>examples/field-nexus-bench</code> — 240 frames, FieldX86 + entropy + wave + NEXUS.</p>
  <table>
    <tr><th>Toolchain</th><th>Profile</th><th>compile_ms</th><th>run wall_ms</th><th>binary bytes</th></tr>
{triad_table}
  </table>
  <p><code>belt_1_0</code> matches host runtime; <code>belt_2_0</code> trades compile time for production single-fabric belt.</p>
  <pre><code>./scripts/grok16-toolchain.sh bench-triad
cat data/bench/triad-latest.json</code></pre>

  <figure class="fig-wide">
    <img src="assets/compare-chart.svg" alt="Field g16 vs host compile comparison" width="920" height="300" loading="lazy" />
    <figcaption>bench-compare — field g16 vs host gcc/g++</figcaption>
  </figure>

  <figure class="fig-wide">
    <img src="assets/bench-all-chart.svg" alt="bench-all profile suite" width="920" height="260" loading="lazy" />
    <figcaption>bench-all — field-nexus-bench across profiles</figcaption>
  </figure>

  <h2 id="field-bench">Field-Opt vs baseline</h2>
  <table>
    <tr><th>Build</th><th>Flags</th><th>kernel wall_ms</th><th>binary bytes</th></tr>
    <tr><td>baseline</td><td>-std=gnu++26 -O2</td><td>2.65</td><td>17144</td></tr>
    <tr><td>field_opt / belt_1_0</td><td>profile flags</td><td>2.11–2.19</td><td>22616</td></tr>
  </table>
  <p>Delta: ~19% faster kernel vs -O2 on same source.</p>

  <h2 id="bench-all">Profile suite (bench-all)</h2>
  <table>
    <tr><th>Profile</th><th>compile_ms</th><th>run_ms</th><th>bytes</th><th>kernel</th></tr>
    <tr><td>field_opt</td><td>828–874</td><td>4–5</td><td>22616</td><td>wall_ms ~2.1</td></tr>
    <tr><td>belt_2_0</td><td>~3708</td><td>~5</td><td>22840</td><td>single fabric</td></tr>
    <tr><td>ai</td><td>735</td><td>6–7</td><td>18232</td><td>wall_ms ~4.0</td></tr>
    <tr><td>vulkan_rtx</td><td>864–876</td><td>4–5</td><td>22728</td><td>wall_ms ~2.1</td></tr>
  </table>

  <h2 id="reproduce">Reproduce</h2>
  <pre><code>export G16_PREFIX="$(pwd)"
export G16_BELT_PROFILE=belt_2_0
./scripts/grok16-toolchain.sh bench-triad
./scripts/grok16-toolchain.sh field-bench
./scripts/grok16-toolchain.sh bench-all</code></pre>

  <h2 id="pgo">PGO</h2>
  <pre><code>./scripts/grok16-toolchain.sh profile
G16_ENABLE_PGO=1 ./scripts/grok16-toolchain.sh field-bench</code></pre>
""",
    ),
    "integration.html": (
        "Integration",
        """
  <h1>Integration</h1>
  <p>Requires Grok16 <strong>v{DISTRO}</strong> with <code>test-battery-release</code> + <code>test-battery-belt</code> green.</p>

  <h2 id="integrate">Auto-integrate (2.0)</h2>
  <pre><code>./scripts/grok16-integrate.sh
./scripts/grok16-toolchain.sh integrate-ammoos
./scripts/grok16-toolchain.sh verify-ammoos-surfaces</code></pre>
  <p>Wires canonical prefix + <code>G16_BELT_PROFILE=belt_2_0</code> to Queen, World_Redata, ZOCR/Final_Ear, PythonG, and <strong>AmmoOS</strong> (SG/NewLatest). Env: <code>data/grok16-integrate.env</code> · Manifest: <code>data/grok16-ammoos-integrate.json</code></p>

  <h2 id="ammoos">AmmoOS incorporation</h2>
  <p>Review: <code>docs/AMMOOS-REVIEW-FOR-GROK-BUILD.md</code> · Profile: <code>ammoos</code> in <code>data/grok16-profiles.json</code> · CMake: <code>cmake/grok16-profile-ammoos.cmake</code> · Smoke: <code>examples/ammoos-smoke/</code></p>
  <p>Stack layers (NEXUS C2 → ZNetwork → Queen → AmmoOS inside Queen) documented in AmmoOS <code>data/field-stack-layer-doctrine.json</code>.</p>

  <h2 id="gates">Safety at consumers</h2>
  <p>Integrated SG tree enforces <strong>single fabric</strong> safety:</p>
  <table>
    <tr><th>Consumer</th><th>Depth field</th><th>Ironclad</th></tr>
    <tr><td>Queen field-net</td><td><code>depth_field_impossible</code></td><td>classify strip</td></tr>
    <tr><td>Queen browser</td><td>navigate enforce</td><td>tab URL clean</td></tr>
    <tr><td>NEXUS panel</td><td>HTTP 302 strip</td><td>field-depth-singularizer</td></tr>
    <tr><td>Field sanity</td><td>integral preflight</td><td><code>ironclad:field_sanity:4</code></td></tr>
  </table>
  <p>Doctrine: <code>NewLatest/data/single-field-depth-doctrine.json</code> · <a href="safety.html">Safety manual</a></p>

  <h2 id="wrdt">World_Redata</h2>
  <pre><code>cd World_Redata
./build-cpp.sh
PYTHONPATH=. pythong -m redata.cli parity
PYTHONPATH=. pythong -m redata.cli security</code></pre>

  <h2 id="env">Downstream env</h2>
  <pre><code>export G16_PREFIX=/path/to/Grok16
export G16_BELT_PROFILE=belt_2_0
export WRDT_G16_PREFIX="$G16_PREFIX"
source data/grok16-integrate.env</code></pre>

  <h2 id="ironclad">Ironclad</h2>
  <p><code>data/g16-ironclad-meld.json</code> — single fabric, linear time, field sanity absorbed at forge link pass.</p>
""".format(DISTRO=DISTRO),
    ),
    "mcp.html": (
        "MCP",
        f"""
  <h1>MCP — Model Context Protocol</h1>
  <p>Grok16 <strong>{DISTRO}</strong> ships a <strong>custom stdio MCP server</strong> for agents. Doctrine: <code>data/grok16-mcp.json</code> · Server: <code>mcp/grok16_mcp_server.py</code></p>

  <h2 id="install">Install</h2>
  <pre><code>pip install -r requirements-mcp.txt
export GROK16_ROOT="$(pwd)" G16_PREFIX="$(pwd)"</code></pre>

  <h2 id="tools">Tools</h2>
  <table>
    <tr><th>Tool</th><th>Description</th></tr>
    <tr><td><code>grok16_version</code></td><td>Distro {DISTRO}, g16 {G16}, belt/speed_bench stamps</td></tr>
    <tr><td><code>grok16_toolchain</code></td><td>Allowlisted <code>grok16-toolchain.sh</code> commands</td></tr>
    <tr><td><code>grok16_rtx_gate</code></td><td><code>queen_rtx</code> / <code>vulkan_rtx</code> permit</td></tr>
    <tr><td><code>grok16_speed_bench</code></td><td>Published <code>field-exec-full-bench.json</code></td></tr>
    <tr><td><code>grok16_power_sort</code></td><td>Power sort doctrine + bench panel</td></tr>
    <tr><td><code>grok16_forge_status</code></td><td>Bootstrap/build forge JSON</td></tr>
  </table>

  <h2 id="allowlist">Toolchain allowlist</h2>
  <p><code>status</code>, <code>verify</code>, <code>paths</code>, <code>integrate</code>, <code>exec-bsp-bench</code>, <code>test-battery-belt</code>, <code>test-battery-release</code></p>

  <h2 id="github">AmmoOS GitHub MCP (separate)</h2>
  <p>AmmoOS publish uses the private GitHub MCP layer in NewLatest — <code>data/ammoos-mcp-layer.json</code>, stdio <code>scripts/github-mcp-stdio.sh</code>, env <code>~/.config/sg/github-mcp.env</code>.</p>
  <p><a href="integration.html">Integration</a> · <a href="release.html">Release</a></p>
""",
    ),
    "profiles.html": (
        "Profiles",
        """
  <h1>Build Profiles</h1>
  <p>Defined in <code>data/grok16-profiles.json</code>. Default C++ standard: <code>gnu++26</code>. Distro 2.0 default belt: <code>belt_2_0</code>.</p>

  <h2 id="belt">Belt profiles (2.0)</h2>
  <table>
    <tr><th>Name</th><th>CMake</th><th>Use</th></tr>
    <tr id="belt-2"><td><strong>belt_2_0</strong></td><td>grok16-profile-belt-2.cmake</td><td>Single fabric production — 8192 chunk, wave-massive, 512 slots</td></tr>
    <tr id="belt-1"><td>belt_1_0</td><td>grok16-profile-field-opt.cmake</td><td>1.0 baseline (field_opt) — triad compare</td></tr>
  </table>
  <pre><code>export G16_BELT_PROFILE=belt_2_0
G16_BENCH_PROFILE=belt_2_0 ./scripts/grok16-toolchain.sh bench</code></pre>

  <h2>Classic profiles</h2>
  <table>
    <tr><th>Name</th><th>CMake</th><th>Bench source</th><th>Use</th></tr>
    <tr id="field-opt"><td>field_opt</td><td>grok16-profile-field-opt.cmake</td><td>examples/field-nexus-bench/</td><td>FieldX86, entropy, NEXUS (1.0 primary)</td></tr>
    <tr id="ai"><td>ai</td><td>grok16-profile-ai.cmake</td><td>examples/ai-matrix-bench/</td><td>Matrix / scoring loops</td></tr>
    <tr id="field-compute"><td>field_compute</td><td>grok16-profile-field.cmake</td><td>examples/field-canvas-kernel/</td><td>CANVAS-style dispatch</td></tr>
    <tr id="vulkan-rtx"><td>vulkan_rtx</td><td>grok16-profile-vulkan.cmake</td><td>field-nexus-bench</td><td>AVX2/FMA CPU kernels</td></tr>
  </table>

  <h2 id="bench">Bench profile selection</h2>
  <pre><code>G16_BENCH_PROFILE=belt_2_0 ./scripts/grok16-toolchain.sh bench
G16_FIELD_SPEED=1 ./scripts/grok16-toolchain.sh field-bench
./scripts/grok16-toolchain.sh bench-triad</code></pre>

  <h2 id="mandate">Safety mandate</h2>
  <p>All field targets include <code>cmake/g16-field-mandate.cmake</code> (<code>G16_FIELD_SAFETY_MANDATE_v1</code>). See <a href="safety.html">Safety</a>.</p>
""",
    ),
    }

SEARCH_INDEX = [
    {"t": "field platform", "p": "field-platform.html", "g": "5.0", "d": "2D auto-field DO NOT CREATE FIELD FILES heat"},
    {"t": "znetwork connect", "p": "znetwork-connect.html", "g": "5.0", "d": "field wire egress convert ingress deconvert identity"},
    {"t": "do not create field files", "p": "field-platform.html", "g": "Warning", "d": "field files heat neighboring fields depth zero"},
    {"t": "grok16 5.1", "p": "index.html", "g": "Home", "d": "Stack fabric G1-G15 MCP stdio belt_2_0"},
    {"t": "mcp grok16", "p": "mcp.html", "g": "Agents", "d": "Custom stdio MCP toolchain bench rtx gate"},
    {"t": "grok16 5.0", "p": "index.html", "g": "Home", "d": "Version one clean start belt_2_0 binary package"},
    {"t": "speed bench", "p": "speed-bench.html", "g": "5.0", "d": "Versioned compile ms execution ops/s report v5.0.0"},
    {"t": "exec-full-bench", "p": "speed-bench.html#reproduce", "g": "Bench", "d": "field-exec-full-bench compile and execution"},
    {"t": "bench-refresh", "p": "release.html#charts", "g": "4.7", "d": "Regenerate triad compare bench-all charts SVG"},
    {"t": "uncompiled", "p": "uncompiled.html", "g": "4.7", "d": "Python interpreter C C++ chamber compile ahead"},
    {"t": "cmake linking", "p": "cmake-linking.html", "g": "Build", "d": "grok16-toolchain.cmake g16-ld speed_demo"},
    {"t": "speed_demo", "p": "speed-bench.html", "g": "Suite", "d": "speed_demo v1.1.0 FieldX86 kernel bench"},
    {"t": "single fabric", "p": "single-fabric.html", "g": "2.0", "d": "One belt die one field amplitude knowing fixed-size"},
    {"t": "belt_2_0", "p": "profiles.html#belt-2", "g": "Profile", "d": "2.0 production belt chunked redata 8192"},
    {"t": "bench-triad", "p": "performance.html#triad", "g": "Bench", "d": "host gcc vs belt_1_0 vs belt_2_0"},
    {"t": "test-battery-belt", "p": "batteries.html#belt", "g": "Battery", "d": "2.0 belt validation atop release"},
    {"t": "grok16-integrate", "p": "integration.html#integrate", "g": "Integrate", "d": "Auto-wire Queen WRDT ZOCR belt_2_0"},
    {"t": "depth fields sealed and destroyed", "p": "safety.html#depth", "g": "Safety", "d": "field_depth sealed and destroyed at gates"},
    {"t": "ironclad:time:1", "p": "safety.html#time", "g": "Safety", "d": "Sovereign linear time linear_ns only"},
    {"t": "test-battery-release", "p": "batteries.html#release", "g": "Battery", "d": "Production gate heavy py forever binutils verify"},
    {"t": "test-battery-expert", "p": "batteries.html#expert", "g": "Battery", "d": "Ironclad linker RTX expert profile"},
    {"t": "g16-ld", "p": "linker.html", "g": "Linker", "d": "Field linker 18 targets mandate flags"},
    {"t": "C64", "p": "c64.html", "g": "Pair", "d": "Commodore 64 classic vs Ultimate catalog lanes"},
    {"t": "C64 classic", "p": "c64-classic.html", "g": "Queen", "d": "retro_c64 breadbin 6510 CHIPS scaffold"},
    {"t": "C64 Ultimate", "p": "c64-ultimate.html", "g": "Pair", "d": "pair-c64-ultimate FPGA hardware pair"},
    {"t": "platforms", "p": "platforms.html", "g": "Release", "d": "17-platform bootstrap matrix"},
    {"t": "GPY-16", "p": "toolkits.html#gpy16", "g": "Toolkit", "d": "Built-in Python GrokVM gpy-16"},
    {"t": "v4.7.1", "p": "release.html", "g": "Release", "d": "Bench refresh charts gcc-14 legacy isolation chamber"},
    {"t": "queen theme", "p": "index.html", "g": "UI", "d": "Queen navy gold emerald manual theme"},
    {"t": "bootstrap", "p": "getting-started.html#bootstrap", "g": "Workflow", "d": "First GCC fetch host build install"},
    {"t": "g16 unified", "p": "architecture.html#unified-driver", "g": "Driver", "d": "Single g16 C C++ Python discern"},
    {"t": "field_opt", "p": "profiles.html#field-opt", "g": "Profile", "d": "1.0 primary Field throughput belt_1_0 alias"},
    {"t": "G16_BELT_PROFILE", "p": "profiles.html#belt", "g": "Env", "d": "Default belt_2_0 single fabric dispatch"},
    {"t": "G16_RELEASE_PROFILE", "p": "getting-started.html#rebuild", "g": "Env", "d": "LTO PGO production rebuild"},
    {"t": "gnu++26", "p": "field-primer.html#standard", "g": "C++", "d": "Default C++ standard"},
    {"t": "field research", "p": "field-research.html", "g": "Book", "d": "Field Research book technology spine"},
    {"t": "combinatorics", "p": "field-research.html", "g": "Book", "d": "Ch7 combinatorics endpoint compatibility layers"},
    {"t": "field-research-book", "p": "field-research.html", "g": "Doctrine", "d": "g16-field-research-book.json verify publish"},
]


def write_pages() -> None:
    for name, (title, body) in pages_dict().items():
        (ROOT / name).write_text(page(title, body), encoding="utf-8")
        print(f"wrote {name}")


def write_search() -> None:
    (ROOT / "search-index.json").write_text(
        json.dumps(SEARCH_INDEX, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote search-index.json")


def patch_legacy_pages() -> None:
    """Bump cache version and nav on hand-maintained pages."""
    legacy = [
        "field-primer.html", "field-research.html", "reference.html", "concepts.html", "io.html",
        "master-coder.html", "master-coder-c.html", "master-coder-cxx.html",
    ]
    new_links = "\n".join(
        f'      <a href="{h}">{l}</a>' for h, l in NAV if h != "index.html"
    )
    new_nav_block = f"""    <div class="nav-links">
      <a href="index.html">Home</a>
{new_links}
    </div>"""
    cache_pat = re.compile(r"manual-(?:css|theme|search|layout)\.js\?v\d+|manual\.css\?v\d+")
    for fname in legacy:
        path = ROOT / fname
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text = cache_pat.sub(lambda m: m.group(0).rsplit("v", 1)[0] + CACHE, text)
        text = text.replace('<span class="nav-version">v16.1.1</span>',
                            f'<span class="nav-version">distro {DISTRO}</span><span class="nav-g16">g16 @ {G16}</span>')
        text = text.replace(f'<span class="nav-version">distro 1.0.0</span><span class="nav-g16">g16 @ 16.1.1</span>',
                            f'<span class="nav-version">distro {DISTRO}</span><span class="nav-g16">g16 @ {G16}</span>')
        text = text.replace(f'<span class="nav-version">distro 2.0.0</span><span class="nav-g16">g16 @ {G16}</span>',
                            f'<span class="nav-version">distro {DISTRO}</span><span class="nav-g16">g16 @ {G16}</span>')
        text = text.replace("<strong>Grok16 Manual</strong>", "<strong>Grok16</strong>")
        if '<div class="nav-links">' in text:
            text = re.sub(
                r'<div class="nav-links">.*?</div>',
                new_nav_block,
                text,
                count=1,
                flags=re.DOTALL,
            )
        path.write_text(text, encoding="utf-8")
        print(f"patched {fname}")


def patch_concepts_single_fabric() -> None:
    """Insert 2.0 single-fabric callout on concepts page."""
    path = ROOT / "concepts.html"
    if not path.is_file():
        return
    marker = '<aside class="callout">\n    <strong>Workflow tip:</strong>'
    insert = """  <aside class="callout callout-accent">
    <strong>Single fabric (2.0):</strong> Knowing is fixed-size on one belt die — parallel I/O fans in, truth stays one amplitude at depth 0. Time is linear (<code>ironclad:time:1</code>). See <a href="single-fabric.html">Single Fabric</a> and <a href="safety.html">Safety</a>.
  </aside>

"""
    text = path.read_text(encoding="utf-8")
    if "Single fabric (2.0)" not in text and marker in text:
        text = text.replace(marker, insert + marker, 1)
        path.write_text(text, encoding="utf-8")
        print("patched concepts.html (single fabric callout)")


def main() -> int:
    bench = load_bench()
    meta = bench_meta(bench)
    write_readme_index(
        page,
        distro=meta["distro"],
        g16=G16,
        report=meta["report"],
    )
    write_pages()
    write_search()
    patch_legacy_pages()
    patch_concepts_single_fabric()
    gen = ROOT / "gen-master-pages.py"
    if gen.is_file():
        subprocess.run([sys.executable, str(gen)], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
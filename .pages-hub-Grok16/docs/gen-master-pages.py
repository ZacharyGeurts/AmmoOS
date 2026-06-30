#!/usr/bin/env pythong
"""Generate Master Coder hub + C + C++ manual pages."""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
DISTRO = "1.0.0"
VER = "16.1.1"
CACHE = "v8"

HEAD = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>Grok16 Manual — {{title}}</title>
  <script>
  (function (d) {{
    try {{
      var t = localStorage.getItem("g16-theme");
      if (t !== "dark" && t !== "light") {{
        t = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      }}
      d.documentElement.setAttribute("data-theme", t);
    }} catch (e) {{
      d.documentElement.setAttribute("data-theme", "light");
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

NAV = f"""  <nav>
    <div class="nav-top">
      <div class="nav-brand"><strong>Grok16</strong> <span class="nav-version">distro {DISTRO}</span> <span class="nav-g16">g16 @ {VER}</span></div>
      <div class="nav-controls" aria-label="Display preferences">
        <div class="control-chip">
          <label class="control-label" for="g16-font-scale">Size</label>
          <select id="g16-font-scale" class="g16-select" aria-label="Font size">
            <option value="0.875">S</option>
            <option value="1" selected>M</option>
            <option value="1.125">L</option>
            <option value="1.25">XL</option>
            <option value="1.5">XXL</option>
          </select>
        </div>
        <div class="theme-switch" role="group" aria-label="Color theme">
          <button type="button" class="g16-seg" id="g16-theme-light" data-theme="light" aria-pressed="false">
            <span class="seg-icon" aria-hidden="true">☀</span><span class="seg-text">Light</span>
          </button>
          <button type="button" class="g16-seg" id="g16-theme-dark" data-theme="dark" aria-pressed="false">
            <span class="seg-icon" aria-hidden="true">☾</span><span class="seg-text">Dark</span>
          </button>
        </div>
      </div>
    </div>
    <div class="nav-links">
      <a href="index.html">Home</a>
      <a href="release.html">Release 1.0</a>
      <a href="getting-started.html">Getting Started</a>
      <a href="architecture.html">Architecture</a>
      <a href="batteries.html">Batteries</a>
      <a href="toolkits.html">Toolkits</a>
      <a href="linker.html">Linker</a>
      <a href="profiles.html">Profiles</a>
      <a href="performance.html">Performance</a>
      <a href="integration.html">Integration</a>
      <a href="concepts.html">Concepts</a>
      <a href="master-coder.html">Master Coder</a>
      <a href="field-primer.html">Field Primer</a>
      <a href="reference.html">Reference</a>
    </div>
  </nav>
"""

FOOT = """  <footer><a href="index.html">Index</a> · <a href="master-coder.html">Master Coder</a></footer>
</body>
</html>
"""


def page(title: str, body: str) -> str:
    return HEAD.replace("{{title}}", title) + NAV + body + FOOT


def table(rows: list[tuple]) -> str:
    out = ['  <table class="idx idx-rich">', '    <tr><th>#</th><th>Item</th><th>Short</th><th>Detail</th></tr>']
    for i, (href, name, short, detail) in enumerate(rows, 1):
        link = f'<a href="{href}">{name}</a>' if href else name
        out.append(f'    <tr><td class="idx-num">{i}</td><td>{link}</td><td class="tip">{short}</td><td class="idx-detail">{detail}</td></tr>')
    out.append("  </table>")
    return "\n".join(out)


C_ROWS = [
    ("reference.html#unified-g16", "g16", "Unified driver", "Single ELF at bin/g16. Inspects argv[0], -std=, -x, and source extensions (.c vs .cpp). Dispatches to libexec/grok16/g16-cc for C. No separate C command — always g16."),
    ("architecture.html#unified-driver", "g16-cc", "C backend", "Relocated GCC C driver after install. Real ELF from upstream program-transform. Unified g16 execv() here when C mode is detected."),
    ("field-primer.html#standard-c", "g16 -std=gnu17", "Default C standard", "G16_C_STD defaults to gnu17 (C17 + GNU extensions). Applied when compiling .c files or when -std=gnu17|c17|… is passed. Override per translation unit."),
    ("getting-started.html#verify", "verify (C leg)", "C smoke compile", "grok16-toolchain.sh verify compiles verify.c with g16 -std=${G16_C_STD}. Proves unified driver reaches g16-cc and frontend accepts gnu17."),
    ("profiles.html#flags-c", "PROFILE c", "C compile flags", "pythong grok16-profile-flags.py field_opt c — emits -std=gnu17 -O3 -march=native plus profile -D macros. Use for C kernels and L0 glue."),
    ("profiles.html#flags-c", "PROFILE c_link", "C link flags", "Same link_flags as CXX profiles (LTO/OpenMP). Unified g16 still auto-selects g16-cc for link when inputs are C-only."),
    ("profiles.html#flags-c", "PROFILE c_pgo_gen", "C PGO generate", "Adds -fprofile-generate=${GROK16_ROOT}/data/pgo to C flags. Run profile command, then rebuild consumers with G16_ENABLE_PGO=1."),
    ("profiles.html#flags-c", "PROFILE c_pgo_use", "C PGO use", "Adds -fprofile-use for C builds after training. Pairs with cxx_pgo_use for mixed projects."),
    ("reference.html#env-g16-c-std", "G16_C_STD", "C standard env", "Exported by grok16-config.sh from data/grok16-version.json. Default gnu17. Used by verify, CMake GROK16_C_STD, and manual g16 invocations."),
    ("reference.html#env-force-c", "G16_FORCE_C=1", "Force C backend", "Override detection — unified g16 always execs g16-cc even for .cpp (debug only)."),
    ("getting-started.html#bootstrap", "bootstrap", "First build", "Fetch GCC 15, patch BASE-VER 16.1.1, host-build, install, relocate backends, install unified g16. Produces working C path without separate gcc binary name."),
    ("getting-started.html#rebuild", "rebuild", "Self-host", "Self-host uses libexec/g16-cc and g16-cxx as CC/CXX during gcc_rebuild — not the unified wrapper — avoiding bootstrap recursion."),
    ("reference.html#cmd-install", "install", "Post-install", "Regenerates VERSION, cmake, manifest. Confirms g16 -dumpversion == 16.1.1. Re-runs driver/Makefile install if present."),
    ("reference.html#cmd-paths", "paths", "Paths dump", "Prints G16_DRIVER, G16_BACKEND_CC, G16_C_STD, GROK16_ROOT, G16_PREFIX. Use before scripting C builds."),
    ("performance.html#bench", "bench (C future)", "C benchmarks", "16.1.1 benches remain CXX-first; C flags available via PROFILE c for mixed stacks. Add examples/minimal-c-project to CI smoke."),
    ("integration.html#gates", "build-cpp.sh", "WRDT L2", "World_Redata C++ engine; C sources in redata use host python. Grok16 C path validates toolchain for embedded .c in future L2 splits."),
    ("architecture.html#unified-driver", "libexec/grok16/", "Backend dir", "g16-cc and g16-cxx live here after relocate. Marker .relocated prevents double-move on reinstall."),
]

CXX_ROWS = [
    ("reference.html#unified-g16", "g16", "Unified driver (C++)", "Same bin/g16 as C. Auto-selects g16-cxx for .cpp/.cxx/.cc, -std=gnu++26, -x c++, -lstdc++, or argv[0] g++16 symlink. One command for the whole toolchain."),
    ("reference.html#unified-g16", "g++16", "Compat symlink", "Symlink to g16. Preserves legacy scripts and muscle memory. Detection uses basename g++16 → C++ mode immediately."),
    ("architecture.html#unified-driver", "g16-cxx", "C++ backend", "Relocated GCC g++ driver. Handles libstdc++, crtbegin/crtend, template parsing, gnu++26. Unified g16 execv() here in C++ mode."),
    ("field-primer.html#standard", "g16 -std=gnu++26", "Default C++ standard", "G16_CXX_STD=gnu++26. World_Redata field_g16.hh requires __cplusplus >= 202400. Pass explicitly when mixing with older TUs."),
    ("getting-started.html#verify", "verify (C++ leg)", "C++ smoke", "verify.cpp compiled with g16 -std=gnu++26. Checks __cplusplus >= 202400. Optional CMake minimal-cmake-project links via same g16 binary."),
    ("profiles.html#flags-cxx", "PROFILE cxx", "C++ compile flags", "Full profile: -std=gnu++26 -O3 -march=native, entropy/Field macros, vectorize, fast-math per profile."),
    ("profiles.html#flags-link", "PROFILE link", "C++ link flags", "LTO thin/full from grok16_lto probe, OpenMP for field_compute. Normalized by grok16-profile-flags.py."),
    ("profiles.html#flags-source", "PROFILE source", "Bench source path", "Returns examples/*/bench .cpp for the profile. Used by _bench_run_one and PGO training."),
    ("profiles.html#flags-defs", "PROFILE defs", "-D macros only", "Profile definition flags without optimization bundle — useful for CMake INTERFACE targets."),
    ("performance.html#pgo", "PROFILE cxx_pgo_gen", "PGO generate", "-fprofile-generate to data/pgo/. Run via grok16-toolchain.sh profile."),
    ("performance.html#pgo", "PROFILE cxx_pgo_use", "PGO use", "-fprofile-use after training. Enable G16_ENABLE_PGO=1 on field-bench for ~few-% win."),
    ("profiles.html#field-opt", "field_opt", "Primary profile", "FieldX86 + entropy + NEXUS. Bench: field-nexus-bench ~2.1ms kernel vs -O2 2.65ms (~19%)."),
    ("profiles.html#ai", "ai", "Matrix profile", "NEXUS matrix scoring. Bench wall_ms ~4.0. -flto=thin link."),
    ("profiles.html#field-compute", "field_compute", "CANVAS profile", "OpenMP SIMD dispatch kernels. field-canvas-kernel bench."),
    ("profiles.html#vulkan-rtx", "vulkan_rtx", "RTX SIMD profile", "AVX2/FMA CPU prep. Shares field-nexus-bench source."),
    ("performance.html#field-bench", "field-bench", "Primary benchmark", "G16_FIELD_SPEED=1 → field_opt. Writes data/bench/latest_*.json."),
    ("performance.html#bench-all", "bench-all", "All profiles", "Runs field_opt, ai, field_compute, vulkan_rtx sequentially."),
    ("profiles.html#mandate", "g16_field_mandate", "CMake security", "fortify, stack protector, RELRO, PIE on field targets. Required for World_Redata L2."),
    ("reference.html#env-force-cxx", "G16_FORCE_CXX=1", "Force C++ backend", "Skip detection — always g16-cxx. Useful when linking C++ objects with ambiguous argv."),
    ("integration.html#gates", "redata.cli parity", "Parity gate", "Python ↔ C++ WRDT bytes. Requires real g16 @ 16.1.1 dumpversion in manifest."),
]

HUB_BODY = f"""
  <h1>Master Coder Index</h1>
  <p>Grok16 @ <strong>{VER}</strong> — unified <code>g16</code> driver auto-detects C vs C++. Pick a language index for every command with full detail columns.</p>

  <h2>Language indexes</h2>
  <table class="idx idx-rich">
    <tr><th>Index</th><th>Scope</th><th>Detail</th></tr>
    <tr><td><a href="master-coder-c.html"><strong>Master Coder C</strong></a></td><td class="tip">C / gnu17 / g16-cc</td><td class="idx-detail">Every C-facing command, flag mode, env var, and backend path. Unified g16 dispatches to g16-cc for .c sources and -std=gnu17. No separate C driver name.</td></tr>
    <tr><td><a href="master-coder-cxx.html"><strong>Master Coder C++</strong></a></td><td class="tip">C++ / gnu++26 / g16-cxx</td><td class="idx-detail">Every C++ command, profile, benchmark, and macro path. Same g16 binary; .cpp and g++16 symlink select g16-cxx. Profiles, PGO, Field-Opt, World_Redata gates.</td></tr>
    <tr><td><a href="concepts.html"><strong>C/C++ Concepts</strong></a></td><td class="tip">Textbook visuals</td><td class="idx-detail">Pointers, arrays, sorting, memory, templates, RAII, move — SVG diagrams and short examples. Press Ctrl+K to jump here from search.</td></tr>
  </table>

  <h2>Unified driver (16.1.1)</h2>
  <p>One binary: <code>$G16_PREFIX/bin/g16</code>. Backends: <code>libexec/grok16/g16-cc</code>, <code>libexec/grok16/g16-cxx</code>. <code>g++16</code> → symlink to <code>g16</code>. CMake sets both CMAKE_C_COMPILER and CMAKE_CXX_COMPILER to g16.</p>

  <h2>1 — Toolchain commands</h2>
"""

# Append shortened original sections - read from existing master-coder and adapt
TOOLCHAIN = [
    ("getting-started.html#bootstrap", "bootstrap", "First-time build", "Fetch GCC 15, patch BASE-VER 16.1.1, host compile, install prefix, relocate backends, install unified g16, write manifest."),
    ("getting-started.html#rebuild", "rebuild", "Self-host", "Incremental (G16_FAST_REBUILD=1) or full bootstrap. Uses libexec backends as CC/CXX for GCC build. Stamp SELFHOST.json."),
    ("reference.html#cmd-install", "install", "Metadata", "VERSION, grok16-toolchain.cmake, grok16-toolchain.json. Requires g16 -dumpversion 16.1.1."),
    ("getting-started.html#verify", "verify", "Smoke tests", "C verify.c + C++ verify.cpp via unified g16; optional CMake example."),
    ("reference.html#cmd-status", "status", "Ready probe", "Exit 0 when g16 is real ELF and dumpversion matches."),
    ("performance.html#field-bench", "field-bench", "Field-Opt bench", "field-nexus-bench with G16_FIELD_SPEED. Primary perf gate."),
    ("performance.html#bench", "bench", "Single profile", "G16_BENCH_PROFILE selects profile. Uses g16 on .cpp sources."),
    ("performance.html#bench-all", "bench-all", "All profiles", "Four profiles → data/bench/latest.json."),
    ("performance.html#pgo", "profile", "PGO train", "Generates data/pgo via cxx_pgo_gen workload."),
    ("reference.html#cmd-paths", "paths", "Env dump", "All GROK16_* and G16_* paths."),
    ("integration.html#queen", "consolidate", "Queen migrate", "Vendor gcc symlink into Grok16."),
]

hub = page("Master Coder Index", HUB_BODY + table(TOOLCHAIN) + "\n")

c_page = page("Master Coder C", f"""
  <h1>Master Coder — C</h1>
  <p>Every C command and flag for Grok16 @ {VER}. Use <code>g16</code> only — it detects <code>.c</code> / <code>-std=gnu17</code> and runs <code>g16-cc</code>.</p>
  <h2>C commands &amp; driver</h2>
""" + table(C_ROWS))

cxx_page = page("Master Coder C++", f"""
  <h1>Master Coder — C++</h1>
  <p>Every C++ command and flag for Grok16 @ {VER}. Use <code>g16</code> (or <code>g++16</code> symlink) — auto-detects C++ and runs <code>g16-cxx</code>.</p>
  <h2>C++ commands &amp; driver</h2>
""" + table(CXX_ROWS))

(ROOT / "master-coder.html").write_text(hub, encoding="utf-8")
(ROOT / "master-coder-c.html").write_text(c_page, encoding="utf-8")
(ROOT / "master-coder-cxx.html").write_text(cxx_page, encoding="utf-8")
print("wrote master-coder*.html")
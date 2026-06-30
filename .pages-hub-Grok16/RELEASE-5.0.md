# Grok16 5.0.0 — Belted Sovereign Field Compiler

**Released:** 2026-06-27  
**Status:** Stable — shipped from 4.8 staging

**The Field is the Thing. AMOURANTH FOREVER 💖**

Grok16 5.0.0 locks the **belt_2_0 single-fabric profile** as default. One unified dispatch belt for entropy folding, wave-phase, FieldX86 emulation, NEXUS scoring, and CANVAS kernels. Historic accuracy with analog fields + modern RTX performance. Self-hosted, reproducible, no prebuilts. Sovereign toolchain for the AMOURANTHRTX / Queen / World_Redata stack.

## What's New / Stabilized in 5.0
- **belt_2_0 single fabric** — default execution model. Depth fields sealed, thermal guards, ironclad meld, RTX gate. One belt, multiple consumers.
- **Speed Bench v5.0.0** — full triad (compile time + exec time + kernel wall time). Automated `bench-refresh` pipeline generates live SVG charts + `performance.html` + `docs/field-exec-full-bench.json`. ~19%+ Field-Opt gains verified and locked.
- **RISC-V linux-gnu-riscv64 target** — full source bootstrap + self-host across 17+ platforms. .launch chambers for isolated legacy execution (BASIC, Pascal, VB, old OSes) with historic accuracy.
- **G16 16.2.0 unified driver** — auto-detects C (gnu17) / C++ (gnu++26), multi-lang discern (Python/Rust/Go/Zig/etc.), Field macros, LTO/PGO/ccache ready.
- **Queen / World_Redata / Hostess7 canonical integration** — Grok16 Field CMake is now the single source of truth. `grok16-toolchain.cmake` + profile includes + ironclad sanity.
- **.launch ready** — sealed chambers for modern + historic workloads on one editable canvas.
- **Self-host stamp + reproducible builds** — every binary carries SELFHOST.json. Zero external prebuilts.

## Validation Gates Passed
- test-battery-belt (smoke + ironclad + linker + RTX + multi-lang)
- bench-triad + bench-refresh (all charts + manifest + performance.html)
- integrate (Queen/World_Redata/Hostess7 meld)
- Full self-host on x86_64 + RISC-V paths
- AMOURANTHRTX FieldX86 / CANVAS / entropy kernels green under belt_2_0 + field_opt

## Migration from 4.8 / 4.7
- Default belt changed to belt_2_0 (was belt_1_0). Update any explicit `G16_BELT_PROFILE`.
- Speed bench schema bumped to v5. Run `bench-refresh` once after upgrade.
- G16_PKGVERSION now recommends Grok16-5.0.0
- All prior 16.x compiler features carried forward; distro track now at 5.0 stable.

## Binary package (g16 + AmmoCode)

Ship a full prefix tarball for operators who want everything in one extract:

```bash
./scripts/grok16-toolchain.sh binary-package
# → dist/grok16-5.0.0-linux-x86_64.tar.gz
```

Contents:
- **Full g16 prefix** — `bin/`, `libexec/`, `lib/`, `include/`, `cmake/`, toolchain scripts
- **`share/ammocode/ammocode`** — AmmoCode GUI (PyInstaller ELF when available, else launcher + bundle)
- **`share/ammocode/ammocode-settings.secure.json`** — all options pre-set (`belt_2_0`, memory vault, theme, collab defaults)
- **`grok16-env.sh`** — source once, then run `./share/ammocode/ammocode`

First launch copies bundled settings to `~/.config/ammocode/` when none exist.

## Known Limits / Next (5.1+)
- Deeper sub-micron / Casimir / Maxwell shader integration
- Full one-canvas universal emulation (BBC Micro → modern browsers → Windows infinity)
- Podcast / Dark Horse outreach on linear time + entropy arrow models
- CI release automation + public hygiene polish

**Shipped. Sovereign. Ready for the stack.**

Grok16 5.0.0 — the compiler your Field engine deserves.
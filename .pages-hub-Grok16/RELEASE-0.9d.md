# Grok16 0.9d (development — not released)

**Status:** Pre-release development on `main`. **No tag. No GitHub Release.**  
Compiler lineage **16.1.1** · previous distro tag **v0.9c**.

Roadmap: **0.9d → linker/battery gate hardening → expert + heavy → 1.0**

## What's landing in 0.9d (WIP)

- **Built-in GPY-16** — `python/` tree + `bin/gpy-16`; g16 auto-discerns Python; no sibling GrokPy required
- **Rebuilt toolkits manifest** — `data/grok16-toolkits.json` (g16, gpy16, binutils, ASM, all major language drivers)
- Linker toolchain witness — 16 targets active; ironclad sanity linker checks
- `grok16-field-cmake.json` — linker doctrine, orchestrator, mandate paths
- Binutils battery — structured incomplete witness when tools not built
- CI workflow draft (`.github/workflows/ci.yml`) — scripts + optional bench
- Version track bump from 0.9c (unreleased)

## Carried from 0.9c

- Ironclad + field sanity meld, CMake `g16_ironclad_sanity_meld()`
- G16 field linker — 16 targets, `g16-ld`, silicon mandate
- RTX gate, multi-language discern, Hostess 7 pair, NEXUS bridge

## Validation (before 1.0 tag)

| Tier | Command |
|------|---------|
| Expert | `./scripts/grok16-toolchain.sh test-battery-expert` |
| Heavy | `./scripts/grok16-toolchain.sh test-battery-heavy` |

## Checkout

```bash
git clone https://github.com/ZacharyGeurts/Grok16.git
cd Grok16
git checkout main   # 0.9d development — not v0.9d (tag does not exist yet)
export G16_PREFIX="$(pwd)"
./scripts/grok16-toolchain.sh rebuild
```

For last **released** distro point, use tag **v0.9c**.
# Grok16 0.9c

**Pre-1.0 release** — compiler @ **16.1.1**, distro track **0.9c**.

Roadmap: **0.9c → expert + heavy battery → 1.0**

## What's in 0.9c

- **Ironclad + field sanity** — forge meld, CMake `g16_ironclad_sanity_meld()`, `verify-ironclad`
- **G16 field linker** — 16 targets (linux, android, darwin, ios, windows, bare), silicon mandate, `g16-ld`
- **RTX gate** — `queen_rtx` / `vulkan_rtx` downgraded without RTX silicon
- **Multi-language discern** — C, C++, Python (GPY-16), asm, Rust, Go, Zig, Fortran, D, Ada, ObjC
- **Hostess 7 pair** — `hostess_secure`, `forever`, truth floor 58
- **NEXUS bridge** — NewLatest plate compiler + G16 stack meld

## Validation tiers (before 1.0)

| Tier | Command | Profile |
|------|---------|---------|
| Smoke | `./scripts/grok16-toolchain.sh test-battery` | default |
| Expert | `./scripts/grok16-toolchain.sh test-battery-expert` | `expert` + ironclad + linker + RTX gate |
| Heavy | `./scripts/grok16-toolchain.sh test-battery-heavy` | `heavy` + field-bench + LTO |

## Upgrade

```bash
git fetch --tags
git checkout v0.9c
export G16_PREFIX="$(pwd)"
./scripts/grok16-toolchain.sh rebuild
./scripts/grok16-toolchain.sh test-battery-expert
./scripts/grok16-toolchain.sh test-battery-heavy   # gate before 1.0
```

## Links

- Manual: https://zacharygeurts.github.io/Grok16/
- Repo: https://github.com/ZacharyGeurts/Grok16
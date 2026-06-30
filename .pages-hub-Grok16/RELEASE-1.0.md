# Grok16 1.0.0

**First stable release** — compiler @ **16.1.1**, distro track **1.0.0**.  
Tag: **v1.0.0** · previous tagged distro: **v0.9c**

## What's in 1.0

- **Unified `g16` driver** — C (`gnu17`), C++ (`gnu++26`), Python/GPY-16, ASM, Rust, Go, Zig, Fortran, D, Ada, ObjC
- **Built-in toolkits** — `data/grok16-toolkits.json`; GPY-16 in `python/`; binutils field tools (`g16-as`, `g16-ld`, …)
- **G16 field linker** — 16 silicon targets, Ironclad/sanity witness, mandate flags (RELRO, BIND_NOW, NX stack, PIE for executables only)
- **Battery gate hardening** — expert + heavy tiers, `test-battery-release` (heavy + python + forever + binutils + verify)
- **Profile/LTO/PGO fixes** — `-flto=thin` normalization, conditional PGO use, expert/heavy `-fPIE` / `-Wl,-z,noexecstack`
- **Linker fix (1.0)** — `-pie` no longer injected on `-shared` links (prevents `libgcc_s.so.1` corruption during rebuild)
- **Ironclad + field sanity** — forge meld, CMake mandate, hostess gate (score 21/21)
- **RTX gate** — `queen_rtx` / `vulkan_rtx` require RTX silicon

## Validation (release gate)

| Tier | Command |
|------|---------|
| Smoke | `./scripts/grok16-toolchain.sh test-battery` |
| Expert | `./scripts/grok16-toolchain.sh test-battery-expert` |
| Heavy | `./scripts/grok16-toolchain.sh test-battery-heavy` |
| **Release** | `./scripts/grok16-toolchain.sh test-battery-release` |

Production rebuild:

```bash
git fetch --tags
git checkout v1.0.0
export G16_PREFIX="$(pwd)"
export G16_RELEASE_PROFILE=1
./scripts/grok16-toolchain.sh rebuild
./scripts/grok16-toolchain.sh test-battery-release
```

## Upgrade from v0.9c

1. Checkout `v1.0.0`
2. `G16_RELEASE_PROFILE=1 ./scripts/grok16-toolchain.sh rebuild`
3. Run `test-battery-release` — must pass before deploying prefix to consumers (Queen, World_Redata, Field CMake)

## Links

- Manual: https://zacharygeurts.github.io/Grok16/
- Repo: https://github.com/ZacharyGeurts/Grok16
- Wiki: https://github.com/ZacharyGeurts/Grok16/wiki
# Grok16 5.0.1 — AmmoOS Incorporation

**Released:** 2026-06-29  
**Pairs with:** [AmmoOS 1.9.9h — Grok Expert Review](https://github.com/ZacharyGeurts/AmmoOS/releases/tag/v1.9.9h)

Grok16 5.0.1 closes the incorporation loop the 5.0.0 foundation opened. AmmoOS is no longer a reference in release notes — it has a profile, integration hooks, verification gate, and documentation path in the toolchain.

## What changed

- **`ammoos` profile** — `cmake/grok16-profile-ammoos.cmake` with `field_physics` variant for entropy-sensitive desktop code
- **Integration wiring** — `grok16-integrate.sh` detects SG/NewLatest, stamps Queen doctrine, publishes `data/grok16-ammoos-integrate.json`
- **Toolchain targets** — `integrate-ammoos`, `verify-ammoos-surfaces` on `grok16-toolchain.sh`
- **Smoke chamber** — `examples/ammoos-smoke/` with portable `.launch`
- **Review document** — `docs/AMMOOS-REVIEW-FOR-GROK-BUILD.md` (business tone, actionable gaps closed where this release could)
- **Docs + wiki + Pages** — integration, field platform, ZNetwork connect; manual rebuilt for 5.0.1

## Unchanged from 5.0.0

- **belt_2_0** single fabric default
- **g16 @ 16.2.0** unified driver
- **Speed Bench v5** — same suite and gates
- **Binary package** — `grok16-5.0.1-linux-x86_64.tar.gz` when built locally
- **2D field platform** — no standalone field files

## Validation

```bash
./scripts/grok16-toolchain.sh verify
./scripts/grok16-toolchain.sh integrate-ammoos
./scripts/grok16-toolchain.sh verify-ammoos-surfaces
./scripts/grok16-toolchain.sh test-battery-belt
```

## Install

```bash
git clone https://github.com/ZacharyGeurts/Grok16.git
cd Grok16 && git checkout v5.0.1
export G16_PREFIX="$(pwd)" G16_BELT_PROFILE=belt_2_0 SG_ROOT=/path/to/SG
./scripts/grok16-toolchain.sh rebuild
./scripts/grok16-toolchain.sh integrate-ammoos
```

## Manual

- **Web:** https://zacharygeurts.github.io/Grok16/
- **Wiki:** https://github.com/ZacharyGeurts/Grok16/wiki

Thank you for running sovereign tooling on your own metal. Ship clean, verify twice, integrate once.
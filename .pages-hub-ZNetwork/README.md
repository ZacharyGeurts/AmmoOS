# ZNetwork 2.1.0 — Stack

![Release](https://img.shields.io/badge/release-2.1.0-green)
![Stack](https://img.shields.io/badge/canonical-NewLatest-blue)
![Grok16](https://img.shields.io/badge/Grok16-5.0.1-gold)
![AmmoOS](https://img.shields.io/badge/AmmoOS-2.0.0--beta3-purple)

**ZNetwork** is the smart relayer — sole internet in/out for the AmmoOS field stack.

**Stack nav:** [AmmoOS STACK-NAV](https://github.com/ZacharyGeurts/AmmoOS/blob/main/STACK-NAV.md) · [Profile hub](https://zacharygeurts.github.io/ZacharyGeurts/stack.html) · [Queen](https://github.com/ZacharyGeurts/Queen) · [KILROY](https://github.com/ZacharyGeurts/KILROY)

## Stack layer

| Layer | Role |
|-------|------|
| Hardware | Witness — no breaks |
| NEXUS C2 | Command `:9477` |
| **ZNetwork** | 100% loopback pipe — relayer + exploit shield |
| Queen | Secured browser shell |
| AmmoOS | Field desktop inside Queen |

When ZNetwork is running, the operator is **`127.0.0.1`**.

## Quick start

```bash
git clone https://github.com/ZacharyGeurts/ZNetwork.git
cd ZNetwork && git checkout v2.1.0
./scripts/znetwork-build-host.sh
./scripts/znetwork-test-battery.sh
./build/znetwork status --json
```

Integrated with NewLatest:

```bash
cd NewLatest
./scripts/integrate-znetwork.sh
```

## Platforms

Grok16-aligned matrix — see `data/znetwork-platform-release.json` and release `znetwork-2.1.0-PLATFORMS.md`.

- **Linux** — full native + cross ELF (x86_64, i386, aarch64, arm, riscv64)
- **Windows** — PE build via mingw (connection snapshot + native backend)
- **macOS** — mach-o backend sources included; host clang build
- **Android** — NDK bootstrap documented

## Lab gates

```bash
./scripts/znetwork-test-battery.sh
./scripts/znetwork-lab-gate.sh
```

Without `ZNETWORK_LAB_GATE_OK=1`, SHADOW downgrades to REVIEW_ONLY.

## Design

See `DESIGN.md` · Field wire: Grok16 `grok16-znetwork-field-wire-doctrine.json`
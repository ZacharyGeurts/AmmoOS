# AmmoOS

![Release](https://img.shields.io/badge/release-1.0.0--beta-brightgreen)
![Edition](https://img.shields.io/badge/edition-field%20OS-blue)
![G16](https://img.shields.io/badge/Grok16-4.7.0-gold)
![Queen](https://img.shields.io/badge/Queen-browser-purple)
![License](https://img.shields.io/badge/license-GPLv3-green)

**AmmoOS** is the **field operating system beta** built from the SG/NewLatest engine — every component either **launches as a native program** or **opens in your web browser** on loopback. Combinatronic rebalance wires chips, languages, and plates before boot.

## Live surfaces (after install)

| Surface | URL | Kind |
|---------|-----|------|
| **Host desktop** | http://127.0.0.1:9477/field | Browser — first page |
| **Field command** | http://127.0.0.1:9477/command | Browser — full C2 |
| **Queen Browser** | http://127.0.0.1:9481/world/browser.html | Browser — OS in Start tab |
| **Underlay F9** | http://127.0.0.1:9477/underlay-f9?sector=underlay | Browser — Tristate installer |
| **Training** | http://127.0.0.1:9477/command#training | Browser — Hostess7 tab |
| **Queen shell** | `Queen/build/rtx/bin/Linux/queen-browser` | Native — RTX program |
| **Dev launcher** | `./nexus.sh` | Native — panel + browser |

## Quick install (Linux x86_64)

```bash
git clone https://github.com/ZacharyGeurts/AmmoOS.git
cd AmmoOS
sudo ./install-all.sh
```

Browser opens **http://127.0.0.1:9477/field** on start.

## Beta pipeline (from dev tree)

```bash
export SG_ROOT=/path/to/SG
./scripts/ammoos-beta-pipeline.sh    # combinatronic · plate · engine · integrate
./scripts/ammoos-launch-verify.sh     # every surface registered
./scripts/pack-ammoos-release.sh      # source + installers + platforms
```

## Combinatronic integration

AmmoOS runs the full **g16 combinatronic optimal** cycle before release:

- **Rebalance** — chip + program batteries, universal leaf ordering
- **Condense** — plate width × length consolidation
- **Combine** — universal panel + combinatorics publish
- **Connect** — chip ISA ↔ language driver edges
- **Spider wire** — ironclad outward lane optimization

Doctrine: `lib/g16-combinatronic-rebalance.py` · State: `.nexus-state/ammoos-*.json`

## Platform matrix

AmmoOS beta ships **source bootstrap** for:

| Platform | Installer |
|----------|-----------|
| Linux x86_64 | `install-all.sh` |
| Linux aarch64 / arm / riscv64 / i386 | `install-all.sh` on target |
| Windows x86_64 | `stealth.ps1` or WSL2 + `install-all.sh` |
| macOS (Intel / Apple Silicon) | `./nexus.sh` dev tree |
| FreeBSD amd64 | `install.sh` |
| Android aarch64 | Queen `browser.html` WebView shell |

Full matrix: [ammoos-1.0.0-beta-PLATFORMS.md](dist/ammoos-1.0.0-beta-PLATFORMS.md) · JSON: `data/ammoos-platform-release.json`

## Architecture

```
Host browser (:9477)
  ├─ /field        → host desktop (apps + startbar)
  ├─ /command      → threat panel + training
  └─ /underlay-f9  → Tristate installer

Queen Browser (:9481)
  └─ /world/browser.html → field OS inside Start tab

Native programs
  ├─ queen-browser     → RTX shell (FIELDC / AmmoOS guest)
  ├─ nexus.sh          → dev launcher
  └─ install-all.sh    → production deploy

Combinatronic engine
  ├─ g16-combinatronic-rebalance.py
  ├─ field-program-combinatronic.py
  └─ Queen/AmmoOS/net/*.fld plates
```

## Manual

| Doc | URL |
|-----|-----|
| **Web manual** | https://zacharygeurts.github.io/AmmoOS/ |
| Getting Started | https://zacharygeurts.github.io/AmmoOS/getting-started.html |
| Launch surfaces | https://zacharygeurts.github.io/AmmoOS/launch-surfaces.html |
| Combinatronic | https://zacharygeurts.github.io/AmmoOS/combinatronic.html |
| Platforms | https://zacharygeurts.github.io/AmmoOS/platforms.html |
| Field I/O | https://zacharygeurts.github.io/AmmoOS/io.html |

## Lineage

AmmoOS beta **1.0.0-beta** packages **NEXUS-Shield / NewLatest 10.4.1** with Grok16 **4.7.0** pairing. NEXUS-Shield remains the upstream operator tree; AmmoOS is the product-facing field OS release.

**Release notes:** [RELEASE-1.0.0-beta.md](RELEASE-1.0.0-beta.md)
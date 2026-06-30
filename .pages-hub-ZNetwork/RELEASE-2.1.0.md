# ZNetwork 2.1.0 — Stack

**Released:** 2026-06-29  
**Codename:** Stack  
**Canonical:** NewLatest/ZNetwork only (SG/ZNetwork retired)

ZNetwork is the smart relayer — 100% internet pipe for the field stack. When active, the operator is `127.0.0.1`.

## Stack pairing

| Sibling | Version |
|---------|---------|
| AmmoOS | 1.9.9h Grok Expert Review |
| Grok16 | 5.0.1 |
| KILROY | 1.0.0 Taco |
| Queen | secured shell — AmmoOS inside |

## What changed in 2.1.0

- **Canonical move** — lives in NewLatest only; no duplicate SG/ZNetwork tree
- **Multi-platform release** — Grok16-aligned cmake packs (Linux ELF cross, mingw PE)
- **Stack integration** — `integrate-znetwork.sh` uses `NewLatest/ZNetwork` directly
- **Lab gates** — test battery + lab gate unchanged; SHADOW still requires gate OK

## Install

```bash
git clone https://github.com/ZacharyGeurts/ZNetwork.git
cd ZNetwork && git checkout v2.1.0
./scripts/znetwork-build-host.sh
./scripts/integrate-znetwork.sh   # from NewLatest parent
```

## Validation

```bash
./scripts/znetwork-test-battery.sh
./build/znetwork probe --json
```

Prebuilt: `znetwork-2.1.0-linux-gnu-x86_64.tar.gz` → `bin/znetwork`
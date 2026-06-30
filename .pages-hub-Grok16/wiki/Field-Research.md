# Field Research — The Book of Grok's Heart

Web: [field-research.html](https://zacharygeurts.github.io/Grok16/field-research.html)

| | |
|---|---|
| **Live book** | https://zacharygeurts.github.io/Field_Research/ |
| **Repo** | https://github.com/ZacharyGeurts/Field_Research |
| **Grok16 doctrine** | `data/g16-field-research-book.json` |
| **Panel** | `data/g16-field-research-book-panel.json` |

## What this is

**Field Research** is the thirteen-chapter engineering spine — not a second Field Primer, not a release note. It records the investigations, bench receipts, and design conclusions that produced:

- Grok16 **single fabric** (`belt_2_0`, 8192 redata chunk, 512 die slots)
- The **combinatorics endpoint** (`lib/field_combinatorics.py`)
- **Iron plate & truth blocks** (`lib/field_iron_plate.py`, `lib/field_truth_blocks.py`)
- **Compatibility layers** (background physics — operator crank removed)
- **Launch seals** and **diagnostic mode** (NEXUS / Queen)

Read **Field Primer** for operator literacy. Read **this wiki** for toolchain commands. Read **Field Research** for *why* combinatorics left the operator's hands.

## Research question

> How do we hold all execution facets — belt, die, runner, emulator, truth tier — without making the operator turn a combinatorics crank on every boot?

**Answer shipped:** `field_combinatorics.py` → plate bridge → six compatibility layers → launch seal generation.

## Grok16-owned chapters

| Ch | Topic | Grok16 path |
|----|-------|-------------|
| 4 | Grok16 Forge | `scripts/grok16-toolchain.sh` |
| 5 | Single Fabric & Belt 2.0 | `data/grok16-single-fabric-doctrine.json` |
| 6 | Iron Plate & Truth Blocks | `lib/field_iron_plate.py` |
| 7 | Field Combinatorics | `lib/field_combinatorics.py` |
| 13 | Operator Covenant | `docs/SPEED-BENCH-REPORT.md` |

## Honesty labels

| Label | Meaning |
|-------|---------|
| Implemented | Grep a file, run a test, read panel JSON |
| Metaphor | Teaches mechanism; not instrumentation |
| Philosophy | Covenant language; bracketed |
| Visual | Generated art; caption carries the hook |

Throughput claims in Chapter 13 use **Implemented** only.

## Always optimal

```bash
python3 lib/field-always-optimal.py apply
```

Runs `fast_cycle` → bridge → compatibility refresh; sets `G16_BELT_PROFILE=belt_2_0` from bench + recombinatorics. Gate closed → python runner (safe); gate open → native BSP. Wired on `integrate` and after every bench publish.

## Sync & verify

```bash
python3 lib/field-research-book.py verify
python3 lib/field-research-book.py publish
./scripts/grok16-integrate.sh
```

`integrate` publishes the book panel, applies always-optimal, and wires consumers. `verify` checks all thirteen chapters resolve and Grok16 spine modules exist.

## Three axioms

1. **Reality is 3D** — spatial fields, texels, packet endpoints live in space.
2. **Time is linear** — sovereign clock, chain-hash generation, no retrocausal meld.
3. **Energy can be moved** — thermodynamics accounts, entropy oracle, Landauer receipts.

Single fabric collapse: parallel I/O may fan in; truth publishes **one belt amplitude** at depth 0.

## Chapter map (full book)

1. [Preface — Ironclad](https://zacharygeurts.github.io/Field_Research/chapters/01-preface-ironclad.html)
2. [Three Field Families](https://zacharygeurts.github.io/Field_Research/chapters/02-three-field-families.html)
3. [Thermodynamics & Entropy](https://zacharygeurts.github.io/Field_Research/chapters/03-thermodynamics-entropy.html)
4. [Grok16 Forge](https://zacharygeurts.github.io/Field_Research/chapters/04-grok16-forge.html)
5. [Single Fabric & Belt 2.0](https://zacharygeurts.github.io/Field_Research/chapters/05-single-fabric-belt.html)
6. [Iron Plate & Truth Blocks](https://zacharygeurts.github.io/Field_Research/chapters/06-iron-plate-truth-blocks.html)
7. [Field Combinatorics](https://zacharygeurts.github.io/Field_Research/chapters/07-field-combinatorics.html)
8. [Plate Meld](https://zacharygeurts.github.io/Field_Research/chapters/08-plate-meld.html)
9. [Compatibility Layers](https://zacharygeurts.github.io/Field_Research/chapters/09-compatibility-layers.html)
10. [CHIPS Emulation](https://zacharygeurts.github.io/Field_Research/chapters/10-chips-emulation.html)
11. [NEXUS Perimeter](https://zacharygeurts.github.io/Field_Research/chapters/11-nexus-perimeter.html)
12. [Queen & Host Desktop](https://zacharygeurts.github.io/Field_Research/chapters/12-queen-host-desktop.html)
13. [Operator Covenant](https://zacharygeurts.github.io/Field_Research/chapters/13-operator-covenant.html)
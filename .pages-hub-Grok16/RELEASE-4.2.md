# Grok16 4.2.0

**Tag:** `v4.2.0` · **Compiler:** `g16 @ 16.2.0` · **Previous:** `v4.0.0` · **Platforms:** 17 (incl. RISC-V)

## .launch chambers (ready)

Portable `queen-launch/v1` manifests ship in every `examples/*/` folder. `chamber_root` uses `${GROK16_ROOT}/examples/<name>` — relocatable across clones.

```bash
export GROK16_ROOT=/path/to/Grok16 SG_ROOT=/path/to/SG
./scripts/grok16-launch-verify.sh
python3 NewLatest/Queen/lib/queen-launch-chamber.py run examples/speed-demo/speed-demo.launch
```

## Multi-platform release

Source bootstrap per platform — see `data/grok16-platform-release.json` and release asset `grok16-4.2.0-PLATFORMS.md`.

| Family | Targets |
|--------|---------|
| Linux GNU | x86_64, i386, aarch64, arm, **riscv64** |
| Android NDK | aarch64, arm, x86_64 |
| Darwin / iOS | x86_64, aarch64 (iOS) |
| Windows PE | x86_64, aarch64 |
| Bare ELF | x86_64, aarch64, **riscv64** |

```bash
./scripts/grok16-release.sh 4.2.0 --push   # gates + tarball + GitHub release
```

## Plate tech — line safety widths

Power sort plate now witnesses **chip path line safety** aligned with chip battery combinatorics:

| Field | Value |
|-------|-------|
| `narrow_band_width` | 16 |
| `pipe_policy` | `adjacent_narrow_only` |
| `wide_piping_prevented` | true |
| `chip_paths_algorithm` | `narrow_band` |

Doctrine: `data/g16-power-sort-doctrine.json` · Plate: `lib/g16-power-sort-plate.py` · Consumer: `NewLatest/lib/field-chip-battery.py`

## What's new

- **CPU Library** — 271-entry catalog (ARM, Apple, mobile, Intel, AMD, chip-battery dies) with schematic text and Queen World UI
- **FFNT / Amouranth Bold** — SDF atlas + secured clipboard font editor
- **Clipboard ghost wire** — historic ring + `clipboard_master` scheme; no visible manager app
- **Line safety plate fields** — `line_safety` on power sort selection + `chip_paths` section metadata
- **Test gate** — `scripts/grok16-test-gate.sh` with per-step timeouts (no hang)

## Test gate (monitored)

```bash
export SG_ROOT=/path/to/SG
./scripts/grok16-test-gate.sh smoke    # ~1 min — default CI gate
./scripts/grok16-test-gate.sh full     # adds release battery + research book
```

## Gates

1. `grok16-test-gate.sh smoke` green
2. Power sort plate cycle emits `line_safety.narrow_band_width: 16`
3. Chip battery `path_total_pct: 100` + `wide_piping_prevented: true`
4. CPU library verify ≥ 80 entries
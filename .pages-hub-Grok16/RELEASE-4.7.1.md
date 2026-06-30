# Grok16 4.7.1

**Tag:** `v4.7.1` · **Compiler:** `g16 @ 16.2.0` · **Previous:** `v4.7.0` · **Platforms:** 17 (incl. RISC-V)

## Patch (2026-06-27)

- **AmmoOS pairing** — NewLatest/AmmoOS beta aligned on Grok16 `4.7.1`
- **Bench refresh** — triad, compare, bench-all, exec-comprehensive, SVG charts
- **Docs + wiki** — GitHub Pages manual and wiki synced to `4.7.1`
- **TDIR / field stack** — AmmoOS restart env (`TDIR`, `NEXUS_ZNETWORK=0`, boot-impl fast path)

```bash
./scripts/grok16-toolchain.sh bench-refresh
./scripts/grok16-release.sh 4.7.1 --push
```

See [RELEASE-4.7.md](RELEASE-4.7.md) for the 4.7 feature set.

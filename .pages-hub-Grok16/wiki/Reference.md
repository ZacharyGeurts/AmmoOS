# Reference

Web: [reference.html](https://zacharygeurts.github.io/Grok16/reference.html)

## grok16-toolchain.sh

| Command | Description |
|---------|-------------|
| bootstrap | First build |
| rebuild | Self-host |
| verify | C/C++ + linker + ironclad |
| test-battery | Smoke tier |
| test-battery-expert | Expert tier |
| test-battery-heavy | Heavy tier |
| test-battery-release | **1.0 release gate** |
| field-bench | Field-Opt bench |
| bench-all | All profiles |
| profile | PGO generate |
| paths | Print env |
| consolidate | Queen migration |

## Environment

| Variable | Default |
|----------|---------|
| GROK16_ROOT | repo root |
| G16_PREFIX | $GROK16_ROOT |
| G16_CXX_STD | gnu++26 |
| G16_FAST_REBUILD | 1 |
| G16_BENCH_PROFILE | field_opt |
| GROK16_BUILD_JOBS | nproc |

See `data/grok16-config.json` for full list.

## Files

| File | Role |
|------|------|
| data/grok16-profiles.json | Profiles |
| cmake/g16-field-mandate.cmake | Hardening |
| SELFHOST.json | Self-host stamp |
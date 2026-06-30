# Grok16 5.0 Migration

- Pin `belt_2_0` in all CMakePresets (`GROK16_FIELD_PROFILE=belt_2_0`)
- Update `G16_PKGVERSION=Grok16-5.0.0` in AMOURANTHRTX build scripts
- Run `integrate` + `bench-refresh` after upgrade
- Legacy chambers now default-sealed — test your `.launch` calls
- Set `G16_MIXED_SOURCE_GUARD=0` only if you intentionally mix `.c` and `.cpp` in one g16 invocation
- AmmoCode consumers: point embed base at `SG/AmmoCode` and `apiBase` at `/api/ammocode`
- Binary package: `./scripts/grok16-toolchain.sh binary-package` → `dist/grok16-5.0.0-linux-x86_64.tar.gz` (g16 + AmmoCode exe + default settings)
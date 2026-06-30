# Profiles

Web: [profiles.html](https://zacharygeurts.github.io/Grok16/profiles.html)

Manifest: `data/grok16-profiles.json`

## Belt profiles (2.0)

| Profile | Use |
|---------|-----|
| **`belt_2_0`** | **2.0 default** — single fabric, chunked redata 8192, wave-massive |
| `belt_1_0` | 1.0 baseline (aliases field_opt) — triad compare |
| `field_opt` | Legacy Field-Opt throughput |

```bash
export G16_BELT_PROFILE=belt_2_0
```

## Other build profiles

| Profile | Use |
|---------|-----|
| `ai` | NEXUS matrix scoring |
| `field_compute` | CANVAS wave dispatch |
| `vulkan_rtx` | RTX SIMD (requires RTX GPU) |
| `expert` | Battery expert tier |
| `heavy` | Battery heavy gate |
| `hostess_secure` | Hostess7 pair |
| `forever` | Forever battery contract |

## CMake

```bash
cmake -S examples/field-nexus-bench -B build \
  -DCMAKE_TOOLCHAIN_FILE=cmake/grok16-toolchain.cmake \
  -DCMAKE_PROJECT_INCLUDE=cmake/grok16-profile-belt-2.cmake
```

## Flag introspection

```bash
pythong scripts/grok16-profile-flags.py belt_2_0 cxx
pythong scripts/grok16-profile-flags.py belt_1_0 cxx
```
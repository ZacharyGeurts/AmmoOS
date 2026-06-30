# CMake and Linking

Web: [cmake-linking.html](https://zacharygeurts.github.io/Grok16/cmake-linking.html) · [linker.html](https://zacharygeurts.github.io/Grok16/linker.html)

## speed_demo CMake project

`examples/speed-demo/CMakeLists.txt` builds `grok16_speed_demo` from `speed_demo.cpp`.

### Host plane

```bash
cmake -S examples/speed-demo -B build/host \
  -DCMAKE_CXX_COMPILER=$(which g++) \
  -DGROK16_HOST_PLANE=ON
cmake --build build/host -j$(nproc)
```

Full-bench reference: **2,417 ms** configure+build · **85.7M ops/s** @ 3s

### G16 belt plane

```bash
cmake -S examples/speed-demo -B build/g16 \
  -DCMAKE_TOOLCHAIN_FILE=$G16_PREFIX/cmake/grok16-toolchain.cmake \
  -DGROK16_PROFILE=belt_2_0
cmake --build build/g16 -j$(nproc)
```

## Toolchain file

`cmake/grok16-toolchain.cmake` (generated at install) sets:

- `CMAKE_C_COMPILER` / `CMAKE_CXX_COMPILER` → `g16`  
- Profile flags from `data/grok16-profiles.json`  
- Linker wrapper → `g16-ld`  

## Linking mandate

| File | Role |
|------|------|
| `cmake/g16-linker-mandate.cmake` | Field link flags, `-pie`, shared rules |
| `cmake/g16-field-mandate.cmake` | `G16_FIELD_SAFETY_MANDATE_v1` on field targets |
| `forge/g16-linker.py` | `g16-ld` backend |

## Stage + compare

```bash
./scripts/field-exec-stage.py          # wave convert once
SPEED_DEMO_TARGET_SEC=3 python3 scripts/field-exec-compare.py
./scripts/grok16-toolchain.sh exec-full-bench   # compile ms + exec ops/s v3
```

Bench versions: `data/grok16-speed-bench-version.json`
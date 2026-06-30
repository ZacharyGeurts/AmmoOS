# Minimal CMake example (Grok16)

Build with the Grok16 toolchain file (after `./scripts/grok16-toolchain.sh bootstrap` or `rebuild`):

```bash
export G16_PREFIX=/path/to/Grok16   # or your install prefix
cmake -S . -B build \
  -DCMAKE_TOOLCHAIN_FILE="$G16_PREFIX/../cmake/grok16-toolchain.cmake"
cmake --build build
./build/grok16_smoke
```

From the repo root:

```bash
cmake -S examples/minimal-cmake-project -B examples/minimal-cmake-project/build \
  -DCMAKE_TOOLCHAIN_FILE=cmake/grok16-toolchain.cmake
cmake --build examples/minimal-cmake-project/build
```

Or run the bundled verify target:

```bash
./scripts/grok16-toolchain.sh verify
```
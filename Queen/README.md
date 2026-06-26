# Queen Browser — NewLatest Build Tree

**Nothing optional. Hold all gates. MP4. We want it ALL.**

Sovereign browser stack for NEXUS-Shield: full web surface, every egress gated, codecs in-tree.

## Vendor clones

| Path | Upstream | Role |
|------|----------|------|
| `vendor/ffmpeg` | [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg) | MP4/H.264/AAC decode — mandatory codec path |
| `vendor/ladybird` | [LadybirdBrowser/ladybird](https://github.com/LadybirdBrowser/ladybird) | Independent browser engine (millennium ship) |
| `vendor/servo` | [servo/servo](https://github.com/servo/servo) | Rust layout/engine track |

```bash
./clone-all.sh          # shallow clones (re-run safe)
./build.sh              # Queen shell + shaders + ffmpeg static (optional stages)
```

## Queen shell (`engine/`)

- **2026 GUI** — aqua/rose field chrome, compshader boot (`shaders/compute/QueenBoot.comp`)
- **AMOURANTHRTX RTX** — loads `QueenBoot.spv` via same FieldSocket push-constant layout as NEXUS panel
- **Plugins** — `plugins/builtin-manifest.json` (all built-in; external plugins supported)
- **NEXUS** — Truth DNS, gatekeeper, honorability via `nexus/` symlinks + env

## Build stages

```bash
# 1 — Queen browser shell (SDL3 + optional Vulkan compshader)
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)

# 2 — FFmpeg (static libs for Queen media path)
./build-ffmpeg.sh

# 3 — Ladybird (full engine — long build, needs deps)
./build-ladybird.sh

# 4 — Servo (Rust engine track)
./build-servo.sh
```

## Run — one exe, RTX goodies included

```bash
export NEXUS_INSTALL_ROOT="$(cd .. && pwd)"
./build.sh
./build/rtx/bin/Linux/queen-browser --queen --extended-field
```

No external Firefox/Chrome. UI + NEXUS panel load **inside** the RTX engine (`FieldWebPanel` + `QueenBoot.comp` compshader boot). NEXUS panel API auto-starts on `:9477` if needed.

Binary names: `queen-browser`, `fieldfox`, `field-queen` — all recognized by NEXUS gatekeeper.
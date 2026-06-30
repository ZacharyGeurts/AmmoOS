# Integration

Web: [integration.html](https://zacharygeurts.github.io/Grok16/integration.html)

Requires Grok16 **v5.1.0** with `test-battery-release` + `test-battery-belt` green.

## Auto-integrate

```bash
./scripts/grok16-integrate.sh
./scripts/grok16-toolchain.sh integrate-ammoos
./scripts/grok16-toolchain.sh verify-ammoos-surfaces
```

Publishes **Field Research book panel** (`lib/field-research-book.py publish`) and wires canonical prefix + `G16_BELT_PROFILE=belt_2_0` to:

- `NewLatest/Queen`
- `World_Redata`
- `ZOCR` / Final_Ear
- `PythonG`
- `Field_Research` (book manifest cross-ref)

Env template: `data/grok16-integrate.env`

Stack fabric (5.1): `lib/g16-stack-fabric.py` stamps G1–G15 through integrate.

## Field Research book

```bash
python3 lib/field-research-book.py verify
python3 lib/field-research-book.py publish
```

Doctrine: `data/g16-field-research-book.json` · Live: https://zacharygeurts.github.io/Field_Research/

## Safety at consumers {#gates}

Integrated SG tree enforces **single fabric** safety:

| Consumer | Depth field | Ironclad |
|----------|-------------|----------|
| Queen field-net | `depth_field_impossible` | classify strip |
| Queen browser | navigate enforce | tab URL clean |
| NEXUS panel | HTTP 302 strip | field-depth-singularizer |
| Field sanity | integral preflight | `ironclad:field_sanity:4` |

Doctrine cross-ref: `NewLatest/data/single-field-depth-doctrine.json`

## World_Redata

```bash
cd World_Redata
./build-cpp.sh
PYTHONPATH=. pythong -m redata.cli parity
PYTHONPATH=. pythong -m redata.cli security
```

## Env

```bash
export G16_PREFIX=/path/to/Grok16
export G16_BELT_PROFILE=belt_2_0
export WRDT_G16_PREFIX="$G16_PREFIX"
source data/grok16-integrate.env
```

## AmmoOS 2.0 Stack

Review: [`docs/AMMOOS-REVIEW-FOR-GROK-BUILD.md`](../docs/AMMOOS-REVIEW-FOR-GROK-BUILD.md)

- **Pair:** AmmoOS `2.0.0-beta3` on `main` (tarballs building now)
- Profile: `ammoos` in `data/grok16-profiles.json`
- CMake: `cmake/grok16-profile-ammoos.cmake` (`G16_AMMOOS_PHYSICS=1` → field_physics variant)
- Smoke chamber: `examples/ammoos-smoke/`
- Generated manifest: `data/grok16-ammoos-integrate.json`
- Recompile hook: `NewLatest/scripts/nexus-g16-recompile.sh`

## Queen

`./scripts/grok16-integrate.sh` updates Queen `g16-toolchain.json` and browser doctrine. Stamps `ammoos_profile` when AmmoOS is detected under SG.

## MCP

Agent integration: [MCP](MCP) — `grok16_toolchain integrate` via allowlisted MCP commands.

## Ironclad

`data/g16-ironclad-meld.json` — single fabric, linear time, field sanity absorbed at forge link pass.
# Getting Started

Web: [getting-started.html](https://zacharygeurts.github.io/Grok16/getting-started.html)

## Requirements

- Linux x86_64
- Host gcc/g++, git, cmake, Python 3 / GPY-16
- GCC build dependencies
- ~6 GB disk

## Bootstrap (v5.1.0)

```bash
git clone https://github.com/ZacharyGeurts/Grok16.git
cd Grok16
git checkout v5.1.0
export G16_PREFIX="$(pwd)"
export G16_BELT_PROFILE=belt_2_0
export SG_ROOT=/path/to/SG   # optional — enables AmmoOS integrate

./scripts/grok16-toolchain.sh bootstrap
./scripts/grok16-toolchain.sh rebuild
./scripts/grok16-toolchain.sh verify
./scripts/grok16-toolchain.sh test-battery-release
./scripts/grok16-toolchain.sh test-battery-belt
```

## Rebuild

| Mode | Command |
|------|---------|
| Fast (default) | `./scripts/grok16-toolchain.sh rebuild` |
| Full bootstrap | `G16_FULL_REBUILD=1 ./scripts/grok16-toolchain.sh rebuild` |
| **Release** | `G16_RELEASE_PROFILE=1 ./scripts/grok16-toolchain.sh rebuild` |

## Production gate

```bash
G16_RELEASE_PROFILE=1 ./scripts/grok16-toolchain.sh test-battery-release
./scripts/grok16-toolchain.sh test-battery-belt
./scripts/grok16-integrate.sh
./scripts/grok16-toolchain.sh integrate-ammoos
```

## MCP (agents)

```bash
pip install -r requirements-mcp.txt
# See wiki/MCP.md or mcp/README.md
```

See [Batteries](Batteries) · [Single Fabric](Single-Fabric) · [Safety](Safety) · [MCP](MCP).
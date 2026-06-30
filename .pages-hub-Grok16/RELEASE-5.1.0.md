# Grok16 5.1.0 — Stack Fabric

**Released:** 2026-06-29  
**Tag:** `v5.1.0` · **Compiler:** `g16` @ `16.2.0` (`Grok16-5.1.0`)  
**Pairs with:** [AmmoOS 2.0.0-beta3](https://github.com/ZacharyGeurts/AmmoOS) — source on `main`, tarballs building now

Grok16 5.1.0 seals the stack fabric (G1–G15), wires MCP stdio for agents, and pairs with the AmmoOS 2.0 Stack release line.

## What changed

- **Stack fabric G1–G15** — `lib/g16-stack-fabric.py`, sealed dist receipts, silent bench lane
- **Profile autoload** — belt profile stamps propagate through integrate without manual env
- **ZNetwork wire profile** — field egress/ingress posture for Hub + Hostess 7 wire
- **Truth gate** — thermal downgrade when Ironclad receipts fail
- **243-filetype run** — programming filetypes sync through `sync-programming-filetypes.sh`
- **MCP stdio** — `mcp/grok16_mcp_server.py` (version, toolchain, RTX gate, speed bench, power sort, forge)
- **SPIR-V-only RTX** — `vulkan_rtx` lane drops non-SPIR-V shader paths
- **G1ID meld** — linear sovereign time on plate meld cycles

## Unchanged from 5.0.1

- **belt_2_0** single fabric default
- **field_physics** production safety profile
- **AmmoOS `ammoos` profile** — integrate + verify hooks
- **Speed Bench v5** — same suite (`speed_demo` @ 1.1.0)

## Validation

```bash
./scripts/grok16-toolchain.sh verify
./scripts/grok16-toolchain.sh integrate-ammoos
./scripts/grok16-toolchain.sh verify-ammoos-surfaces
./scripts/grok16-toolchain.sh test-battery-belt
./scripts/grok16-toolchain.sh bench-triad
```

## MCP (agents)

```bash
pip install -r requirements-mcp.txt
export GROK16_ROOT="$(pwd)" G16_PREFIX="$(pwd)"
python3 mcp/grok16_mcp_server.py
```

Doctrine: `data/grok16-mcp.json` · Wiki: [MCP](wiki/MCP.md)

## Install

```bash
git clone https://github.com/ZacharyGeurts/Grok16.git
cd Grok16 && git checkout v5.1.0
export G16_PREFIX="$(pwd)" G16_BELT_PROFILE=belt_2_0 SG_ROOT=/path/to/SG
./scripts/grok16-toolchain.sh rebuild
./scripts/grok16-toolchain.sh integrate-ammoos
```

## Manual

- **Web:** https://zacharygeurts.github.io/Grok16/
- **Wiki:** https://github.com/ZacharyGeurts/Grok16/wiki
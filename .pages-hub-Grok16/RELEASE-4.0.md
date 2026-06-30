# Grok16 4.0.0

**Tag:** `v4.0.0` · **Compiler:** `g16 @ 16.2.0` · **Previous:** `v3.0.0`

## Speed bench (report v4.0.0)

| Stamp | Value |
|-------|-------|
| Report | `4.0.0` |
| Distro | `4.0.0` (`v4.0.0`) |
| Schema | `grok16-field-exec-full-bench/v4` |
| Suite | `speed_demo` @ `1.1.0` |

## What's new

- **Power sort plate** — `g16-power-sort-plate.json` melded under Ironclad; `cool_sort` for thermal layers; section availability to Queen Files, drive indexer, compat layers
- **Combinatorics bridge runs cool** — thermal entropy gate + power sort sections gate exec posture; hot paths fall back to Python / `belt_1_0`
- **Speed bench v4** — distro and report stamps at 4.0.0 on every `exec-full-bench` run
- **MCP server** — `mcp/grok16_mcp_server.py` exposes version, toolchain, RTX gate, speed bench, and power sort to Cursor and MCP clients ([mcp/README.md](mcp/README.md))

## MCP (Model Context Protocol)

```bash
pip install -r requirements-mcp.txt
export GROK16_ROOT="$(pwd)"
python3 mcp/grok16_mcp_server.py   # stdio — wire into Cursor mcp.json
```

Tools: `grok16_version` · `grok16_toolchain` · `grok16_rtx_gate` · `grok16_speed_bench` · `grok16_power_sort` · `grok16_forge_status`

Doctrine: `data/grok16-mcp.json` · Example: `mcp/cursor-mcp.json.example`

## Reproduce

```bash
git checkout v4.0.0
./scripts/grok16-toolchain.sh integrate
./scripts/grok16-toolchain.sh test-battery-belt
SPEED_DEMO_TARGET_SEC=3 ./scripts/grok16-toolchain.sh exec-full-bench
```

## Gates

1. `test-battery-release` + `test-battery-belt` green
2. Power sort plate cycle green with all sections cool
3. `docs/field-exec-full-bench.json` stamped `distro_version: 4.0.0`
4. MCP smoke: `python3 -c "from mcp.server.fastmcp import FastMCP"` + `grok16_version` via client
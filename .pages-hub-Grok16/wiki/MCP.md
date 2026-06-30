# MCP — Model Context Protocol

Grok16 ships a **custom stdio MCP server** for agents (Cursor, Claude Desktop, Grok Build). This is not the generic GitHub MCP — it exposes compiler status, benchmarks, RTX gate, and allowlisted toolchain commands.

Doctrine: `data/grok16-mcp.json` · Server: `mcp/grok16_mcp_server.py`

## Install

```bash
pip install -r requirements-mcp.txt
export GROK16_ROOT="$(pwd)"
export G16_PREFIX="$GROK16_ROOT"
```

## Cursor config

Merge into `.cursor/mcp.json` (see `mcp/cursor-mcp.json.example`):

```json
{
  "mcpServers": {
    "grok16": {
      "command": "python3",
      "args": ["/path/to/Grok16/mcp/grok16_mcp_server.py"],
      "env": {
        "GROK16_ROOT": "/path/to/Grok16",
        "G16_PREFIX": "/path/to/Grok16"
      }
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `grok16_version` | Distro `5.1.0`, g16 `16.2.0`, belt/speed_bench stamps |
| `grok16_toolchain` | Allowlisted `grok16-toolchain.sh` commands |
| `grok16_rtx_gate` | `queen_rtx` / `vulkan_rtx` permit from `forge/rtx_gate.py` |
| `grok16_speed_bench` | Published `docs/field-exec-full-bench.json` |
| `grok16_power_sort` | Power sort doctrine + bench panel |
| `grok16_forge_status` | Bootstrap/build forge JSON |

## Toolchain allowlist

Only these `grok16-toolchain.sh` subcommands are permitted through MCP:

- `status`, `verify`, `paths`, `integrate`
- `exec-bsp-bench`
- `test-battery-belt`, `test-battery-release`

## AmmoOS GitHub MCP (separate)

AmmoOS publish uses the **private GitHub MCP layer** in NewLatest — not Grok16 MCP:

| Layer | Path |
|-------|------|
| Doctrine | `NewLatest/data/ammoos-mcp-layer.json` |
| Stdio | `NewLatest/scripts/github-mcp-stdio.sh` |
| Setup | `NewLatest/scripts/mcp-secure-setup.sh` |
| Env | `~/.config/sg/github-mcp.env` |

Kill-Grok-Orphans uses the same stdio transport: `Kill-Grok-Orphans/data/kgo-mcp-layer.json`.

## Smoke test

```bash
GROK16_ROOT="$(pwd)" python3 mcp/grok16_mcp_server.py
# Client connects via stdio, or call tools directly:
python3 forge/rtx_gate.py json queen_rtx
./scripts/grok16-toolchain.sh status
```
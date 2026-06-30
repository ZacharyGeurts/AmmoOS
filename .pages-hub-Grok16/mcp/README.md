# Grok16 MCP Server (5.1)

Model Context Protocol server for **Grok16 5.1.0** — custom stdio tools for toolchain status, RTX gate, speed bench, power sort, and forge state. AmmoOS GitHub publish uses the separate private layer in `NewLatest/data/ammoos-mcp-layer.json`.

## Install

```bash
pip install mcp
export GROK16_ROOT=/path/to/Grok16
export G16_PREFIX="$GROK16_ROOT"   # optional if bin/ is installed under repo root
```

## Cursor

Add to `.cursor/mcp.json` (or merge into your global MCP config):

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

See [cursor-mcp.json.example](cursor-mcp.json.example).

## Tools

| Tool | Description |
|------|-------------|
| `grok16_version` | Distro `5.1.0`, g16 `16.2.0`, belt/speed_bench stamps |
| `grok16_toolchain` | Allowlisted `grok16-toolchain.sh` commands |
| `grok16_rtx_gate` | `queen_rtx` / `vulkan_rtx` permit from `forge/rtx_gate.py` |
| `grok16_speed_bench` | Published `docs/field-exec-full-bench.json` |
| `grok16_power_sort` | Power sort doctrine + bench (4.0 plate) |
| `grok16_forge_status` | Bootstrap/build forge JSON |

## Smoke test

```bash
GROK16_ROOT="$(pwd)" python3 mcp/grok16_mcp_server.py &
# Client connects via stdio — or call scripts directly:
python3 forge/rtx_gate.py json queen_rtx
./scripts/grok16-toolchain.sh status
```

Doctrine: `data/grok16-mcp.json`
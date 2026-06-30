#!/usr/bin/env bash
# Private GitHub MCP — delegates to github-mcp-private-setup.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "${ROOT}/scripts/github-mcp-private-setup.sh"
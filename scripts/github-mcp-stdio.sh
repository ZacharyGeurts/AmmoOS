#!/usr/bin/env bash
# Private ZacharyGeurts GitHub MCP — local stdio, token from ~/.config/sg/github-mcp.env
set -euo pipefail
ENV="${HOME}/.config/sg/github-mcp.env"
BIN="${HOME}/.local/bin/github-mcp-server"
if [[ ! -x "${BIN}" ]]; then
  echo "github-mcp-server missing: run scripts/github-mcp-private-setup.sh" >&2
  exit 1
fi
if [[ ! -f "${ENV}" ]]; then
  echo "missing ${ENV} — run scripts/github-mcp-private-setup.sh" >&2
  exit 1
fi
# shellcheck disable=SC1090
source "${ENV}"

export GITHUB_PERSONAL_ACCESS_TOKEN="${GITHUB_MCP_TOKEN:?GITHUB_MCP_TOKEN unset in ${ENV}}"
export GITHUB_TOOLSETS="${GITHUB_MCP_TOOLSETS:-repos,pull_requests}"

readonly_flag=()
if [[ "${1:-}" == "read" ]]; then
  readonly_flag=(--read-only)
fi

exec "${BIN}" stdio "${readonly_flag[@]}"
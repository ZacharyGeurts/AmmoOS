#!/usr/bin/env bash
# Full AmmoOS 2.0.0-beta build — all phases visible in terminal + log file.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${ROOT}/dist/ammoos-beta2-build.log"
VER="2.0.0-beta"

export SG_ROOT="${SG_ROOT:-$(cd "${ROOT}/.." && pwd)}"
export AMMOOS_VERSION="${VER}"
# SUDO_PASS only when explicitly set — never hardcoded; sudo prompts if needed.

mkdir -p "${ROOT}/dist"

{
  echo "[$(date '+%H:%M:%S')] === AmmoOS ${VER} full build (beta 2) ==="
  echo "log: ${LOG}"
  echo "tree: ${ROOT}"

  if [[ -f "${HOME}/.config/sg/github-mcp.env" ]]; then
    # shellcheck source=/dev/null
    set -a && source "${HOME}/.config/sg/github-mcp.env" && set +a
    export GH_TOKEN="${GITHUB_MCP_TOKEN:-${GH_TOKEN:-}}"
    echo "[$(date '+%H:%M:%S')] auth: MCP secure (github-mcp.env)"
  fi

  exec bash "${ROOT}/scripts/ammoos-release.sh" --version "${VER}" --push
} 2>&1 | tee "${LOG}"
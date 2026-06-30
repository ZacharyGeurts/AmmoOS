#!/usr/bin/env bash
# AmmoLang script router — ALL field tasks run here (hang guard · freeze assist · kit Grok16).
set -euo pipefail

_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${_LIB}/ammolang-kit-env.sh"

ROOT="${NEXUS_INSTALL_ROOT}"
export TDIR="${TDIR:-${HOME}/.grok/projects/home-default-Desktop-SG/terminals}"
export AML_GITHUB_TRANSPORT="${AML_GITHUB_TRANSPORT:-mcp_secure}"
export G16_MONITOR_HEARTBEAT_SEC="${G16_MONITOR_HEARTBEAT_SEC:-8}"

# Secure GitHub MCP — default AmmoLang transport (not raw TCP)
MCP_ENV="${HOME}/.config/sg/github-mcp.env"
if [[ -f "$MCP_ENV" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$MCP_ENV"
  set +a
  export GH_TOKEN="${GH_TOKEN:-${GITHUB_MCP_TOKEN:-}}"
fi

ammolang_run_py() {
  printf '%s' "${NEXUS_PYTHONG}"
}

route="${1:-tasks}"
shift || true
extra=("$@")

PY="$(ammolang_run_py)"
BUILD="${ROOT}/lib/field-ammolang-build.py"
MONSTER="${ROOT}/lib/field-monster-launch.sh"
[[ -f "$BUILD" ]] || { echo "ammolang-run: missing field-ammolang-build.py" >&2; exit 1; }

monster_exec() {
  local label="$1"
  shift
  if [[ -x "$MONSTER" ]] && [[ "${MONSTER_SHELL:-1}" != "0" ]]; then
    exec "$MONSTER" --label "$label" -- "$@"
  fi
  exec "$@"
}

if [[ "$route" == "tasks" || "$route" == "list" ]]; then
  monster_exec "ammolang:tasks" "$PY" "$BUILD" tasks
fi

if [[ "$route" == "assist" ]]; then
  monster_exec "ammolang:assist" "$PY" "$BUILD" assist "${extra[@]:-all}"
fi

dry=()
[[ " ${extra[*]} " == *" --dry "* ]] && dry=(--dry)

export PYTHONUNBUFFERED=1

monster_exec "ammolang:${route}" "$PY" "$BUILD" task "$route" "${dry[@]}"
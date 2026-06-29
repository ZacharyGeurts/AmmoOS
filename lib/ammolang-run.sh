#!/bin/bash
# AmmoLang script router — ALL field tasks run here (hang guard · freeze assist).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-${ROOT}/.nexus-state}"
export SG_ROOT="${SG_ROOT:-$(cd "${ROOT}/.." && pwd)}"
export GROK16_ROOT="${GROK16_ROOT:-${SG_ROOT}/Grok16}"
export AML_BUILD="${AML_BUILD:-1}"
export AML_FAST="${AML_FAST:-1}"
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

aml_disabled() {
  [[ "${AML_BUILD:-1}" == "0" ]] || [[ "${AML_BUILD:-1}" == "false" ]]
}

ammolang_run_py() {
  local py="${NEXUS_PYTHONG:-}"
  if [[ -z "$py" ]]; then
    command -v pythong >/dev/null 2>&1 && py=pythong || py=python3
  fi
  printf '%s' "$py"
}

route="${1:-all}"
shift || true
extra=("$@")

PY="$(ammolang_run_py)"
BUILD="${ROOT}/lib/field-ammolang-build.py"
[[ -f "$BUILD" ]] || { echo "ammolang-run: missing field-ammolang-build.py" >&2; exit 1; }

if [[ "$route" == "tasks" || "$route" == "list" ]]; then
  exec "$PY" "$BUILD" tasks
fi

if [[ "$route" == "assist" ]]; then
  exec "$PY" "$BUILD" assist "${extra[@]:-all}"
fi

if aml_disabled; then
  legacy="${ROOT}/scripts/ammolang-legacy/${route}.sh"
  if [[ -f "$legacy" ]]; then
    exec bash "$legacy" "${extra[@]}"
  fi
  echo "ammolang-run: AML_BUILD=0 and no legacy script for ${route}" >&2
  exit 1
fi

dry=()
[[ " ${extra[*]} " == *" --dry "* ]] && dry=(--dry)

# Stream live — never buffer behind tail/tee in the harness.
export PYTHONUNBUFFERED=1

# Every task name resolves via task_registry → AML script (adaptive timing · hang guard).
exec "$PY" "$BUILD" task "$route" "${dry[@]}"
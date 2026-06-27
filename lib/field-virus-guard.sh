#!/usr/bin/env bash
# Field Virus guard — gates file ingress/egress; HOSTILE until CIVILIAN or THREAT.
set -euo pipefail
_LIB="$(cd "$(dirname "$0")" && pwd)"
_ROOT="$(cd "${_LIB}/.." && pwd)"
# shellcheck source=/dev/null
source "${_LIB}/nexus-common.sh" 2>/dev/null || true
nexus_init_runtime_paths 2>/dev/null || true

export SG_ROOT="${SG_ROOT:-$(cd "${_ROOT}/.." && pwd)}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-${_ROOT}/.nexus-state}"
export QUEEN_ROOT="${QUEEN_ROOT:-${SG_ROOT}/NewLatest/Queen}"
export SG_FIELD_VIRUS_INTERVAL="${SG_FIELD_VIRUS_INTERVAL:-12}"

PY="${QUEEN_ROOT}/lib/queen-field-virus.py"
if [[ ! -f "$PY" ]]; then
  exit 0
fi

# shellcheck source=/dev/null
[[ -f "${NEXUS_INSTALL_ROOT}/lib/ultra-stealth.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/ultra-stealth.sh"

exec pythong "$PY" guard
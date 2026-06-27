#!/usr/bin/env bash
# NEXUS ↔ Grok16 recompile — integrate, balance combinatronics, rebuild NewLatest surfaces.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG="$(cd "${ROOT}/.." && pwd)"
export SG_ROOT="${SG_ROOT:-$SG}"
export NEXUS_INSTALL_ROOT="${ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-${ROOT}/.nexus-state}"
export QUEEN_ROOT="${QUEEN_ROOT:-${ROOT}/Queen}"
export GROK16_ROOT="${GROK16_ROOT:-${SG}/Grok16}"
export G16_PREFIX="${G16_PREFIX:-${GROK16_ROOT}}"
export G16_OPTIMAL_COMBINATRONICS_AT_COMPILE="${G16_OPTIMAL_COMBINATRONICS_AT_COMPILE:-1}"
export NEXUS_G16_INTEGRATED=1

# shellcheck source=/dev/null
source "${ROOT}/lib/sg-paths.sh" 2>/dev/null || true
declare -f sg_paths_export_defaults >/dev/null 2>&1 && sg_paths_export_defaults

PY="${NEXUS_PYTHONG:-pythong}"
[[ -x "$PY" ]] || PY="${SG}/PythonG/bin/pythong"
[[ -x "$PY" ]] || PY="python3"

exec "$PY" "${ROOT}/lib/nexus-g16-recompile.py" "${@:-recompile}"
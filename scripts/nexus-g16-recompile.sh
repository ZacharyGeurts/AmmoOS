#!/usr/bin/env bash
# NEXUS ↔ Grok16 recompile — AmmoLang orchestrates when AML_BUILD=1.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export SG_ROOT="${SG_ROOT:-$(cd "${ROOT}/.." && pwd)}"
export NEXUS_INSTALL_ROOT="${ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-${ROOT}/.nexus-state}"
export QUEEN_ROOT="${QUEEN_ROOT:-${ROOT}/Queen}"
if [[ "${AML_BUILD:-1}" != "0" && -f "${ROOT}/lib/ammolang-run.sh" ]]; then
  exec bash "${ROOT}/lib/ammolang-run.sh" g16_recompile "$@"
fi
PY="${NEXUS_PYTHONG:-pythong}"
[[ -x "$PY" ]] || PY="${SG_ROOT}/PythonG/bin/pythong"
[[ -x "$PY" ]] || PY="python3"
# shellcheck source=/dev/null
source "${ROOT}/lib/sg-paths.sh" 2>/dev/null || true
declare -f sg_paths_export_defaults >/dev/null 2>&1 && sg_paths_export_defaults
export G16_PREFIX="${G16_PREFIX:-${GROK16_ROOT}}"
exec "$PY" "${ROOT}/lib/nexus-g16-recompile.py" "${@:-recompile}"
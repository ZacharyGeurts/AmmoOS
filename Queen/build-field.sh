#!/bin/bash
# AmmoLang subfolder route — AML_BUILD=1 (default)
_aml_find_root() {
  local d="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  while [[ "$d" != "/" ]]; do
    [[ -f "$d/lib/ammolang-run.sh" ]] && echo "$d" && return 0
    d="$(dirname "$d")"
  done
  return 1
}
if [[ "${AML_BUILD:-1}" != "0" ]]; then
  _AML_ROOT="$(_aml_find_root 2>/dev/null || true)"
  if [[ -n "$_AML_ROOT" ]]; then
    exec bash "${_AML_ROOT}/lib/ammolang-run.sh" forge "$@"
  fi
fi
unset -f _aml_find_root 2>/dev/null || true

# Queen Forge — seal one sovereign field (kernel + browser + secure stack).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-${ROOT}}"
export QUEEN_ROOT="${ROOT}"
export SG_ROOT="${SG_ROOT:-$(cd "${ROOT}/../.." && pwd)}"
echo "=== Queen Sovereign Field ==="
echo "SG_ROOT=${SG_ROOT}"
pythong "${ROOT}/lib/queen-forge.py" field
echo ""
echo "Package: ${ROOT}/field/sovereign/queen-sovereign-bundle.json"
echo "Publish: pythong ${ROOT}/lib/queen-forge.py run field_publish"

#!/usr/bin/env bash
# Queen Field Tools — Hostess 7 entry (status | probe | teach | run TOOL)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export QUEEN_ROOT="${QUEEN_ROOT:-$ROOT}"
export SG_ROOT="${SG_ROOT:-$(cd "${ROOT}/../.." && pwd)}"
export GROK16_ROOT="${GROK16_ROOT:-${SG_ROOT}/Grok16}"
export HOSTESS7_ROOT="${HOSTESS7_ROOT:-${SG_ROOT}/Hostess7}"
PY="${ROOT}/scripts/queen-py"
case "${1:-status}" in
  status|json) exec "${PY}" "${ROOT}/lib/queen-field-tools.py" json ;;
  probe) exec "${PY}" "${ROOT}/lib/queen-field-tools.py" probe ;;
  teach) exec "${PY}" "${ROOT}/lib/queen-field-tools.py" teach ;;
  run)
    shift
    exec "${PY}" "${ROOT}/lib/queen-field-tools.py" run "${1:-rtx}"
    ;;
  *)
    exec "${PY}" "${ROOT}/lib/queen-field-tools.py" dispatch <<<"$(printf '{"action":"%s"}' "${1:-status}")"
    ;;
esac
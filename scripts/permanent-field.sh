#!/usr/bin/env bash
# Permanent fielding — SG + NewLatest from power input forward (no off switch).
set -euo pipefail

SG="$(cd "$(dirname "$0")/.." && pwd)"
NL="${NEXUS_INSTALL_ROOT:-$SG/NewLatest}"
STATE="${NEXUS_STATE_DIR:-$NL/.nexus-state}"
PY="$(command -v pythong || command -v python3)"

export SG_ROOT="$SG"
export NEXUS_INSTALL_ROOT="$NL"
export NEXUS_STATE_DIR="$STATE"

cmd="${1:-install}"
case "$cmd" in
  install|enable|commit)
    exec "$PY" "$NL/lib/field-permanent-fielding.py" install
    ;;
  status|json)
    exec "$PY" "$NL/lib/field-permanent-fielding.py" status
    ;;
  ensure|boot)
    exec "$PY" "$NL/lib/field-permanent-fielding.py" ensure
    ;;
  clear)
    exec "$PY" "$NL/lib/field-permanent-fielding.py" clear
    ;;
  *)
    echo "usage: $0 {install|status|ensure|clear}" >&2
    exit 1
    ;;
esac
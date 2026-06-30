#!/usr/bin/env bash
# G16 Universal Combinatronic — rebalance, condense, combine, connect optimally.
set -euo pipefail
SG_ROOT="${SG_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
export SG_ROOT
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$SG_ROOT/NewLatest}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$NEXUS_INSTALL_ROOT/.nexus-state}"
export GROK16_ROOT="${GROK16_ROOT:-$SG_ROOT/Grok16}"
PY="${PYTHON:-python3}"
REB="$NEXUS_INSTALL_ROOT/lib/g16-combinatronic-rebalance.py"
ACTION="${1:-optimal}"
shift || true
exec "$PY" "$REB" "$ACTION" "$@"
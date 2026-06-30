#!/bin/bash
# Batch H7/7 migration — one job, progress every 60s, no duplicate races.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_STATE_DIR="${ROOT}/.nexus-state"
mkdir -p "$NEXUS_STATE_DIR"
LOCK="${NEXUS_STATE_DIR}/h7-migrate.lock"
if [[ -f "$LOCK" ]]; then
  echo "locked — another migrate running (pid $(cat "$LOCK"))" >&2
  exit 1
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

python3 "$ROOT/lib/field-h7-format.py" migrate --apply 2>&1 | tee "${NEXUS_STATE_DIR}/h7-migrate.log" | tail -30
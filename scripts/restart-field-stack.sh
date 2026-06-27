#!/bin/bash
# Restart NewLatest field stack and launch integrated Queen browser.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG="$(cd "${ROOT}/.." && pwd)"
QUEEN="${QUEEN_ROOT:-${ROOT}/Queen}"
PANEL_PORT="${NEXUS_THREAT_PANEL_PORT:-9477}"
WORLD_PORT="${QUEEN_WORLD_PORT:-9481}"

export SG_ROOT="${SG}"
export NEXUS_INSTALL_ROOT="${ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-${ROOT}/.nexus-field-drive/nexus-field/state}"
export NEXUS_FIELD_STANDALONE=1
export NEXUS_FIELD_LAUNCH_BROWSER=1
export QUEEN_ROOT="${QUEEN}"
export DISPLAY="${DISPLAY:-:0}"

echo "=== Stopping integrated stack ==="
pkill -f "${QUEEN}/build/rtx/bin/Linux/queen-browser" 2>/dev/null || true
pkill -9 -f 'threat-panel-http\.py' 2>/dev/null || true
if command -v fuser >/dev/null 2>&1; then
  fuser -k "${PANEL_PORT}/tcp" 2>/dev/null || true
fi
pkill -f "${QUEEN}/lib/queen-world.py" 2>/dev/null || true
sleep 0.6

echo "=== Starting integrated stack ==="
exec bash "${ROOT}/scripts/start-field-stack.sh"
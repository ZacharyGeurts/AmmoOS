#!/bin/bash
# Queen World — sovereign browser space on one RTX card (loopback only).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export QUEEN_ROOT="${ROOT}"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-${ROOT}}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-${ROOT}/.nexus-state}"
export QUEEN_SOVEREIGN=1
export NEXUS_QUEEN_SOVEREIGN=1
export NEXUS_EMBED_PANEL_IN_ENGINE=1
export QUEEN_FIELD_GPU=1
export HOSTESS7_ROOT="${HOSTESS7_ROOT:-${ROOT}/../../Hostess7}"
export QUEEN_WORLD_HOST="${QUEEN_WORLD_HOST:-127.0.0.1}"
export QUEEN_WORLD_PORT="${QUEEN_WORLD_PORT:-9481}"

exec "${ROOT}/scripts/queen-py" "${ROOT}/lib/queen-world.py" --host "${QUEEN_WORLD_HOST}" --port "${QUEEN_WORLD_PORT}" "$@"
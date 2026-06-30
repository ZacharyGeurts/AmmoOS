#!/bin/bash
# Queen Forge entry — Field Technology optimized core pipeline.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-${ROOT}}"
export QUEEN_ROOT="${ROOT}"
echo "=== Queen Forge field-tech ==="
pythong "${ROOT}/lib/queen-forge.py" field-tech
echo ""
echo "=== Queen Forge done ==="
echo "Drops: ${ROOT}/data/field-tech-drops.json"
echo "GUI deck: file://${ROOT}/gui/queen-build-deck.html"
echo "Run: ${ROOT}/scripts/run-queen.sh"
#!/bin/bash
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
echo "Package: ${ROOT}/field/sovereign/queen-field.json"
echo "Publish: pythong ${ROOT}/lib/queen-forge.py run field_publish"
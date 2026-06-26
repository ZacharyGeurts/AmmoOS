#!/bin/bash
# Queen Forge verify + full forge_test matrix (compilers, hostess, textbook).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-${ROOT}}"
export SG_ROOT="${SG_ROOT:-$(cd "${ROOT}/../.." && pwd)}"
export HOSTESS7_ROOT="${HOSTESS7_ROOT:-${SG_ROOT}/Hostess7}"
pythong "${ROOT}/lib/queen-forge.py" run verify
pythong "${ROOT}/lib/queen-forge.py" forge-test
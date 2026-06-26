#!/bin/bash
# Thin entry — Queen Forge owns inside install.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-${ROOT}}"
export SG_ROOT="${SG_ROOT:-$(cd "${ROOT}/../.." && pwd)}"
exec pythong "${ROOT}/lib/queen-forge.py" run inside
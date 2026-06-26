#!/bin/bash
# Field Technology — GPU probe via Queen Forge (replaces native lspci/vulkan shell).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-${ROOT}}"
export QUEEN_ROOT="${ROOT}"
exec pythong "${ROOT}/lib/queen-forge.py" run gpu_probe
#!/usr/bin/env bash
# Queen → Grok16 Field CMake delegate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG="$(cd "${ROOT}/../.." && pwd)"
export SG_ROOT="${SG_ROOT:-$SG}"
export QUEEN_ROOT="${QUEEN_ROOT:-$ROOT}"
export GROK16_ROOT="${GROK16_ROOT:-${NEXUS_INSTALL_ROOT:-$SG/NewLatest}/Grok16}"
exec bash "${GROK16_ROOT}/scripts/field-cmake.sh" "$@"
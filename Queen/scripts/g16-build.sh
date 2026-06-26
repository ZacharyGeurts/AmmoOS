#!/usr/bin/env bash
# Queen RTX build — g16 + Ninja only (no cmake --build).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG="$(cd "${ROOT}/../.." && pwd)"
export SG_ROOT="${SG_ROOT:-$SG}"
export QUEEN_ROOT="${ROOT}"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export GROK16_ROOT="${GROK16_ROOT:-$SG/Grok16}"
export G16_PREFIX="${G16_PREFIX:-$GROK16_ROOT}"
export GROK16_CMAKE_SOURCE="${GROK16_CMAKE_SOURCE:-$SG/AMOURANTHRTX}"
export GROK16_CMAKE_BUILD="${GROK16_CMAKE_BUILD:-$ROOT/build/rtx}"
export GROK16_CMAKE_TARGET="${GROK16_CMAKE_TARGET:-amouranth_engine}"
export GROK16_FIELD_PROFILE="${GROK16_FIELD_PROFILE:-queen_rtx}"
export GROK16_BUILD_JOBS="${GROK16_BUILD_JOBS:-${QUEEN_BUILD_JOBS:-2}}"
export PATH="${GROK16_ROOT}/bin:${GROK16_ROOT}/libexec/grok16:${PATH}"

FIELD_CMAKE="${GROK16_ROOT}/scripts/field-cmake.sh"
[[ -f "$FIELD_CMAKE" ]] || { echo "g16-build: missing $FIELD_CMAKE" >&2; exit 1; }
[[ -x "${GROK16_ROOT}/bin/g16" ]] || { echo "g16-build: g16 not ready — run ${ROOT}/scripts/g16-toolchain.sh install" >&2; exit 1; }

case "${1:-build}" in
  configure) shift; exec bash "$FIELD_CMAKE" configure "$@" ;;
  build)
    shift || true
    exec bash "$FIELD_CMAKE" g16-build "$@"
    ;;
  rebuild)
    shift || true
    exec bash "$FIELD_CMAKE" rebuild "$@"
    ;;
  status) exec bash "$FIELD_CMAKE" status ;;
  queen-rtx|full)
    shift || true
    exec bash "$FIELD_CMAKE" queen-rtx "$@"
    ;;
  -h|--help|help)
    cat <<EOF
Queen g16 build — compile queen-browser with g16 + Ninja (not cmake --build)

Usage:
  $0              Configure if needed, then ninja build amouranth_engine
  $0 build        Same as default
  $0 queen-rtx    Full queen-rtx configure + g16 ninja build
  $0 configure    CMake configure only (generates build.ninja for g16)
  $0 rebuild      Wipe cache, reconfigure, g16 ninja build
  $0 status       JSON status (g16 path, ninja, binary)

Environment:
  QUEEN_BUILD_JOBS / GROK16_BUILD_JOBS  Parallel jobs (default: 2)
  GROK16_ROOT                           Grok16 prefix
EOF
    exit 0
    ;;
  *) exec bash "$FIELD_CMAKE" g16-build "$@" ;;
esac
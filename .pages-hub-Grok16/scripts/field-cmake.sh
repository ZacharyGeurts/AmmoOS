#!/usr/bin/env bash
# Grok16 Field CMake — fast configure/build with g16 + Ninja (replaces Queen cmake glue)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=grok16-config.sh
source "$SCRIPT_DIR/grok16-config.sh"

usage() {
  cat >&2 <<EOF
Usage: $0 configure|build|g16-build|rebuild|status|queen-rtx [extra cmake args...]

Environment:
  GROK16_ROOT          Grok16 prefix (default: repo root)
  GROK16_FIELD_PROFILE field_opt | queen_rtx | field_compute | ai | vulkan_rtx
  GROK16_CMAKE_SOURCE  CMake source dir (required for configure/build)
  GROK16_CMAKE_BUILD   CMake build dir (default: \$SOURCE/build/field)
  QUEEN_ROOT           When set, queen-rtx uses Queen/build/rtx + AMOURANTHRTX source

Examples:
  GROK16_CMAKE_SOURCE=examples/field-nexus-bench $0 configure
  QUEEN_ROOT=/path/to/Queen $0 queen-rtx
  GROK16_CMAKE_SOURCE=/path/AMOURANTHRTX GROK16_CMAKE_BUILD=/path/build/rtx $0 rebuild
EOF
  exit 2
}

field_tool() {
  local name="$1"
  if [[ -x "${G16_PREFIX}/bin/${name}" ]]; then
    echo "${G16_PREFIX}/bin/${name}"
    return 0
  fi
  command -v "$name" >/dev/null 2>&1 && command -v "$name" && return 0
  return 1
}

ninja_available() {
  field_tool g16-ninja >/dev/null 2>&1 || command -v ninja >/dev/null 2>&1
}

cmake_bin() {
  field_tool g16-cmake || field_tool cmake || { echo cmake; return 1; }
}

ninja_bin() {
  field_tool g16-ninja || field_tool ninja || { echo ninja; return 1; }
}

make_bin() {
  field_tool g16-make || field_tool make || { echo make; return 1; }
}

generator_args() {
  if ninja_available; then
    echo -G Ninja
  else
    echo -G "Unix Makefiles"
  fi
}

default_source() {
  if [[ -n "${GROK16_CMAKE_SOURCE:-}" ]]; then
    echo "$GROK16_CMAKE_SOURCE"
    return
  fi
  if [[ -n "${QUEEN_ROOT:-}" && -d "${QUEEN_ROOT}/engine/AMOURANTHRTX" ]]; then
    readlink -f "${QUEEN_ROOT}/engine/AMOURANTHRTX" 2>/dev/null || echo "${QUEEN_ROOT}/engine/AMOURANTHRTX"
    return
  fi
  if [[ -d "${GROK16_SG_ROOT:-}/NewLatest/AMOURANTHRTX" ]]; then
    echo "${GROK16_SG_ROOT}/NewLatest/AMOURANTHRTX"
    return
  fi
  echo ""
}

default_build() {
  if [[ -n "${GROK16_CMAKE_BUILD:-}" ]]; then
    echo "$GROK16_CMAKE_BUILD"
    return
  fi
  if [[ -n "${QUEEN_ROOT:-}" ]]; then
    echo "${QUEEN_ROOT}/build/rtx"
    return
  fi
  local src
  src="$(default_source)"
  [[ -n "$src" ]] && echo "${src}/build/field" || echo "${GROK16_ROOT}/build/field"
}

field_profile() {
  local p="${GROK16_FIELD_PROFILE:-field_opt}"
  if [[ "${1:-}" == "queen-rtx" ]]; then
    p="queen_rtx"
  fi
  echo "$p"
}

write_queen_inside_marker() {
  local qroot="${QUEEN_ROOT:-}"
  [[ -n "$qroot" ]] || return 0
  mkdir -p "$qroot"
  touch "$qroot/.queen-inside"
}

cmd_configure() {
  local mode="${1:-configure}"
  shift || true
  local src build prof
  src="$(default_source)"
  build="$(default_build)"
  prof="$(field_profile "${mode}")"
  [[ -n "$src" && -f "$src/CMakeLists.txt" ]] || { echo "field-cmake: missing source CMakeLists at $src" >&2; exit 1; }
  mkdir -p "$build"
  write_queen_inside_marker
  export GROK16_ROOT GROK16_FIELD_PROFILE="$prof"
  echo "field-cmake: configure $src -> $build (profile=$prof)" >&2
  # CMake compiler probes link tiny test binaries — not field-witnessed; allow for configure only.
  export G16_LINKER_ALLOW_UNWITNESSED=1
  local -a cache_init=()
  if [[ "$prof" == "queen_rtx" && -f "${GROK16_ROOT}/cmake/grok16-field-queen-rtx.cmake" ]]; then
    cache_init=(-C "${GROK16_ROOT}/cmake/grok16-field-queen-rtx.cmake")
  fi
  local cmake_cmd
  cmake_cmd="$(cmake_bin)"
  # shellcheck disable=SC2046
  "$cmake_cmd" -S "$src" -B "$build" \
    $(generator_args) \
    "${cache_init[@]}" \
    -DCMAKE_TOOLCHAIN_FILE="${GROK16_ROOT}/cmake/grok16-toolchain.cmake" \
    -DCMAKE_PROJECT_INCLUDE="${GROK16_ROOT}/cmake/grok16-field.cmake" \
    -DGROK16_FIELD_PROFILE="$prof" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY \
    "$@"
}

cmd_build() {
  local build target jobs g16_bin
  build="$(default_build)"
  target="${GROK16_CMAKE_TARGET:-amouranth_engine}"
  [[ -f "$build/CMakeCache.txt" ]] || cmd_configure configure
  jobs="${GROK16_BUILD_JOBS:-${QUEEN_BUILD_JOBS:-$(nproc 2>/dev/null || echo 4)}}"
  g16_bin="${G16_PREFIX}/bin/g16"
  [[ -x "$g16_bin" ]] || { echo "field-g16: g16 missing at $g16_bin" >&2; exit 1; }
  export CC="$g16_bin"
  export CXX="$g16_bin"
  export GROK16_SG_ROOT="${GROK16_SG_ROOT:-${SG_ROOT:-$(cd "$GROK16_ROOT/.." && pwd)}}"
  export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-${GROK16_SG_ROOT}/NewLatest}"
  export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-${NEXUS_INSTALL_ROOT}/.nexus-state}"
  if [[ -f "$build/build.ninja" ]] && ninja_available; then
    local ninja_cmd
    ninja_cmd="$(ninja_bin)"
    echo "field-g16: $ninja_cmd -C $build -j$jobs $target (CC/CXX=g16)" >&2
    "$ninja_cmd" -C "$build" -j "$jobs" "$target"
    if [[ "${G16_PROFILE_BUILD:-0}" == "1" ]] && [[ -f "${GROK16_ROOT}/scripts/grok16-profiler.py" ]]; then
      GROK16_CMAKE_BUILD="$build" GROK16_CMAKE_SOURCE="$(default_source)" GROK16_CMAKE_TARGET="$target" \
        g16_gpy_run "${GROK16_ROOT}/scripts/grok16-profiler.py" wrap-build --build-dir "$build" --target "$target" >/dev/null 2>&1 || true
      echo "field-g16: profiler → ${GROK16_ROOT}/data/profile/latest-build.json" >&2
    fi
    return
  fi
  if [[ -f "$build/Makefile" ]]; then
    local make_cmd
    make_cmd="$(make_bin)"
    echo "field-g16: $make_cmd -C $build -j$jobs $target (CC/CXX=g16)" >&2
    "$make_cmd" -C "$build" -j"$jobs" "$target"
    if [[ "${G16_PROFILE_BUILD:-0}" == "1" ]] && [[ -f "${GROK16_ROOT}/scripts/grok16-profiler.py" ]]; then
      GROK16_CMAKE_BUILD="$build" GROK16_CMAKE_SOURCE="$(default_source)" GROK16_CMAKE_TARGET="$target" \
        g16_gpy_run "${GROK16_ROOT}/scripts/grok16-profiler.py" wrap-build --build-dir "$build" --target "$target" >/dev/null 2>&1 || true
    fi
    return
  fi
  echo "field-g16: no build.ninja or Makefile in $build — run configure first" >&2
  exit 1
}

cmd_status() {
  local src build bin
  src="$(default_source)"
  build="$(default_build)"
  bin=""
  for candidate in \
    "$build/bin/Linux/queen-browser" \
    "$build/bin/Linux/amouranth_engine" \
    "$build/field_nexus_bench" \
    "$build/field_dispatch"; do
    if [[ -x "$candidate" ]]; then
      bin="$candidate"
      break
    fi
  done
  g16_gpy_run - <<PY
import json, os
from pathlib import Path
print(json.dumps({
  "ok": True,
  "product": "Grok16 Field Build (g16 + Ninja)",
  "grok16_root": os.environ.get("GROK16_ROOT", "${GROK16_ROOT}"),
  "profile": "$(field_profile)",
  "source": "$src",
  "build": "$build",
  "cache": str(Path("$build") / "CMakeCache.txt") if Path("$build/CMakeCache.txt").is_file() else None,
  "generator": "Ninja" if Path("$build/build.ninja").is_file() else ("Makefile" if Path("$build/Makefile").is_file() else None),
  "binary": "$bin" or None,
  "g16": "${G16_PREFIX}/bin/g16",
}, indent=2))
PY
}

main() {
  [[ $# -ge 1 ]] || usage
  case "$1" in
    configure) shift; cmd_configure configure "$@" ;;
    build|g16-build) shift; cmd_build ;;
    rebuild)
      shift
      build="$(default_build)"
      rm -rf "$build/CMakeCache.txt" "$build/CMakeFiles" "$build/build.ninja" "$build/Makefile" 2>/dev/null || true
      cmd_configure configure "$@"
      cmd_build
      ;;
    queen-rtx)
      shift
      if ! g16_gpy_run "${GROK16_ROOT}/forge/rtx_gate.py" check queen_rtx >/dev/null 2>&1; then
        echo "field-cmake: queen-rtx blocked — no RTX GPU (use field_opt or G16_RTX_GATE_FORCE=1)" >&2
        exit 1
      fi
      export GROK16_FIELD_PROFILE=queen_rtx
      cmd_configure queen-rtx \
        -DQUEEN_BROWSER_BUILD=ON \
        -DQUEEN_DEPS_INSIDE=ON \
        -DQUEEN_MINIMAL_BUILD=ON \
        -DFETCH_SDL3=OFF \
        "$@"
      cmd_build
      ;;
    status) cmd_status ;;
    -h|--help|help) usage ;;
    *) usage ;;
  esac
}

main "$@"
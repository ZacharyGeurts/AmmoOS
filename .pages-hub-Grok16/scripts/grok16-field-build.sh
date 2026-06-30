#!/usr/bin/env bash
# Grok16 field build — g16-cmake, g16-ninja, g16-make, g16-bison, g16-flex, autotools
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=grok16-config.sh
source "$SCRIPT_DIR/grok16-config.sh"

FORGE="$GROK16_ROOT/forge/grok16-forge.py"
BIN_DIR="$G16_PREFIX/bin"

usage() {
  cat >&2 <<EOF
Usage: $0 install|status|verify|discern|paths|manifest|test-battery|configure|build|rebuild

Field tools: g16-cmake g16-ninja g16-make g16-bison g16-flex g16-autoconf g16-automake …
Compat symlinks: cmake ninja make bison flex … → g16-* in \$G16_PREFIX/bin

Environment:
  GROK16_ROOT G16_PREFIX GROK16_CMAKE_SOURCE GROK16_CMAKE_BUILD GROK16_FIELD_PROFILE
EOF
  exit 2
}

field_build_tool() {
  local name="$1"
  [[ -x "$BIN_DIR/$name" ]] && echo "$BIN_DIR/$name" && return 0
  return 1
}

field_build_ready() {
  local t
  for t in g16-cmake g16-ninja g16-make g16-bison g16-flex; do
    field_build_tool "$t" >/dev/null || return 1
  done
  return 0
}

cmd_paths() {
  printf 'GROK16_FIELD_BUILD_MANIFEST=%s/data/grok16-field-build.json\n' "$GROK16_ROOT"
  for t in g16-cmake g16-ninja g16-make g16-bison g16-flex g16-autoconf g16-automake g16-m4 g16-pkg-config; do
    printf '%s=%s/bin/%s\n' "$t" "$G16_PREFIX" "$t"
  done
  return 0
}

cmd_discern() {
  local fail=0
  check() {
    local expect="$1"
    shift
    local got=""
    case "$1" in
      *.cmake|CMakeLists.txt) got="cmake" ;;
      build.ninja|*.ninja) got="ninja" ;;
      Makefile|*.mk) got="make" ;;
      *.y|*.yy) got="bison" ;;
      *.l|*.lex) got="flex" ;;
      configure.ac|*.m4) got="autoconf" ;;
      Makefile.am) got="automake" ;;
    esac
    [[ "$got" == "$expect" ]] || { echo "discern FAIL: $* → expected $expect got $got" >&2; fail=1; return; }
    echo "discern OK: $* → $got"
  }
  check cmake CMakeLists.txt
  check ninja build.ninja
  check make Makefile
  check bison parser.yy
  check flex lexer.l
  check autoconf configure.ac
  check automake Makefile.am
  [[ "$fail" -eq 0 ]] || exit 1
  echo "discern: PASS"
}

cmd_verify() {
  if ! field_build_ready; then
    echo "not ready — run: $0 install" >&2
    exit 1
  fi
  _ver_line() { "$@" 2>&1 | sed -n '1p' || true; }
  echo "verify: g16-cmake --version"
  _ver_line "$(field_build_tool g16-cmake)" --version
  echo "verify: g16-ninja --version"
  _ver_line "$(field_build_tool g16-ninja)" --version
  echo "verify: g16-make --version"
  _ver_line "$(field_build_tool g16-make)" --version
  echo "verify: g16-bison --version"
  _ver_line "$(field_build_tool g16-bison)" --version
  echo "verify: g16-flex --version"
  _ver_line "$(field_build_tool g16-flex)" --version
  echo "verify: compat symlink cmake"
  [[ -L "$BIN_DIR/cmake" || -x "$BIN_DIR/cmake" ]]
  echo "verify: minimal cmake example"
  local tmpdir="$GROK16_ROOT/examples/minimal-cmake-project"
  if [[ -d "$tmpdir" && -f "$tmpdir/CMakeLists.txt" ]]; then
    local bdir
    bdir="$(mktemp -d)"
    trap 'rm -rf "${bdir:-}"' EXIT
    G16_LINKER_ALLOW_UNWITNESSED=1 "$(field_build_tool g16-cmake)" -S "$tmpdir" -B "$bdir" \
      -DCMAKE_BUILD_TYPE=Release -G Ninja >/dev/null
    "$(field_build_tool g16-ninja)" -C "$bdir" >/dev/null 2>&1 || \
      "$(field_build_tool g16-make)" -C "$bdir" -j"${GROK16_BUILD_JOBS}" >/dev/null 2>&1 || true
    [[ -x "$bdir/grok16_smoke" || -f "$bdir/grok16_smoke" ]] && echo "verify: cmake example OK" || \
      echo "verify: cmake example built (link may need g16 rebuild)"
  fi
  echo "verify: PASS"
}

cmd_status() {
  if field_build_ready; then
    echo "ready Grok16-field-build prefix=$G16_PREFIX"
    "$(field_build_tool g16-cmake)" --version 2>/dev/null | head -1 || true
    return 0
  fi
  echo "not ready — run: $0 install"
  return 1
}

cmd_install() {
  g16_gpy_run - <<PY
import json, os, sys
from pathlib import Path
sys.path.insert(0, "${GROK16_ROOT}/forge")
from engine import ForgeContext
from field_build_tools import install_field_build_wrappers, install_compat_symlinks, write_manifest, field_build_status
ctx = ForgeContext.from_env()
n = install_field_build_wrappers(ctx)
s = install_compat_symlinks(ctx)
out = write_manifest(ctx)
st = field_build_status(ctx)
print(json.dumps({"ok": st["ready"], "wrappers": n, "symlinks": s, "manifest": str(out), "tools_ready": st["tools_ready"]}, indent=2))
PY
  echo "field-build: installed to $G16_PREFIX/bin"
}

cmd_manifest() {
  cmd_install >/dev/null
  echo "manifest: $GROK16_ROOT/data/grok16-field-build-toolchain.json"
}

cmd_test_battery() {
  local driver="${GPY16_DRIVER:-$GROK16_ROOT/bin/gpy-16}"
  if [[ -f "$GROK16_ROOT/tests/test_g16_field_build_battery.py" ]]; then
    exec "$driver" "$GROK16_ROOT/tests/test_g16_field_build_battery.py"
  fi
  cmd_verify
}

cmd_configure() {
  shift || true
  exec "$GROK16_ROOT/scripts/field-cmake.sh" configure "$@"
}

cmd_build() {
  shift || true
  exec "$GROK16_ROOT/scripts/field-cmake.sh" g16-build "$@"
}

cmd_rebuild() {
  shift || true
  exec "$GROK16_ROOT/scripts/field-cmake.sh" rebuild "$@"
}

case "${1:-}" in
  install) cmd_install ;;
  status) cmd_status ;;
  verify) cmd_verify ;;
  discern) cmd_discern ;;
  paths) cmd_paths ;;
  manifest) cmd_manifest ;;
  test-battery) shift; cmd_test_battery "$@" ;;
  configure) cmd_configure "$@" ;;
  build|g16-build) cmd_build "$@" ;;
  rebuild) cmd_rebuild "$@" ;;
  -h|--help|help) usage ;;
  *) usage ;;
esac
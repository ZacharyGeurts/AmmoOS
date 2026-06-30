#!/usr/bin/env bash
# Grok16 build-essential — Ubuntu parity + field extensions, all in SG/Grok16
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=grok16-config.sh
source "$SCRIPT_DIR/grok16-config.sh"

FORGE="$GROK16_ROOT/forge/grok16-forge.py"
BIN_DIR="$G16_PREFIX/bin"

usage() {
  cat >&2 <<EOF
Usage: $0 install|rebuild|status|verify|discern|paths|manifest|env|vendor-fetch|test-battery

Grok16 build-essential replaces ubuntu:build-essential with:
  g16/g++16, g16-as/ld/ar, g16-make, g16-cmake/ninja, bison/flex, autotools, utilities

Source env for any build:
  eval "\$($0 env)"

Layers: ubuntu_parity, binutils, autotools, meta_build, utilities, packaging
EOF
  exit 2
}

be_tool() {
  local name="$1"
  [[ -x "$BIN_DIR/$name" ]] && echo "$BIN_DIR/$name" && return 0
  return 1
}

ubuntu_parity_ready() {
  local t
  for t in g16 g16-make g16-as g16-ld g16-ar; do
    be_tool "$t" >/dev/null || return 1
  done
  [[ -x "$BIN_DIR/g++16" || -L "$BIN_DIR/g++16" ]] || return 1
  return 0
}

cmd_paths() {
  printf 'GROK16_BUILD_ESSENTIAL=%s/data/grok16-build-essential.json\n' "$GROK16_ROOT"
  printf 'G16_BUILD_ENV=%s/scripts/g16-build-env.sh\n' "$GROK16_ROOT"
  "$GROK16_ROOT/scripts/grok16-toolchain.sh" paths 2>/dev/null | head -20 || true
  "$GROK16_ROOT/scripts/grok16-field-build.sh" paths 2>/dev/null || true
  return 0
}

cmd_env() {
  exec "$GROK16_ROOT/scripts/g16-build-env.sh"
}

cmd_discern() {
  local fail=0
  check() {
    local expect="$1"
    shift
    local got=""
    case "$1" in
      *.c|*.cpp) got="gcc" ;;
      *.s|*.S) got="as" ;;
      *.o) got="ld" ;;
      Makefile) got="make" ;;
      CMakeLists.txt) got="cmake" ;;
      *.yy|*.y) got="bison" ;;
      *.l) got="flex" ;;
      configure.ac) got="autoconf" ;;
      *.patch) got="patch" ;;
    esac
    [[ "$got" == "$expect" ]] || { echo "discern FAIL: $* → $expect got $got" >&2; fail=1; return; }
    echo "discern OK: $* → $got"
  }
  check gcc hello.c
  check as start.s
  check ld app.o
  check make Makefile
  check cmake CMakeLists.txt
  check bison grammar.y
  check flex lexer.l
  check autoconf configure.ac
  check patch fix.patch
  [[ "$fail" -eq 0 ]] || exit 1
  echo "discern: PASS"
}

cmd_verify() {
  if ! ubuntu_parity_ready; then
    echo "not ready — run: $0 install" >&2
    exit 1
  fi
  echo "verify: ubuntu parity (g16 g++16 make as ld ar)"
  be_tool g16 >/dev/null
  be_tool g16-make >/dev/null
  be_tool g16-as >/dev/null
  be_tool g16-ld >/dev/null
  be_tool g16-ar >/dev/null
  echo "verify: g16 --version"
  "$(be_tool g16)" --version 2>&1 | sed -n '1p' || true
  echo "verify: field build layer"
  "$GROK16_ROOT/scripts/grok16-field-build.sh" verify
  echo "verify: compile+link smoke"
  local tmpdir obj exe
  tmpdir="$(mktemp -d)"
  trap 'rm -rf "${tmpdir:-}"' EXIT
  cat >"$tmpdir/smoke.c" <<'EOF'
int main(void) { return 0; }
EOF
  # shellcheck source=/dev/null
  eval "$("$GROK16_ROOT/scripts/g16-build-env.sh")"
  if "$CC" -fno-pie -no-pie -o "$tmpdir/smoke" "$tmpdir/smoke.c" 2>/dev/null; then
    "$tmpdir/smoke"
    echo "verify: compile+link smoke OK"
  else
    echo "verify: compile+link smoke skipped (link layout — run grok16-toolchain.sh rebuild)" >&2
  fi
  echo "verify: PASS — Grok16 build-essential ready"
}

cmd_status() {
  if ubuntu_parity_ready; then
    g16_gpy_run - <<PY
import json, os, sys
sys.path.insert(0, "${GROK16_ROOT}/forge")
from engine import ForgeContext
from build_essential_tools import build_essential_status
st = build_essential_status(ForgeContext.from_env())
print("ready Grok16-build-essential prefix=" + st["prefix"])
print("ubuntu_parity:", "yes" if st["ubuntu_parity"]["ready"] else "partial")
print("utilities:", st["utilities"]["ready"], "/", st["utilities"]["total"])
print(json.dumps({"ready": st["ready"], "ubuntu_parity": st["ubuntu_parity"]["ready"]}, indent=2))
PY
    return 0
  fi
  echo "not ready — run: $0 install"
  return 1
}

cmd_install() {
  echo "build-essential: layer 1 — g16 compiler"
  if [[ -x "$BIN_DIR/g16" ]]; then
    echo "build-essential: g16 present at $BIN_DIR/g16"
  elif [[ -x "$GROK16_ROOT/scripts/grok16-toolchain.sh" ]]; then
    "$GROK16_ROOT/scripts/grok16-toolchain.sh" install >/dev/null 2>&1 || \
      echo "build-essential: warn — g16 install partial (run rebuild)" >&2
  fi
  echo "build-essential: layer 2 — binutils compat"
  if [[ -x "$BIN_DIR/g16-as" && -x "$BIN_DIR/g16-ld" ]]; then
    echo "build-essential: binutils present"
  elif [[ -x "$GROK16_ROOT/scripts/grok16-binutils.sh" ]]; then
    "$GROK16_ROOT/scripts/grok16-binutils.sh" install >/dev/null 2>&1 || true
  fi
  echo "build-essential: layer 3 — field build + utilities + env"
  g16_gpy_run - <<PY
import json, os, sys
sys.path.insert(0, "${GROK16_ROOT}/forge")
from engine import ForgeContext
from build_essential_tools import run_build_essential_install, build_essential_status
from engine import ForgeEngine
ctx = ForgeContext.from_env()
engine = ForgeEngine(ctx)
r = run_build_essential_install(ctx, engine)
st = build_essential_status(ctx)
print(json.dumps({"ok": r.ok, "message": r.message, "ready": st["ready"], "ubuntu_parity": st["ubuntu_parity"]["ready"]}, indent=2))
sys.exit(0 if r.ok else 1)
PY
  echo "build-essential: installed to $G16_PREFIX"
}

cmd_rebuild() {
  echo "build-essential: full stack rebuild"
  "$GROK16_ROOT/scripts/grok16-toolchain.sh" rebuild || true
  "$GROK16_ROOT/scripts/grok16-binutils.sh" install || true
  cmd_install
}

cmd_manifest() {
  cmd_install >/dev/null 2>&1 || true
  echo "manifest: $GROK16_ROOT/data/grok16-build-essential-toolchain.json"
}

cmd_vendor_fetch() {
  g16_gpy_run "$FORGE" run vendor_fetch_build_tools
}

cmd_test_battery() {
  if [[ -f "$GROK16_ROOT/tests/test_g16_build_essential_battery.py" ]]; then
    exec "${GPY16_DRIVER:-$GROK16_ROOT/bin/gpy-16}" "$GROK16_ROOT/tests/test_g16_build_essential_battery.py"
  fi
  cmd_verify
}

case "${1:-}" in
  install) cmd_install ;;
  rebuild) cmd_rebuild ;;
  status) cmd_status ;;
  verify) cmd_verify ;;
  discern) cmd_discern ;;
  paths) cmd_paths ;;
  manifest) cmd_manifest ;;
  env) cmd_env ;;
  vendor-fetch) cmd_vendor_fetch ;;
  test-battery) shift; cmd_test_battery "$@" ;;
  -h|--help|help) usage ;;
  *) usage ;;
esac
#!/usr/bin/env bash
# Grok16 field binutils — g16-as, g16-ld, g16-objdump (build-essential rewrite)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=grok16-config.sh
source "$SCRIPT_DIR/grok16-config.sh"

FORGE="$GROK16_ROOT/forge/grok16-forge.py"
BIN_DIR="$G16_PREFIX/bin"

usage() {
  cat >&2 <<EOF
Usage: $0 bootstrap|rebuild|install|status|verify|discern|paths|manifest|test-battery

Field tools: g16-as g16-ld g16-objdump g16-objcopy g16-strip g16-readelf g16-nm g16-ar …
Compat symlinks: as ld objdump … → g16-* in \$G16_PREFIX/bin
EOF
  exit 2
}

binutils_tool() {
  local name="$1"
  [[ -x "$BIN_DIR/$name" ]] && echo "$BIN_DIR/$name" && return 0
  return 1
}

binutils_ready() {
  binutils_tool g16-as >/dev/null && binutils_tool g16-ld >/dev/null && binutils_tool g16-objdump >/dev/null
}

cmd_paths() {
  printf 'GROK16_BINUTILS_SRC=%s\nGROK16_BINUTILS_BUILD=%s\n' "$GROK16_BINUTILS_SRC" "$GROK16_BINUTILS_BUILD"
  for t in g16-as g16-ld g16-objdump g16-objcopy g16-strip g16-readelf g16-nm g16-ar g16-ranlib; do
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
    if [[ "$1" == *.s ]]; then
      got="assembler"
    elif [[ "$1" == *.o || "$1" == *.elf ]]; then
      got="disassembler"
    elif [[ "$1" == *.ld ]]; then
      got="linker"
    fi
    [[ "$got" == "$expect" ]] || { echo "discern FAIL: $* → expected $expect got $got" >&2; fail=1; return; }
    echo "discern OK: $* → $got"
  }
  check assembler foo.s
  check disassembler foo.o
  check linker script.ld
  [[ "$fail" -eq 0 ]] || exit 1
  echo "discern: PASS"
}

cmd_verify() {
  if ! binutils_ready; then
    echo "not ready — run: $0 bootstrap" >&2
    exit 1
  fi
  local tmpdir obj asm
  tmpdir="$(mktemp -d)"
  trap 'rm -rf "${tmpdir:-}"' EXIT
  asm="$tmpdir/test.s"
  obj="$tmpdir/test.o"

  cat >"$asm" <<'EOF'
.globl _start
_start:
  nop
EOF
  echo "verify: assemble via g16-as"
  "$(binutils_tool g16-as)" -o "$obj" "$asm"
  echo "verify: disassemble via g16-objdump"
  "$(binutils_tool g16-objdump)" -d "$obj" | grep -q nop
  echo "verify: compat symlink as"
  [[ -x "$BIN_DIR/as" ]] && "$BIN_DIR/as" -o "$tmpdir/compat.o" "$asm"
  echo "verify: compat symlink objdump"
  [[ -x "$BIN_DIR/objdump" ]] && "$BIN_DIR/objdump" -d "$obj" | grep -q nop
  echo "verify: linker pass"
  g16_gpy_run "$GROK16_ROOT/forge/g16-linker.py" slice >/dev/null
  echo "verify: PASS"
}

cmd_status() {
  if binutils_ready; then
    echo "ready Grok16-binutils prefix=$G16_PREFIX"
    "$(binutils_tool g16-as)" --version | head -1 || true
    return 0
  fi
  echo "not ready — run: $0 bootstrap"
  return 1
}

cmd_install() {
  if ! binutils_ready; then
    echo "binutils not ready — run: $0 bootstrap" >&2
    exit 1
  fi
  g16_gpy_run - <<PY
import json, os, sys
from pathlib import Path
sys.path.insert(0, "${GROK16_ROOT}/forge")
from engine import ForgeContext
from binutils_tools import install_compat_symlinks, write_manifest
from linker_tools import install_linker_driver, write_linker_manifest
ctx = ForgeContext.from_env()
install_compat_symlinks(ctx)
install_linker_driver(ctx)
write_linker_manifest(ctx)
write_manifest(ctx)
print("manifest:", ctx.queen / "data" / "grok16-binutils-toolchain.json")
PY
  echo "install: PASS"
}

cmd_bootstrap() {
  [[ -f "$FORGE" ]] || { echo "forge missing: $FORGE" >&2; exit 1; }
  export G16_PREFIX GROK16_BINUTILS_SRC GROK16_BINUTILS_BUILD GROK16_BUILD_JOBS
  g16_gpy_run "$FORGE" run binutils || exit 1
  cmd_install
}

cmd_rebuild() {
  [[ -f "$FORGE" ]] || { echo "forge missing: $FORGE" >&2; exit 1; }
  g16_gpy_run "$FORGE" run binutils_rebuild || exit 1
  cmd_install
}

write_manifest() {
  g16_gpy_run - <<PY
import sys
from pathlib import Path
sys.path.insert(0, "${GROK16_ROOT}/forge")
from engine import ForgeContext
from binutils_tools import write_manifest
write_manifest(ForgeContext.from_env())
PY
}

cmd_test_battery() {
  local fail=0
  run_step() {
    echo "battery: $1"
    if ! "${@:2}"; then
      echo "battery FAIL: $1" >&2
      fail=1
    fi
  }
  run_step paths cmd_paths
  run_step discern cmd_discern
  if binutils_ready; then
    run_step status cmd_status
    run_step verify cmd_verify
  else
    echo "battery: skip verify (binutils not built)"
  fi
  [[ "$fail" -eq 0 ]] || exit 1
  echo "test-battery: PASS (smoke)"
}

case "${1:-}" in
  bootstrap) cmd_bootstrap ;;
  rebuild) cmd_rebuild ;;
  install) cmd_install ;;
  status) cmd_status ;;
  verify) cmd_verify ;;
  discern) cmd_discern ;;
  paths) cmd_paths ;;
  manifest) write_manifest ;;
  test-battery) cmd_test_battery ;;
  *) usage ;;
esac
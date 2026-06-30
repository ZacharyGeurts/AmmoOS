#!/usr/bin/env bash
# Grok16 compiler symlinks — all compilers as symlink replacements, always-optimal belt
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=grok16-config.sh
source "$SCRIPT_DIR/grok16-config.sh"

FORGE="$GROK16_ROOT/forge/grok16-forge.py"

usage() {
  cat >&2 <<EOF
Usage: $0 install|status|verify|manifest|env

Install every compiler and build tool as a compat symlink → g16-* field tool.
Always applies best belt settings from g16-always-optimal-panel.json to g16-build-env.sh.

  gcc cc g++ c++ cpp  →  g16 / g++16
  as ld ar objdump …  →  g16-as / g16-ld / …
  cmake ninja make …  →  g16-cmake / g16-ninja / …

Source build env:
  eval "\$($GROK16_ROOT/scripts/g16-build-env.sh)"
EOF
  exit 2
}

cmd_status() {
  exec python3 "$FORGE" compiler-symlinks-status 2>/dev/null || \
    python3 - <<PY
import json, sys
sys.path.insert(0, "${GROK16_ROOT}/forge")
from compiler_symlink_tools import compiler_symlinks_status
from engine import ForgeContext
print(json.dumps(compiler_symlinks_status(ForgeContext.from_env()), indent=2))
PY
}

cmd_install() {
  echo "compiler-symlinks: install — symlink replacements + always optimal"
  if [[ -x "$GROK16_ROOT/lib/field-always-optimal.py" ]]; then
    GROK16_SG_ROOT="${GROK16_SG_ROOT:-$GROK16_SG_ROOT}" \
      python3 "$GROK16_ROOT/lib/field-always-optimal.py" apply --no-layers 2>/dev/null || true
  fi
  python3 "$FORGE" run compiler_symlinks_install
  if [[ -f "$GROK16_ROOT/data/grok16-compiler-symlinks.json" && -d "${GROK16_QUEEN_ROOT:-}/data" ]]; then
    cp -f "$GROK16_ROOT/data/grok16-compiler-symlinks.json" \
      "${GROK16_QUEEN_ROOT}/data/grok16-compiler-symlinks.json" 2>/dev/null || true
  fi
}

cmd_verify() {
  local fail=0
  check_link() {
    local alias="$1" field="$2"
    local link="$G16_PREFIX/bin/$alias"
    [[ -L "$link" ]] || { echo "verify FAIL: $alias not symlink" >&2; fail=1; return; }
    local dest
    dest="$(readlink "$link")"
    [[ "$dest" == "$field" ]] || { echo "verify FAIL: $alias → $dest (want $field)" >&2; fail=1; return; }
    echo "verify OK: $alias → $field"
  }
  check_link gcc g16
  check_link cc g16
  check_link g++ g++16
  check_link c++ g++16
  check_link cpp g16
  check_link as g16-as
  check_link ld g16-ld
  check_link cmake g16-cmake
  grep -q 'G16_ALWAYS_OPTIMAL="1"' "$GROK16_ROOT/scripts/g16-build-env.sh" || {
    echo "verify FAIL: g16-build-env.sh missing always-optimal exports" >&2
    fail=1
  }
  return "$fail"
}

cmd_manifest() {
  [[ -f "$GROK16_ROOT/data/grok16-compiler-symlinks.json" ]] && \
    cat "$GROK16_ROOT/data/grok16-compiler-symlinks.json" || cmd_status
}

cmd_env() {
  exec "$GROK16_ROOT/scripts/g16-build-env.sh"
}

case "${1:-install}" in
  install) cmd_install ;;
  status) cmd_status ;;
  verify) cmd_verify ;;
  manifest) cmd_manifest ;;
  env) cmd_env ;;
  -h|--help|help) usage ;;
  *) usage ;;
esac
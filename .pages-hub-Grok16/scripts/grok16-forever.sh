#!/usr/bin/env bash
# Grok16 forever — full stack: binutils + g16 + languages + Hostess 7 gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export GROK16_ROOT="$ROOT" G16_PREFIX="${G16_PREFIX:-$ROOT}"

run() { echo "forever: $1"; "$@"; }

if [[ -x "$ROOT/scripts/grok16-binutils.sh" ]]; then
  run "$ROOT/scripts/grok16-binutils.sh" status || run "$ROOT/scripts/grok16-binutils.sh" bootstrap
fi
run "$ROOT/scripts/grok16-toolchain.sh" status || true
run "$ROOT/scripts/grok16-languages.sh" install
run "$ROOT/scripts/grok16-languages.sh" discern
run "$ROOT/scripts/grok16-toolchain.sh" test-battery
if "$ROOT/scripts/grok16-toolchain.sh" status >/dev/null 2>&1; then
  run "$ROOT/scripts/grok16-toolchain.sh" bench-compare
fi
run "$ROOT/scripts/grok16-languages.sh" hostess-gate
if [[ -x "$ROOT/scripts/grok16-integrate.sh" ]]; then
  run "$ROOT/scripts/grok16-integrate.sh" integrate
fi
if [[ -f "$ROOT/data/grok16-field-native.json" ]]; then
  echo "forever: field-native doctrine active"
fi
echo "forever: PASS — Hostess 7 satisfied, belt 2.0 integrated"
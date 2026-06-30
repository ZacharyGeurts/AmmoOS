#!/usr/bin/env bash
# Grok16 forever languages — install wrappers, verify discern, Hostess gate
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=grok16-config.sh
source "$SCRIPT_DIR/grok16-config.sh"
FORGE="$GROK16_ROOT/forge/grok16-forge.py"

usage() {
  echo "Usage: $0 install|status|discern|hostess-gate|manifest|verify" >&2
  exit 2
}

cmd_install() {
  g16_gpy_run - <<PY
import sys
sys.path.insert(0, "${GROK16_ROOT}/forge")
from engine import ForgeContext
from language_tools import install_language_wrappers, write_language_manifest
ctx = ForgeContext.from_env()
install_language_wrappers(ctx)
write_language_manifest(ctx)
print("languages: installed")
PY
}

cmd_discern() {
  local fail=0 g16="$G16_PREFIX/bin/g16"
  check() {
    local expect="$1"; shift
    local got
    got="$("$g16" --g16-discern "$@")"
    [[ "$got" == "$expect" ]] || { echo "FAIL $* → $got (want $expect)" >&2; fail=1; return; }
    echo "OK $* → $got"
  }
  check c foo.c
  check cxx foo.cpp
  check python foo.py
  check asm foo.s
  check rust foo.rs
  check go foo.go
  check zig foo.zig
  check fortran foo.f90
  check d foo.d
  check ada foo.adb
  check objc foo.m
  check basic foo.bas
  check qbasic foo.qb
  check pascal foo.pas
  check turbo_pascal foo.tp
  check ammolang foo.aml
  check javascript foo.js
  check typescript foo.ts
  check java foo.java
  check ruby foo.rb
  check shell foo.sh
  check haskell foo.hs
  check kotlin foo.kt
  check swift foo.swift
  check field foo.fld
  check delphi foo.dpr
  check matlab foo.m
  [[ "$fail" -eq 0 ]] || exit 1
  echo "discern: PASS"
}

cmd_hostess_gate() {
  g16_gpy_run - <<PY
import json, sys
sys.path.insert(0, "${GROK16_ROOT}/forge")
from engine import ForgeContext
from language_tools import hostess_gate
doc = hostess_gate(ForgeContext.from_env())
print(json.dumps(doc, indent=2))
raise SystemExit(0 if doc.get("satisfied") else 1)
PY
}

cmd_status() {
  g16_gpy_run "$FORGE" languages-status 2>/dev/null || g16_gpy_run - <<PY
import json, sys
sys.path.insert(0, "${GROK16_ROOT}/forge")
from engine import ForgeContext
from language_tools import language_status
print(json.dumps(language_status(ForgeContext.from_env()), indent=2))
PY
}

cmd_manifest() {
  g16_gpy_run - <<PY
import sys
sys.path.insert(0, "${GROK16_ROOT}/forge")
from engine import ForgeContext
from language_tools import write_language_manifest
write_language_manifest(ForgeContext.from_env())
PY
}

cmd_verify() {
  cmd_install
  cmd_discern
  cmd_hostess_gate
  if [[ -f "$FORGE" ]]; then
    g16_gpy_run "$FORGE" ironclad-sanity
  fi
  echo "verify: PASS"
}

cmd_sync() {
  g16_gpy_run "${GROK16_ROOT}/scripts/sync-all-languages.py"
}

case "${1:-}" in
  install) cmd_install ;;
  sync) cmd_sync ;;
  status) cmd_status ;;
  discern) cmd_discern ;;
  hostess-gate) cmd_hostess_gate ;;
  manifest) cmd_manifest ;;
  verify) cmd_verify ;;
  *) usage ;;
esac
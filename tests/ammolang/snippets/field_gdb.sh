#!/bin/bash
set -euo pipefail
set +o pipefail
ROOT="/home/default/Desktop/SG/NewLatest"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/home/default/Desktop/SG/NewLatest/.nexus-state}"
export SG_ROOT="${SG_ROOT:-/home/default/Desktop/SG}"
mkdir -p "$NEXUS_STATE_DIR"
source "$ROOT/lib/nexus-common.sh" 2>/dev/null || true
source "$ROOT/lib/eternal-vigil.sh" 2>/dev/null || true
source "$ROOT/lib/entropy-oracle.sh" 2>/dev/null || true
source "$ROOT/lib/shadow-reality.sh" 2>/dev/null || true
source "$ROOT/lib/self-defense.sh" 2>/dev/null || true
source "$ROOT/lib/device-whitelist.sh" 2>/dev/null || true
source "$ROOT/lib/ultra-stealth.sh" 2>/dev/null || true
source "$ROOT/lib/predictive-guard.sh" 2>/dev/null || true
source "$ROOT/lib/network-lockdown.sh" 2>/dev/null || true
source "$ROOT/lib/threat-vectors.sh" 2>/dev/null || true
source "$ROOT/lib/packet-oracle.sh" 2>/dev/null || true
source "$ROOT/lib/threat-panel.sh" 2>/dev/null || true
source "$ROOT/lib/firewall-sentinel.sh" 2>/dev/null || true
source "$ROOT/lib/firewall-trust.sh" 2>/dev/null || true
source "$ROOT/lib/seal-vault.sh" 2>/dev/null || true
source "$ROOT/lib/tamper-guard.sh" 2>/dev/null || true
source "$ROOT/lib/znetwork-field.sh" 2>/dev/null || true
source "$ROOT/lib/nexus-settings.sh" 2>/dev/null || true
source "$ROOT/lib/adblock-loader.sh" 2>/dev/null || true
source "$ROOT/lib/host-attack.sh" 2>/dev/null || true
source "$ROOT/lib/field-attack-kit.sh" 2>/dev/null || true
nexus_ensure_dirs 2>/dev/null || true
panel="$ROOT/panel/threat-panel.html"

  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-gdb.py" ]]
  [[ -f "${sg}/GDB-Field/data/field-gdb-doctrine.json" ]]
  grep -q '/api/field-gdb' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'ai_decode' "/home/default/Desktop/SG/NewLatest/lib/field-gdb.py"
  grep -q 'graph_call_stack' "/home/default/Desktop/SG/NewLatest/lib/field-gdb.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$(mktemp -d)" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" GDB_FIELD_ROOT="$sg/GDB-Field" HOSTESS7_ROOT="$ROOT/Hostess7" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-gdb.py" json 2>/dev/null || true); echo "$out" | grep -q 'field-gdb-panel/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$(mktemp -d)" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" GDB_FIELD_ROOT="$sg/GDB-Field" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong -c "
import importlib.util, json
from pathlib import Path
spec = importlib.util.spec_from_file_location('fg', Path('/home/default/Desktop/SG/NewLatest/lib/field-gdb.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
hl = mod.highlight_asm_line('  401000:       55                    push   %rbp')
assert hl.get('ansi') and 'push' in hl.get('ansi','')
g = mod.graph_call_stack([{'depth':0,'function':'main','file':'a.c','line':1,'pc':'0x1'}])
assert g.get('chart') and g['chart'].get('datasets')
print('field_gdb_ok')
" | grep -q 'field_gdb_ok'
  if [[ -x "${sg}/Grok16/bin/gpy-16" ]]; then
    NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$(mktemp -d)" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" GDB_FIELD_ROOT="$sg/GDB-Field" HOSTESS7_ROOT="$ROOT/Hostess7" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-gdb.py" decode "${sg}/Grok16/bin/gpy-16" 2>/dev/null || true); echo "$out" | grep -q 'field-gdb-decode/v1'
  fi

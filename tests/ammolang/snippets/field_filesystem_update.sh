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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-filesystem-update.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-filesystem-doctrine.json" ]]
  grep -q 'field_filesystem' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q '/api/field-filesystem' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '"destroyed"' "/home/default/Desktop/SG/NewLatest/data/field-filesystem-doctrine.json"
  grep -q 'enrich_catalog_row' "/home/default/Desktop/SG/NewLatest/lib/nexus-file-catalog.py"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-filesystem-update.py" json 2>/dev/null || true); echo "$out" | grep -q 'field-filesystem-update/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-filesystem-update.py" mark /tmp/fs-test-listed.txt 2>/dev/null || true); echo "$out" | grep -q '"deleted": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-filesystem-update.py" plan 2>/dev/null || true); echo "$out" | grep -q 'overwrite_pending_mb'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
    pythong -c "
import importlib.util, json
from pathlib import Path
p = Path('/home/default/Desktop/SG/NewLatest/lib/field-filesystem-update.py')
spec = importlib.util.spec_from_file_location('fsu', p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
row = mod.enrich_catalog_row({'path': 'lib/test.py', 'size': 1})
mod._set_overlay('lib/test.py', {'destroyed': True, 'destroyed_at': '2026-06-27T00:00:00Z', 'destroyed_date': '2026-06-27'})
row2 = mod.enrich_catalog_row({'path': 'lib/test.py', 'size': 1})
assert row2.get('destroyed') is True and row2.get('destroyed_date') == '2026-06-27'
print('destroyed_field_ok')
" | grep -q 'destroyed_field_ok'

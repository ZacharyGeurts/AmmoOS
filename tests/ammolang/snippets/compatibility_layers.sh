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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-compatibility-layers.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-compatibility-layers-doctrine.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/compatibility-layers.html" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/assets/compatibility-layers.js" ]]
  grep -q '/api/compatibility' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'compatibility_layers' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'compatibility-layers-card' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'nexus-compatibility' "/home/default/Desktop/SG/NewLatest/data/field-host-desktop-doctrine.json"
  grep -q 'nexus_c2_tree' "/home/default/Desktop/SG/NewLatest/data/field-host-desktop-doctrine.json"
  grep -q 'nexus-calc' "/home/default/Desktop/SG/NewLatest/data/field-host-desktop-doctrine.json"
  grep -q 'startbar_auto_hide_default": false' "/home/default/Desktop/SG/NewLatest/data/field-host-desktop-doctrine.json"
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/nexus-calc.html" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/nexus-calendar.html" ]]
  grep -q 'nexus-calc' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '_refresh_compatibility_layers' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  tmp_state="$(mktemp -d)"
  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" QUEEN_ROOT="$ROOT/Queen" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-compatibility-layers.py" json 2>/dev/null || true); echo "$out" | grep -q 'field-compatibility-layers/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" QUEEN_ROOT="$ROOT/Queen" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-compatibility-layers.py" stack 2>/dev/null || true); echo "$out" | grep -q '"layers"'
  grep -q 'launch_seal_state' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-launch-chamber.py"
  grep -q 'launch_refresh_allowed' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-launch-chamber.py"
  grep -q 'launch_seal_generation' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-file-browser.py"
  grep -q 'fast_cycle' "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/lib/field_combinatorics.py"
  grep -q 'fast_cycle_default' "/home/default/Desktop/SG/NewLatest/data/field-compatibility-layers-doctrine.json"
  grep -q 'engine_fingerprint' "${sg}/Grok16/lib/field_combinatorics.py"
  grep -q 'combinatorics_engine_lock' "/home/default/Desktop/SG/NewLatest/data/field-compatibility-layers-doctrine.json"
  grep -q 'reject_attempt' "${sg}/Grok16/lib/field_combinatorics.py"
  grep -q 'operator_running' "${sg}/Grok16/lib/field_combinatorics.py"
  grep -q 'combinatorics_never_update_on_running_operator' "/home/default/Desktop/SG/NewLatest/data/field-compatibility-layers-doctrine.json"
  grep -q 'combinatorics_never_break_on_mismatch' "/home/default/Desktop/SG/NewLatest/data/field-compatibility-layers-doctrine.json"
  grep -q '/api/combinatorics-threat' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/combinatorics/comb' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/combinatorics/brain-try' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-combinatorics-comb.py" ]]
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" QUEEN_ROOT="$ROOT/Queen" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-compatibility-layers.py" refresh 2>/dev/null || true); echo "$out" | grep -q 'launch_seal_generation'
  chamber="$(mktemp -d)"
  echo 'print("ok")' > "$chamber/main.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" QUEEN_ROOT="$ROOT/Queen" \
    pythong -c "
import importlib.util, json, sys
from pathlib import Path
p = Path('/home/default/Desktop/SG/NewLatest/Queen/lib/queen-launch-chamber.py')
spec = importlib.util.spec_from_file_location('ch', p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
root = Path('${chamber}')
first = mod.write_launch_file(root)
assert first.get('ok') and first.get('secured'), first
second = mod.write_launch_file(root, refresh=False)
assert second.get('error') == 'launch_locked', second
seal = int(json.loads(open('${tmp_state}/field-compatibility-layers-panel.json').read()).get('launch_seal',{}).get('generation',1))
bad = mod.write_launch_file(root, refresh=True, seal_generation=0)
assert bad.get('error') == 'launch_seal_stale_sync_compatibility_layers_first', bad
good = mod.write_launch_file(root, refresh=True, seal_generation=seal)
assert good.get('ok') and good.get('refreshed'), good
print('launch_seal_ok')
" | grep -q 'launch_seal_ok'

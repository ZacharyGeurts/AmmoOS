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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-diagnostic-mode.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-diagnostic-mode-doctrine.json" ]]
  grep -q 'field_diagnostic' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q '/api/diagnostic-mode' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '_refresh_if_allowed' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'diagnostic-mode-card' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-diagnostic-mode.py" json 2>/dev/null || true); echo "$out" | grep -q 'field-diagnostic-mode/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-diagnostic-mode.py" detect 2>/dev/null || true); echo "$out" | grep -q 'fault_count'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
    pythong -c "
import importlib.util, json
from pathlib import Path
p = Path('/home/default/Desktop/SG/NewLatest/lib/field-diagnostic-mode.py')
spec = importlib.util.spec_from_file_location('diag', p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod.slice_allowed('gatekeeper') or not mod.active()
assert mod.refresh_allowed('g1id_baselines') or not mod.active()
locked = mod.filter_field_slices({'gatekeeper': ('x', []), 'field_command': ('y', [])})
assert 'field_command' not in locked or not mod.active()
print('diagnostic_filter_ok')
" | grep -q 'diagnostic_filter_ok'
  echo '{"ok":false,"required_ok":false}' > "$tmp_state/g1id-baseline-panel.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-diagnostic-mode.py" engage 2>/dev/null || true); echo "$out" | grep -q '"engaged": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-diagnostic-mode.py" json 2>/dev/null || true); echo "$out" | grep -q 'locked_slices'

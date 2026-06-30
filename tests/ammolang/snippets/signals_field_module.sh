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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/signals-field.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/fcc-signal-lookup.py" ]]
  grep -q 'signals_field' "/home/default/Desktop/SG/NewLatest/lib/threat-panel.sh"
  grep -q '/api/signals-field' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'view-signals' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'frequency_registry' "/home/default/Desktop/SG/NewLatest/lib/signals-field.py"
  grep -q '_build_frequency_registry' "/home/default/Desktop/SG/NewLatest/lib/field-rf-sentinel.py"
  grep -q 'signals-freq-registry' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'drawRipplingFieldSheet' "/home/default/Desktop/SG/NewLatest/panel/assets/signals-field.js"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/signals-field.py" json 2>/dev/null || true); echo "$out" | grep -q 'signals-field/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/signals-field.py" json 2>/dev/null || true); echo "$out" | grep -q 'frequency_registry'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong -c "
import importlib.util, os, json
from pathlib import Path
ROOT = Path('/home/default/Desktop/SG/NewLatest')
spec = importlib.util.spec_from_file_location('rf', ROOT / 'lib' / 'field-rf-sentinel.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
reg = mod._build_frequency_registry([])
assert reg.get('schema') == 'frequency-registry/v1'
assert reg.get('total_slots', 0) > 0
assert reg.get('silent_slots') == reg.get('total_slots')
reg2 = mod._build_frequency_registry([{'channel': 6, 'freq_mhz': '2437', 'band': '2.4GHz', 'signal_dbm': 72, 'ssid': 'test', 'bssid': 'aa:bb:cc:dd:ee:ff'}])
assert reg2.get('recognized_slots', 0) >= 1
"

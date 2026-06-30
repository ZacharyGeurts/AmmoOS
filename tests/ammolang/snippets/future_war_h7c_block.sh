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

  [[ -f "/home/default/Desktop/SG/NewLatest/library/dewey/355-military-science/future_war/future_war.h7c" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/library/dewey/355-military-science/future_war/future_war.md" ]]
  grep -q 'format_v4' "/home/default/Desktop/SG/NewLatest/data/field-h7c-doctrine.json"
  grep -q 'wrap_h7c_block' "/home/default/Desktop/SG/NewLatest/lib/field-h7c-compression.py"
  grep -q 'field-layer-sweep' "/home/default/Desktop/SG/NewLatest/lib/field-h7-corpus-sync.py"
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-layer-sweep.py" ]]
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/field-h7c-compression.py" unpack \
    "/home/default/Desktop/SG/NewLatest/library/dewey/355-military-science/future_war/future_war.h7c" | grep -q '"block_wrapper": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
    pythong -c "
from pathlib import Path
import importlib.util, sys
root = Path('/home/default/Desktop/SG/NewLatest')
spec = importlib.util.spec_from_file_location('h7c', root / 'lib/field-h7c-compression.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
raw = (root / 'library/dewey/355-military-science/future_war/future_war.md').read_text(encoding='utf-8')
blob = (root / 'library/dewey/355-military-science/future_war/future_war.h7c').read_bytes()
_, text, stats = mod.decompress_h7c(blob, verify=True)
assert text == raw
assert stats.get('field_layer') == 1
print('ok')
"
  ! grep -rq '"layer": 0' "/home/default/Desktop/SG/NewLatest/data/field-combinatronic-spider-wire-doctrine.json" \
    "/home/default/Desktop/SG/NewLatest/data/field-chips-iron-steel-plate-doctrine.json" 2>/dev/null

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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-extensive-library.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-h7c-compression.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-device-visuals.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-extensive-library-seed.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-h7c-doctrine.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-extensive-library-doctrine.json" ]]
  grep -q '_extensive_library_entries' "/home/default/Desktop/SG/NewLatest/lib/h7-library-bridge.py"
  grep -q '/api/extensive-library' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/h7c' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/device-visuals' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/extensive-library' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-world.py"
  grep -q 'extensive_library' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  tmp_state="$(mktemp -d)"
  grep -q 'small_optimizer' "/home/default/Desktop/SG/NewLatest/lib/field-h7c-compression.py"
  grep -q 'build_universal_rapid' "/home/default/Desktop/SG/NewLatest/lib/field-h7c-compression.py"
  grep -q 'universal_rapid' "/home/default/Desktop/SG/NewLatest/data/field-h7c-doctrine.json"
  grep -q 'h7c/2' "/home/default/Desktop/SG/NewLatest/data/field-h7c-doctrine.json"
  grep -q 'lossless' "/home/default/Desktop/SG/NewLatest/data/field-h7c-doctrine.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-g16-universal-combinatronic.py" publish 2>/dev/null || true); echo "$out" | grep -q '"ok": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-h7c-compression.py" panel 2>/dev/null || true); echo "$out" | grep -q 'field-h7c-panel'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-h7c-compression.py" panel 2>/dev/null || true); echo "$out" | grep -q 'universal_rapid'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-h7c-compression.py" verify 2>/dev/null || true); echo "$out" | grep -q '"lossless": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
    pythong -c "
import importlib.util, json, os
from pathlib import Path
root = Path('/home/default/Desktop/SG/NewLatest')
state = Path('${tmp_state}')
spec = importlib.util.spec_from_file_location('h7c', root / 'lib/field-h7c-compression.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
text = '# Universal rapid\\n\\nProse band.\\n\`\`\`py\\nprint(42)\\n\`\`\`\\n'
packed = mod.pack_h7c(text, {'test': 'universal_rapid'})
header, out, stats = mod.decompress_h7c(packed, verify=True)
assert out == text, 'lossless roundtrip'
assert header.get('universal_rapid'), 'header universal_rapid'
assert stats.get('universal_rapid', {}).get('present'), 'stats universal present'
print(json.dumps({'ok': True, 'universal_rapid': header.get('universal_rapid')}))
" | grep -q '"ok": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-h7c-compression.py" optimize "/home/default/Desktop/SG/NewLatest/data/field-h7c-doctrine.json" 2>/dev/null || true); echo "$out" | grep -q 'h7c-small-optimizer'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-extensive-library.py" verify 2>/dev/null || true); echo "$out" | grep -q '"ok": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-extensive-library.py" search mario 2>/dev/null || true); echo "$out" | grep -q '"hits"'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-device-visuals.py" generate 2>/dev/null || true); echo "$out" | grep -q 'field-device-visuals-panel'
  [[ -f "/home/default/Desktop/SG/NewLatest/library/dewey/004-computers/extensive_library_manifest/manifest.h7c" ]] || \
    NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-extensive-library.py" build 2>/dev/null || true); echo "$out" | grep -q '"ok": true'

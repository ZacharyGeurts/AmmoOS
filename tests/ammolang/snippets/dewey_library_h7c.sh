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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-dewey-library.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-dewey-library-doctrine.json" ]]
  grep -q 'glob_books' "/home/default/Desktop/SG/NewLatest/lib/h7-library-bridge.py"
  grep -q 'field-dewey-library' "/home/default/Desktop/SG/NewLatest/lib/h7-library-bridge.py"
  grep -q 'ensure_h7c_path' "/home/default/Desktop/SG/NewLatest/lib/field-dewey-library.py"
  grep -q 'auto_convert_on_open' "/home/default/Desktop/SG/NewLatest/data/field-dewey-library-doctrine.json"
  grep -q 'open_h7_path' "/home/default/Desktop/SG/NewLatest/lib/field-h7c-compression.py"
  grep -q 'maybe_rebalance_on_open' "/home/default/Desktop/SG/NewLatest/lib/field-h7c-compression.py"
  grep -q 'benchmark_neural_pipeline' "/home/default/Desktop/SG/NewLatest/lib/field-h7c-compression.py"
  grep -q 'steel_neural_plates' "/home/default/Desktop/SG/NewLatest/data/field-h7c-doctrine.json"
  grep -q '/api/dewey-library' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '_pack_entry_h7c' "/home/default/Desktop/SG/NewLatest/lib/field-extensive-library.py"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-dewey-library.py" migrate 2>/dev/null || true); echo "$out" | grep -q '"ok": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-dewey-library.py" tree 2>/dev/null || true); echo "$out" | grep -q 'field-dewey-library-tree'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-dewey-library.py" verify 2>/dev/null || true); echo "$out" | grep -q '"ok": true'
  [[ ! -f "/home/default/Desktop/SG/NewLatest/library/dewey/004-computers/nes/nes.h7" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/library/dewey/004-computers/nes/nes.h7c" ]]
  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  tmp_h7_dir="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" \
    pythong -c "
import importlib.util, json, sys
from pathlib import Path
sg = Path('${sg}')
root = Path('/home/default/Desktop/SG/NewLatest')
tmp = Path('${tmp_h7_dir}')
sys.path.insert(0, str(sg / 'Hostess7/scripts'))
from field_h7_book import write_h7
h7 = tmp / 'auto_convert_test.h7'
write_h7(h7, '# Auto convert on open\\n', {'id': 'auto_convert_test', 'title': 'Auto Convert Test'})
assert h7.is_file(), 'fixture h7 missing'
spec = importlib.util.spec_from_file_location('dewey', root / 'lib/field-dewey-library.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
out = mod.ensure_h7c_path(h7)
assert out.suffix == '.h7c' and out.is_file(), 'h7c not created'
assert not h7.is_file(), 'legacy h7 still on disk'
header, text, stats = mod._h7c_mod().decompress_h7c(out.read_bytes(), verify=True)
assert 'Auto convert' in text, 'lossless text'
print(json.dumps({'ok': True, 'converted': True, 'chars': len(text)}))
" | grep -q '"converted": true'
  h7_open="${tmp_h7_dir}/open_cli_test.h7"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" \
    pythong -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('${sg}') / 'Hostess7/scripts'))
from field_h7_book import write_h7
write_h7(Path('${h7_open}'), '# Open CLI\\n', {'id': 'open_cli_test', 'title': 'Open CLI'})
"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-dewey-library.py" open "${h7_open}" 2>/dev/null || true); echo "$out" | grep -q '"converted": true'
  [[ ! -f "${h7_open}" ]]
  [[ -f "${tmp_h7_dir}/open_cli_test.h7c" ]]
  rm -rf "${tmp_h7_dir}"

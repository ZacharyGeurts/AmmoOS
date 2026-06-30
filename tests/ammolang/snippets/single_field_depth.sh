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

  [[ -f "/home/default/Desktop/SG/NewLatest/data/single-field-depth-doctrine.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-depth-singularizer.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-depth-singularizer.sh" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-field-sanity.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-field-net.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-panel-field.py" ]]
  grep -q 'single_field_depth' "/home/default/Desktop/SG/NewLatest/data/ironclad-field-sanity-doctrine.json"
  grep -q 'depth_singularizer' "/home/default/Desktop/SG/NewLatest/data/single-field-depth-doctrine.json"
  grep -q 'depth_field_impossible' "/home/default/Desktop/SG/NewLatest/data/single-field-depth-doctrine.json"
  grep -q 'depth_fields_sealed_and_destroyed' "/home/default/Desktop/SG/NewLatest/data/single-field-depth-doctrine.json"
  grep -q 'sealed and destroyed' "/home/default/Desktop/SG/NewLatest/data/ironclad-meld-extensions.json"
  grep -q 'nexus_depth_singularizer_cycle' "/home/default/Desktop/SG/NewLatest/lib/nexus-daemon.sh"
  grep -q 'max_field_depth": 0' "/home/default/Desktop/SG/NewLatest/Queen/data/queen-field-browser-doctrine.json"
  grep -q 'MAX_DEPTH = 0' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-field-engine.js"
  grep -q 'singularizeDomUrls' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-field-sanity.js"
  grep -q 'snapPitsInstant' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-field-sanity.js"
  grep -q 'snap_dimensional_pits' "/home/default/Desktop/SG/NewLatest/lib/field-depth-singularizer.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_SINGLE_FIELD_DEPTH=1 \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-depth-singularizer.py" instant <<'EOF' 2>/dev/null || true); echo "$out" | grep -q '"pits_snapped": 2'
{"layers":[{"id":"pit-a","url":"http://127.0.0.1:9477/field?field_depth=3","depth":3,"active":true},{"id":"pit-b","url":"http://127.0.0.1:9481/world/","depth":2}]}
EOF
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_SINGLE_FIELD_DEPTH=1 \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-depth-singularizer.py" strip-url 'http://127.0.0.1:9477/field?field_depth=3' 2>/dev/null || true); echo "$out" | grep -q '"changed": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-depth-singularizer.py" forbid 'http://127.0.0.1:9477/field?field_depth=3' 2>/dev/null || true); echo "$out" | grep -q '"depth_fields_sealed_and_destroyed": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-depth-singularizer.py" impossibility 2>/dev/null || true); echo "$out" | grep -q 'creation_forbidden'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_SINGLE_FIELD_DEPTH=1 \
out=$(pythong "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-field-sanity.py" pass <<'EOF' 2>/dev/null || true); echo "$out" | grep -q '"single_field_depth": true'
{"layers":[{"id":"a","url":"http://127.0.0.1:9477/field?field_depth=3","depth":3,"active":true}]}
EOF
  tmp_defrag="$(mktemp -d)"
  printf '%s\n' '{"layers":[{"url":"http://127.0.0.1:9477/field?field_depth=2","depth":2}],"field_depth":3}' \
    > "${tmp_defrag}/ironclad-field-sanity-panel.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_defrag" NEXUS_SINGLE_FIELD_DEPTH=1 \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-depth-singularizer.py" cycle 2>/dev/null || true); echo "$out" | grep -q '"fixes":'
  ! grep -q 'field_depth=' "${tmp_defrag}/ironclad-field-sanity-panel.json"
  grep -q '"depth": 0' "${tmp_defrag}/ironclad-field-sanity-panel.json"
  rm -rf "$tmp_defrag"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_SINGLE_FIELD_DEPTH=1 \
out=$(pythong "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-field-net.py" json 2>/dev/null 2>/dev/null || true); echo "$out" | grep -q 'single_field_depth' || \
    NEXUS_INSTALL_ROOT="$ROOT" pythong -c "
import importlib.util
from pathlib import Path
p=Path('/home/default/Desktop/SG/NewLatest/Queen/lib/queen-field-net.py')
spec=importlib.util.spec_from_file_location('qfn', p)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
c=m.classify_url('http://127.0.0.1:9477/field?field_depth=5')
assert c.get('field_depth')==0 and c.get('field_on_field') is False and c.get('depth_field_impossible') is True and c.get('depth_fields_sealed_and_destroyed') is True
print('ok')
"

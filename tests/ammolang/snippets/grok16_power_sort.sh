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
  [[ -f "${sg}/Grok16/data/g16-power-sort-doctrine.json" ]]
  [[ -f "${sg}/Grok16/lib/field-power-sort.py" ]]
  [[ -f "${sg}/Grok16/lib/g16-power-sort-plate.py" ]]
  grep -q 'plate_not_wire' "${sg}/Grok16/data/g16-power-sort-doctrine.json"
  grep -q 'g16_power_sort' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'power_sort' "${sg}/Grok16/lib/field-always-optimal.py"
  grep -q '_power_sort_mod' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-file-browser.py"
  grep -q 'sections' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-file-browser.py"
  grep -q '/api/power-sort' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '"id": "power_sort"' "/home/default/Desktop/SG/NewLatest/data/ironclad-meld-extensions.json"
  grep -q 'field-physics-witness' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q '/api/physics-witness' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'locational_sitrep' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q '/api/locational-sitrep' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/home/default/Desktop/SG/NewLatest/.nexus-field-drive/nexus-field/state}" \
    python3 "/home/default/Desktop/SG/NewLatest/lib/field-locational-sitrep-plate.py" cycle | grep -q '"plate_not_wire": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/home/default/Desktop/SG/NewLatest/.nexus-field-drive/nexus-field/state}" GROK16_ROOT="$sg/Grok16" \
    python3 "/home/default/Desktop/SG/NewLatest/lib/field-physics-witness.py" cycle | grep -q 'We all need to know thermals'
  GROK16_SG_ROOT="$sg" SG_ROOT="$sg" NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/home/default/Desktop/SG/NewLatest/.nexus-field-drive/nexus-field/state}" \
    python3 "${sg}/Grok16/lib/field-power-sort.py" apply | grep -q '"always_best_sort": true'
  GROK16_SG_ROOT="$sg" SG_ROOT="$sg" NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/home/default/Desktop/SG/NewLatest/.nexus-field-drive/nexus-field/state}" \
    python3 "${sg}/Grok16/lib/g16-power-sort-plate.py" cycle | grep -q '"plate_not_wire": true'
  grep -q 'line_safety' "${sg}/Grok16/data/g16-power-sort-doctrine.json"
  grep -q 'narrow_band_width' "${sg}/Grok16/lib/field-power-sort.py"
  GROK16_SG_ROOT="$sg" SG_ROOT="$sg" NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/home/default/Desktop/SG/NewLatest/.nexus-field-drive/nexus-field/state}" \
    python3 "${sg}/Grok16/lib/g16-power-sort-plate.py" cycle | grep -q '"narrow_band_width": 16'
  [[ -f "${sg}/Grok16/data/g16-power-sort-panel.json" ]]
  [[ -f "${sg}/Grok16/data/g16-power-sort-bench.json" ]]
  [[ -x "${sg}/Grok16/scripts/grok16-test-gate.sh" ]]

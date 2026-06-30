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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-chips-plate-stack.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-chips-iron-steel-plate-doctrine.json" ]]
  grep -q 'chips_plate_stack' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'chips_plate_stack' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'chips_plate_stack' "/home/default/Desktop/SG/NewLatest/data/field-plate-meld-doctrine.json"
  grep -q 'sovereign_time_only' "/home/default/Desktop/SG/NewLatest/data/field-chips-iron-steel-plate-doctrine.json"
  grep -q 'steel_rewrite' "/home/default/Desktop/SG/NewLatest/data/field-chips-iron-steel-plate-doctrine.json"
  grep -q 'steel_family' "/home/default/Desktop/SG/NewLatest/lib/field-chips-plate-stack.py"
  grep -q 'field-steel-plate-optimal' "/home/default/Desktop/SG/NewLatest/data/field-chips-iron-steel-plate-doctrine.json"
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-steel-plate-optimal.py" ]]
  grep -q 'direct_neural_calculator' "/home/default/Desktop/SG/NewLatest/lib/field-chips-plate-stack.py"
  grep -q 'organize_chip_paths' "/home/default/Desktop/SG/NewLatest/lib/iron-plate-organize.py"
  grep -q '/api/chips/plate-stack' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/chips/plate-stack' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-world.py"
  grep -q 'chips_plate_stack' "/home/default/Desktop/SG/NewLatest/lib/g16-combinatronic-rebalance.py"
  grep -q 'plate_stack' "/home/default/Desktop/SG/NewLatest/data/field-ironclad-chips-combinatorics-doctrine.json"
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-chips-core.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-chips-core-doctrine.json" ]]
  grep -q 'chips_core' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'chips_core' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'condense_after_ironclad' "/home/default/Desktop/SG/NewLatest/lib/field-chips-core.py"
  grep -q '/api/chips/core' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/chips/core' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-world.py"
  grep -q 'chips_core' "/home/default/Desktop/SG/NewLatest/lib/g16-combinatronic-rebalance.py"
  grep -q 'qcc-chips-core' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-chips-cores.html"
  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/field-ironclad-chips-combinatorics.py" publish >/dev/null
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/field-steel-neural-plates.py" build >/dev/null
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-chips-plate-stack.py" build 2>/dev/null || true); echo "$out" | grep -q 'field-chips-plate-stack/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-chips-plate-stack.py" verify 2>/dev/null || true); echo "$out" | grep -q '"ok": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-chips-plate-stack.py" wire 2>/dev/null || true); echo "$out" | grep -q 'sovereign_linear_ns'
  grep -q 'field-plate-rebalance-derivatives' "/home/default/Desktop/SG/NewLatest/lib/field-chips-plate-stack.py"
  grep -q 'plate_rebalance_derivatives' "/home/default/Desktop/SG/NewLatest/lib/g16-combinatronic-rebalance.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-plate-rebalance-derivatives.py" verify 2>/dev/null || true); echo "$out" | grep -q '"ok": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/g16-combinatronic-rebalance.py" plate_derivatives 2>/dev/null || true); echo "$out" | grep -q 'central_difference'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-chips-core.py" build 2>/dev/null || true); echo "$out" | grep -q 'field-chips-core/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-chips-core.py" verify 2>/dev/null || true); echo "$out" | grep -q '"ok": true'

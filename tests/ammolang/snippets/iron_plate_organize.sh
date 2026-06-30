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

  tmp_state="$(mktemp -d)"
  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/iron-plate-organize.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/iron-plate-organize-doctrine.json" ]]
  grep -q 'iron_plate_organize' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'iron_plate_organize' "/home/default/Desktop/SG/NewLatest/data/field-plate-meld-doctrine.json"
  grep -q 'iron_plate_organize' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q '/api/iron-plate/organize' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'composite_bsp' "/home/default/Desktop/SG/NewLatest/data/iron-plate-organize-doctrine.json"
  grep -q 'ironclad_chain' "/home/default/Desktop/SG/NewLatest/data/iron-plate-organize-doctrine.json"
  grep -q '_ironclad_chain_tree' "/home/default/Desktop/SG/NewLatest/lib/iron-plate-organize.py"
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/iron-plate-spot-detector.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/iron-plate-spot-doctrine.json" ]]
  grep -q 'thermal_gate' "/home/default/Desktop/SG/NewLatest/lib/iron-plate-spot-detector.py"
  grep -q '_thermal_gate' "/home/default/Desktop/SG/NewLatest/lib/iron-plate-organize.py"
  grep -q 'iron_plate_spot' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q '/api/iron-plate/spots' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  [[ -f "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/lib/g16-iron-plate-spot-detector.py" ]]
  grep -q 'iron_plate_spot' "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/forge/ironclad_tools.py"
  grep -q 'organize_gain' "/home/default/Desktop/SG/NewLatest/lib/iron-plate-organize.py"
  grep -q 'c2_browser_embed' "/home/default/Desktop/SG/NewLatest/data/ironclad-meld-extensions.json"
  grep -q '_iron_plate_organize' "/home/default/Desktop/SG/NewLatest/lib/field-host-desktop.py"
  grep -q '"id": "iron_plate_organize"' "/home/default/Desktop/SG/NewLatest/data/ironclad-meld-extensions.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/iron-plate-organize.py" json 2>/dev/null || true); echo "$out" | grep -q 'iron-plate-organize/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/iron-plate-organize.py" json 2>/dev/null || true); echo "$out" | grep -q 'composite_bsp'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/iron-plate-organize.py" apply-desktop 2>/dev/null || true); echo "$out" | grep -q 'tray_icons'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/iron-plate-motion-resolve.py" resolve 2>/dev/null || true); echo "$out" | grep -q 'iron_plate_organize'

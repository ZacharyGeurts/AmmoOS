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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-cpu-library.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-cpu-library-seed.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-font-kit.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-font-doctrine.json" ]]
  grep -q 'cpu_library' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'cpu_library' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'field_font' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q '/api/cpu-library' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/field-font' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/field-font-editor' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/cpu-library' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-world.py"
  grep -q 'field-cpu-library' "/home/default/Desktop/SG/NewLatest/data/field-host-desktop-doctrine.json"
  grep -q 'field-font-editor' "/home/default/Desktop/SG/NewLatest/data/field-host-desktop-doctrine.json"
  grep -q 'desktop' "/home/default/Desktop/SG/NewLatest/data/field-host-desktop-doctrine.json"
  grep -q 'clipboard_master' "/home/default/Desktop/SG/NewLatest/data/field-clipboard-doctrine.json"
  grep -q 'historic_ring' "/home/default/Desktop/SG/NewLatest/data/field-clipboard-doctrine.json"
  grep -q 'history-paste' "/home/default/Desktop/SG/NewLatest/lib/field-clipboard-wire.py"
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/world/queen-cpu-library.html" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/field-font-editor.html" ]]
  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-cpu-library.py" verify 2>/dev/null || true); echo "$out" | grep -q '"ok": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-cpu-library.py" search arm 2>/dev/null || true); echo "$out" | grep -q '"hits"'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-font-kit.py" build 2>/dev/null || true); echo "$out" | grep -q '"ok": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-font-kit.py" panel 2>/dev/null || true); echo "$out" | grep -q 'field-font-panel/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-clipboard-wire.py" history 2>/dev/null || true); echo "$out" | grep -q 'field-clipboard-history/v1'
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/assets/fonts/amouranth-bold-sdf.png" ]]

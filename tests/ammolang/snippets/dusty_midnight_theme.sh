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

panel="/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/assets/dusty-midnight.css" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/assets/us-dashboard.js" ]]
  grep -q 'dusty-midnight' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'dusty-midnight.css' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'us-dashboard.js' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'us-host-machine' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'us-traffic-canvas' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'renderUSDashboard' "/home/default/Desktop/SG/NewLatest/panel/assets/us-dashboard.js"
  grep -q 'nexus-military-v8' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'nexus-military-v82' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'nexus-v82' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'v8.2.0' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q '_panel_slice' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'prefetchTabSlices' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'field_brain' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q '/api/field-brain' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-brain-panel.py" ]]
  [[ -d "/home/default/Desktop/SG/NewLatest/library/dewey" ]]

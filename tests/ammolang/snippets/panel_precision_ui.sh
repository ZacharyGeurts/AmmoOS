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
  grep -q 'view-precision-map' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'view-precision-web' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'precision-map.js' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'precision-spiderweb.js' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'nexus-map.js' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'nexus-theme.css' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/assets/nexus-map.js" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/assets/nexus-theme.css" ]]
  grep -q 'NexusMap' "/home/default/Desktop/SG/NewLatest/panel/assets/precision-map.js"
  grep -q 'us-dashboard' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'us-hero' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'map-viewport' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'primeMapPanel' "/home/default/Desktop/SG/NewLatest/panel/assets/nexus-map.js"
  grep -q 'resolveAnchor' "/home/default/Desktop/SG/NewLatest/panel/assets/precision-map.js"
  grep -q 'renderPrecisionMap' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'renderPrecisionSpiderweb' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'Precision · Map' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'Precision · Web' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'precision-place-toggle' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'precision-web-canvas' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"

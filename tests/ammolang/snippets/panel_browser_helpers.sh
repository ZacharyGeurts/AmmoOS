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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/panel-browser.sh" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/field.html" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/assets/field-foundation.js" ]]
  grep -q '/api/field' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'panel_ready' "/home/default/Desktop/SG/NewLatest/lib/threat-panel.sh"
  grep -q 'function paintPanel' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'No client cache' "/home/default/Desktop/SG/NewLatest/panel/assets/field-foundation.js"
  grep -q '/api/status' "/home/default/Desktop/SG/NewLatest/panel/assets/field-foundation.js"
  grep -q 'field-live' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'select, select option' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  ! grep -q '_inject_field_bootstrap' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/hostess7-field.sh" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/hostess7-operator.sh" ]]
  source "/home/default/Desktop/SG/NewLatest/lib/panel-browser.sh"
  nexus_panel_url | grep -q '127.0.0.1'
  nexus_panel_url | grep -q '/field'
  nexus_panel_app_url | grep -q '/app'

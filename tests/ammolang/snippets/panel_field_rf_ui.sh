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
  grep -q 'view-field-rf' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'renderFieldRF' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'renderPoliceAgency' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'police-agency-select' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'police-category-filter' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'police-import-file' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'police-import-images' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'gov-merge-banner' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'intelligence databases' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'program-tag-select' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'Obscure programs' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'program-tag-desc' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'location.reload' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'field-rf-shield-enabled' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'field-rf-lawful-kick' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'field-rf-shoot-to-kill' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'field-rf-unpermitted' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'view-field-rf' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'SHOOT TO KILL' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'field-material.js' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'field-rf-material-map' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'renderMaterialField' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'disabled forever' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'field-rf-pollution' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'field-rf-operations' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'field-rf-antenna-fields' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'resolution_score' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'NEAR-INFINITE' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'Permitted spectrum' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'WIFI_THREAT' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html" || grep -q 'Lawful kick' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"

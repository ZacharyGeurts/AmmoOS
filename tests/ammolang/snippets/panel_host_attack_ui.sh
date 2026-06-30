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
  grep -q 'view-host-attack' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'Host Attack' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'renderHostAttackMap' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'host-earth-map' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'leaflet.js' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'createGlobeLayer' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'SDF Wireframe' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'trashHostPin' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'host-map-trash' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'Zachary Geurts' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'normalizeGeo' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'warmHostEarthMap' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'attackKitKill' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'haBleedLine' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'selectHostTarget' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'host-kill-dossier' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'haTooltipText' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'target_os' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'sdf-render.js' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'NexusSdf' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'hydrateHostSdfMarkers' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'formatGps' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'HA_SDF_PIN_ANCHOR' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/assets/sdf/manifest.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/assets/sdf/pin-hostile.sdf.png" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/assets/sdf/globe-world.sdf.png" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/assets/sdf/globe-wireframe.sdf.png" ]]
  grep -q 'globe-wireframe' "/home/default/Desktop/SG/NewLatest/panel/assets/sdf/manifest.json"
  grep -q 'attackKitCheckOnline' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'attackKitRekill' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'attackKitNokill' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'haOnlineBadgeHtml' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'ha-online-badge' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'NO-KILL' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'Check Online' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'RE-KILL' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'same-host validation' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'checkNexusUpdate' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'nexus-version-btn' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'nexus-upgrade-btn' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'nexus-restart-btn' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'distance_label' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -qE 'v[4-7]\.[0-9]+\.[0-9]+' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"

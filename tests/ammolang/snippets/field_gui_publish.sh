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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-gui-publish.sh" ]]
  grep -q 'nexus_field_gui_publish_all' "/home/default/Desktop/SG/NewLatest/lib/threat-panel.sh"
  grep -q 'field_hardware' "/home/default/Desktop/SG/NewLatest/lib/threat-panel.sh"
  grep -q 'field_hazard_onset' "/home/default/Desktop/SG/NewLatest/lib/threat-panel.sh"
  grep -q 'lethal_enforcement' "/home/default/Desktop/SG/NewLatest/lib/threat-panel.sh"
  grep -q '/api/field' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'renderHardware(doc)' "/home/default/Desktop/SG/NewLatest/panel/assets/signals-field.js"
  grep -q 'fetch("/api/status"' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'FIELD_PARALLEL_SLICES' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'PANEL_PARALLEL_KEYS' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'max_workers: int = 25' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  ! grep -q 'nexus_hostess7_nexus_update_plan' "/home/default/Desktop/SG/NewLatest/lib/hostess7-operator.sh"
  grep -q 'NEXUS_VERSION="g16-1.0"' "/home/default/Desktop/SG/NewLatest/lib/nexus-common.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" bash -c '
    source "${NEXUS_INSTALL_ROOT}/lib/nexus-common.sh"
    nexus_init_runtime_paths
    source "${NEXUS_INSTALL_ROOT}/lib/field-gui-publish.sh"
    nexus_field_gui_publish_all
    [[ -s "$NEXUS_STATE_DIR/field-hardware-panel.json" ]] || nexus_field_hardware_json | grep -q field-hardware
  '

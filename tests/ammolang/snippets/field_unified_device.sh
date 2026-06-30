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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-unified-device.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-unified-device-doctrine.json" ]]
  grep -q 'one_field_whole_device' "/home/default/Desktop/SG/NewLatest/data/field-unified-device-doctrine.json"
  grep -q 'kilroy_kernel_first' "/home/default/Desktop/SG/NewLatest/data/field-unified-device-doctrine.json"
  grep -q 'unified_device_field' "/home/default/Desktop/SG/NewLatest/lib/field-underlay.py"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" KILROY_ROOT="/home/default/Desktop/SG/NewLatest/KILROY" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-unified-device.py" board 2>/dev/null 2>/dev/null || true); echo "$out" | grep -q '"one_field": true'
  [[ -f "${tmp_state}/field-unified-device.json" ]]
  grep -q 'kilroy_kernel' "${tmp_state}/field-unified-device.json"
  grep -q 'motherboard' "${tmp_state}/field-unified-device.json"
  grep -q 'fcc' "${tmp_state}/field-unified-device.json"
  rm -rf "$tmp_state"

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

  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  [[ -f "${sg}/Grok16/data/g16-always-optimal-doctrine.json" ]]
  [[ -f "${sg}/Grok16/lib/field-always-optimal.py" ]]
  grep -q 'always_optimal' "${sg}/Grok16/scripts/grok16-integrate.sh"
  grep -q 'ideal_profile' "${sg}/NewLatest/lib/field-plate-combinatorics-bridge.py"
  grep -q '_run_always_optimal' "/home/default/Desktop/SG/NewLatest/lib/field-compatibility-layers.py"
  grep -q 'nexus_boot_impl_always_optimal' "/home/default/Desktop/SG/NewLatest/lib/nexus-boot-impl.sh"
  grep -q 'auto_on_panel_boot' "${sg}/Grok16/data/g16-always-optimal-doctrine.json"
  grep -q '/api/always-optimal' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  GROK16_SG_ROOT="$sg" SG_ROOT="$sg" NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/home/default/Desktop/SG/NewLatest/.nexus-field-drive/nexus-field/state}" \
    python3 "${sg}/Grok16/lib/field-always-optimal.py" apply --no-layers | grep -q '"always_optimal": true'
  [[ -f "${sg}/Grok16/data/g16-always-optimal-panel.json" ]]
  grep -q 'G16_BELT_PROFILE' "${sg}/Grok16/data/grok16-integrate.env"

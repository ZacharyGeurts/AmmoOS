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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-chips-program-usage.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-chips-program-usage-doctrine.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-chips-program-usage-seed.json" ]]
  grep -q 'chips_program_usage' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q '/api/chips/usage' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/chips/usage' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-world.py"
  grep -q 'chips_usage' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-kilroy.py"
  grep -q 'chips_usage' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-desktop.py"
  grep -q 'kilroy_integration' "/home/default/Desktop/SG/NewLatest/data/field-chips-program-usage-doctrine.json"
  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/field-ironclad-chips-combinatorics.py" publish >/dev/null
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-chips-program-usage.py" resolve browser 2>/dev/null || true); echo "$out" | grep -q 'field-chips-program-usage/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-chips-program-usage.py" kilroy 2>/dev/null || true); echo "$out" | grep -q '"program_id": "kilroy"'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-chips-program-usage.py" publish 2>/dev/null || true); echo "$out" | grep -q 'field-chips-program-usage-registry/v1'
  rm -rf "$tmp_state"

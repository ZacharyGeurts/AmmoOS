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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/h7-library-truth.py" ]]
  [[ -f "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/lib/field_combinatorics.py" ]]
  [[ -f "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/lib/field_truth_blocks.py" ]]
  grep -q 'combinatorics_bridge' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q '_refresh_combinatorics_bridge' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'combinatoric_tree_complete' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'walk_tree_to_end' "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/lib/field_combinatorics.py"
  grep -q 'condense_plates' "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/lib/field_combinatorics.py"
  grep -q 'combinatorics-bridge/v2' "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py"
  grep -q 'c2_taskbar' "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py"
  grep -q 'combinatorics_rejected' "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py"
  grep -q 'read_last_good_panel' "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/lib/field_combinatorics.py"
  grep -q '_combinatorics_posture' "/home/default/Desktop/SG/NewLatest/lib/g16-compiler-sense-plate.py"
  grep -q '/api/library/truth' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'h7r-sentence' "/home/default/Desktop/SG/NewLatest/panel/assets/h7-reader.js"
  tmp_state="$(mktemp -d)"
  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" \
    python3 "$sg/Grok16/lib/field_truth_blocks.py" publish | grep -q 'truth_block_count'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" \
    python3 "$sg/Grok16/lib/field_combinatorics.py" publish | grep -q 'combinatoric_tree'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py" build 2>/dev/null || true); echo "$out" | grep -q 'combinatoric_tree_complete'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
    HOSTESS7_ROOT="${HOSTESS7_ROOT:-$ROOT/Hostess7}" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/h7-library-truth.py" sentence network-security-field-guide 0 "Firewalls filter traffic." 2>/dev/null || true); echo "$out" | grep -q 'verdict'

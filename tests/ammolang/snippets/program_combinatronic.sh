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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-program-combinatronic.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-program-combinatronic-seed.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-program-combinatronic-doctrine.json" ]]
  grep -q 'program_combinatronic' "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/data/g16-field-combinatorics-doctrine.json"
  grep -q '_program_combinatronic_slice' "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/lib/field_combinatorics.py"
  grep -q 'program_combinatronic' "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py"
  grep -q 'program_combinatronic' "/home/default/Desktop/SG/NewLatest/lib/field-combinatorics-comb.py"
  grep -q '/api/program/combinatronic' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'boil_command' "/home/default/Desktop/SG/NewLatest/lib/field-program-combinatronic.py"
  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-program-combinatronic.py" combinatronic 2>/dev/null || true); echo "$out" | grep -q 'field-program-combinatronic/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-program-combinatronic.py" boil python def 2>/dev/null || true); echo "$out" | grep -q '"canonical": "declare"'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
    python3 "$sg/Grok16/lib/field_combinatorics.py" publish | grep -q 'program_combinatronic'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-program-combinatronic.py" combinatronic 2>/dev/null || true); echo "$out" | grep -q '"boil_complete": true'

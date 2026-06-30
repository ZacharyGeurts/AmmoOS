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
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-code-bugfinder.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-code-bugfinder-doctrine.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-media-codec-doctrine.json" ]]
  grep -q '/api/bugfinder' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/bugfinder/ironclad-cycle' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'ironclad_bugfix_cycle' "/home/default/Desktop/SG/NewLatest/lib/field-code-bugfinder.py"
  grep -q 'code_bugfinder' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'truth_compare_high_rate' "/home/default/Desktop/SG/NewLatest/lib/field-code-bugfinder.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$(mktemp -d)" SG_ROOT="$sg" HOSTESS7_ROOT="$ROOT/Hostess7" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-code-bugfinder.py" json 2>/dev/null || true); echo "$out" | grep -q 'field-code-bugfinder-panel/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$(mktemp -d)" SG_ROOT="$sg" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/field-code-bugfinder.py" text \
      'password = "hardcoded_secret"; eval(user_input)' \
    | grep -q 'truth_compares_per_sec'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$(mktemp -d)" SG_ROOT="$sg" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/field-code-bugfinder.py" scan "/home/default/Desktop/SG/NewLatest/lib/field-code-bugfinder.py" --max 32 \
    | grep -q '"bug_count"'

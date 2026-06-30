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

  grep -q 'sense_universal_slice' "/home/default/Desktop/SG/NewLatest/lib/field-sense-package-meld.py"
  grep -q 'universal_lock' "/home/default/Desktop/SG/NewLatest/data/field-sense-package-doctrine.json"
  grep -q 'universal_lock' "/home/default/Desktop/SG/NewLatest/data/eye-ear-plate-doctrine.json"
  grep -q 'sense_stack' "/home/default/Desktop/SG/NewLatest/data/universal-protector-doctrine.json"
  grep -q 'sense_universal' "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/data/g16-field-combinatorics-doctrine.json"
  grep -q '_sense_universal_slice' "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/lib/field_combinatorics.py"
  grep -q 'universal_lock' "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/lib/field_combinatorics.py"
  grep -q 'field_ellie_fier' "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/lib/field_combinatorics.py"
  grep -q 'sense_universal' "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py"
  grep -q '_universal_lock_gate' "/home/default/Desktop/SG/NewLatest/lib/eye-ear-plate.py"
  grep -q 'universal_lock' "/home/default/Desktop/SG/NewLatest/lib/universal-protector.py"
  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-sense-package-meld.py" slice 2>/dev/null || true); echo "$out" | grep -q 'field-sense-universal-slice'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
    python3 "$sg/Grok16/lib/field_combinatorics.py" publish | grep -q 'sense_universal'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py" build 2>/dev/null || true); echo "$out" | grep -q 'sense_universal_lock'

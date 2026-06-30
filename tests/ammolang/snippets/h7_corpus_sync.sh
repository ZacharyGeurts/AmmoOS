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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-h7-corpus-sync.py" ]]
  grep -q 'h7_corpus_sync' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'is_legitimate_h7_textbook' "/home/default/Desktop/SG/NewLatest/lib/field-non-fielded-safety.py"
  grep -q 'h7-k12-field-corpus' "/home/default/Desktop/SG/NewLatest/lib/h7-field-drive-tie.py"
  grep -q 'h7-security-field-corpus' "/home/default/Desktop/SG/NewLatest/lib/h7-field-drive-tie.py"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
    HOSTESS7_ROOT="${HOSTESS7_ROOT:-$ROOT/Hostess7}" \
    SG_ROOT="${SG_ROOT:-$(dirname "$ROOT")}" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-h7-corpus-sync.py" sync --no-build 2>/dev/null || true); echo "$out" | grep -q 'field-h7-corpus-sync'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
    HOSTESS7_ROOT="${HOSTESS7_ROOT:-$ROOT/Hostess7}" \
    SG_ROOT="${SG_ROOT:-$(dirname "$ROOT")}" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-h7-corpus-sync.py" audit 2>/dev/null || true); echo "$out" | grep -q 'legitimate_h7'

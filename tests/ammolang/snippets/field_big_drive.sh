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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-big-drive.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-big-drive-doctrine.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/field-big-drive.html" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/assets/field-big-drive.js" ]]
  grep -q '/api/field-big-drive' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/field-big-drive' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'field-big-drive' "/home/default/Desktop/SG/NewLatest/data/field-host-desktop-doctrine.json"
  grep -q 'Open in Big Drive' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-files.js"
  grep -q '_storage_formats' "/home/default/Desktop/SG/NewLatest/lib/field-file-formats.py"
  grep -q 'field_on_field_forbidden' "/home/default/Desktop/SG/NewLatest/data/field-big-drive-doctrine.json"
  grep -q 'bd-stabilizer-bar' "/home/default/Desktop/SG/NewLatest/panel/field-big-drive.html"
  grep -q 'stabilizer_progress' "/home/default/Desktop/SG/NewLatest/lib/field-big-drive.py"
  grep -q 'stabilize_drive' "/home/default/Desktop/SG/NewLatest/lib/field-big-drive.py"
py="python3"
  command -v pythong >/dev/null 2>&1 && py="pythong"
  SG_ROOT="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    "$py" "/home/default/Desktop/SG/NewLatest/lib/field-big-drive.py" json | grep -q 'field-big-drive/v1'
tmp_iso="$NEXUS_STATE_DIR/big-drive-test.iso"
  printf 'plain iso payload' >"$tmp_iso"
  stab_out=$(SG_ROOT="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    "$py" "/home/default/Desktop/SG/NewLatest/lib/field-big-drive.py" dispatch <<EOF
{"action":"stabilize","path":"${tmp_iso}","device_id":"usb_stick"}
EOF
)
  echo "$stab_out" | grep -q '"ok": true'
  echo "$stab_out" | grep -q 'universal_2d'

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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-always-files.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-always-files-doctrine.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-vfs-ai-contract.json" ]]
  grep -q 'history_for_path' "/home/default/Desktop/SG/NewLatest/lib/field-drive-indexer.py"
  grep -q 'enrich_entry' "/home/default/Desktop/SG/NewLatest/lib/field-always-files.py"
  grep -q 'properties_menu' "/home/default/Desktop/SG/NewLatest/lib/field-always-files.py"
  grep -q 'system_security' "/home/default/Desktop/SG/NewLatest/lib/field-always-files.py"
  grep -q 'system_security' "/home/default/Desktop/SG/NewLatest/data/field-always-files-doctrine.json"
  grep -q 'password_required' "/home/default/Desktop/SG/NewLatest/data/field-always-files-doctrine.json"
  grep -q '_maybe_enrich_row' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-file-browser.py"
  grep -q 'always_properties' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-file-browser.py"
  grep -q '/api/field-vfs' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/field-timeshift' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'always_files' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'alwaysKnowsBadge' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-files.js"
  grep -q 'showProperties' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-files.js"
  grep -q 'renderPropertiesFlyout' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-files.js"
  grep -q 'qf-props-flyout' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-files.html"
  grep -q 'qf-props-menu' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-files.html"
  grep -q 'QueenIconEngine' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-icon-engine.js"
  grep -q 'file-folder-32.png' "/home/default/Desktop/SG/NewLatest/Queen/data/queen-icon-battery.json"
  grep -q 'QueenIconEngine' "/home/default/Desktop/SG/NewLatest/panel/assets/field-startbar.js"
  grep -q 'folderIconEl' "/home/default/Desktop/SG/NewLatest/panel/assets/field-startbar.js"
  grep -q 'qf-sec-banner' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-files.css"
  grep -q 'qf-fly-pane' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-viewer.css"
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/world/assets/icons/file-folder-32.png" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/panel/assets/queen-icon-engine.js" ]]
  tmp_state="$(mktemp -d)"
  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" QUEEN_ROOT="/home/default/Desktop/SG/NewLatest/Queen" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-always-files.py" sync 2>/dev/null || true); echo "$out" | grep -q 'field-always-files-plate/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" QUEEN_ROOT="/home/default/Desktop/SG/NewLatest/Queen" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-always-files.py" ai 2>/dev/null || true); echo "$out" | grep -q 'field-vfs-ai-context/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" QUEEN_ROOT="/home/default/Desktop/SG/NewLatest/Queen" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-always-files.py" resolve lib/field-always-files.py 2>/dev/null || true); echo "$out" | grep -q 'field-always-file/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" QUEEN_ROOT="/home/default/Desktop/SG/NewLatest/Queen" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-always-files.py" properties lib/field-always-files.py 2>/dev/null || true); echo "$out" | grep -q 'field-always-properties/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" QUEEN_ROOT="/home/default/Desktop/SG/NewLatest/Queen" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-always-files.py" properties lib/field-always-files.py 2>/dev/null || true); echo "$out" | grep -q 'password_required'

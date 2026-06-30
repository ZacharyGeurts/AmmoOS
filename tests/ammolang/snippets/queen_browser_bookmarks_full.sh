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

  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/data/queen-localhost-bookmarks.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-browser-settings.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-bookmark-tree.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-bookmark-tooltips.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/world/queen-bookmarks-bar.js" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/world/queen-browser-settings.html" ]]
  grep -q 'localhost_flyout' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-browser.py"
  grep -q 'bookmark_trees' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-browser.py"
  grep -q 'qb-bookmarks-search' "/home/default/Desktop/SG/NewLatest/Queen/world/browser.html"
  grep -q '/api/queen-browser-settings' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-world.py"
  grep -q 'tooltips_enabled' "/home/default/Desktop/SG/NewLatest/Queen/data/queen-browser-settings-doctrine.json"
  grep -q 'security_locked_keys' "/home/default/Desktop/SG/NewLatest/Queen/data/queen-browser-settings-doctrine.json"
  grep -q '_secure_compat_profile' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-browser.py"
  pythong -c "import json; d=json.load(open('/home/default/Desktop/SG/NewLatest/Queen/data/queen-browser-settings-doctrine.json')); assert 'tooltips_fetch_meta' not in (d.get('defaults') or {}), d"
  ! [[ -f "/home/default/Desktop/SG/NewLatest/Queen/world/queen-browser.js" ]]
  grep -q '_extract_gecko_tree' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-browser-import.py"
out=$(pythong "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-browser-settings.py" posture 2>/dev/null || true); echo "$out" | grep -q '"security_locked": true'

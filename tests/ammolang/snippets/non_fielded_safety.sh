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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-non-fielded-safety.py" ]]
  grep -q 'NEXUS_FIELD_PUBLISH_REQUIRES_DEFIELD' "/home/default/Desktop/SG/NewLatest/config/nexus.conf"
  grep -q 'NEXUS_FIELD_DRIVE_STATE_REDIRECT=0' "/home/default/Desktop/SG/NewLatest/config/nexus.conf"
  grep -q 'non_fielded_safety' "/home/default/Desktop/SG/NewLatest/data/field-underlay-switch-doctrine.json"
  grep -q 'non_fielded_safety' "/home/default/Desktop/SG/NewLatest/data/field-switch-safety-doctrine.json"
  grep -q 'defield_audit' "/home/default/Desktop/SG/NewLatest/lib/field-drive-converter.py"
  grep -q 'field_one' "/home/default/Desktop/SG/NewLatest/data/field-one-doctrine.json"
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-one.py" json 2>/dev/null 2>/dev/null || true); echo "$out" | grep -q '"field_one": true'
  grep -q 'hostile_scan' "/home/default/Desktop/SG/NewLatest/data/field-one-doctrine.json"
  grep -q 'FIELD_NOT_ONE' "/home/default/Desktop/SG/NewLatest/lib/field-one-hostile-scan.py"
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-one-hostile-scan.py" --dry-run 2>/dev/null 2>/dev/null || true); echo "$out" | grep -q '"field_one": "field_one"'
  grep -q 'purge_nested_drive_field' "/home/default/Desktop/SG/NewLatest/lib/field-non-fielded-safety.py"
  grep -q '_gate_publish' "/home/default/Desktop/SG/NewLatest/lib/field-drive-system.py"
  grep -q 'nexus-field' "/home/default/Desktop/SG/NewLatest/World_Redata/redata/safety.py" 2>/dev/null \
    || grep -q 'nexus-field' "/home/default/Desktop/SG/NewLatest/../World_Redata/redata/safety.py"
  grep -q '_non_fielded_posture' "/home/default/Desktop/SG/NewLatest/lib/field-underlay-switch.py"
  grep -q 'defield-audit' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'purge-nested-drive' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'ti-defield-status' "/home/default/Desktop/SG/NewLatest/panel/assets/tristate-installer.js"
  grep -q 'f9-defield-audit' "/home/default/Desktop/SG/NewLatest/panel/assets/underlay-f9.js"
  grep -q 'NEXUS_FIELD_DRIVE_STATE_REDIRECT' "/home/default/Desktop/SG/NewLatest/lib/field-drive-system.sh"
  tmp_state="$(mktemp -d)"
  tmp_team="$(mktemp -d)"
  mkdir -p "${tmp_team}/nexus-field/system"
  echo probe >"${tmp_team}/nexus-field/system/hotspot.txt"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$(dirname "$ROOT")" \
    HOSTESS7_TEAM_FIELD="$tmp_team" HOSTESS7_ROOT="${tmp_team}/h7" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-non-fielded-safety.py" audit 2>/dev/null 2>/dev/null || true); echo "$out" | grep -q 'nested_nexus_field_on_drives'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$(dirname "$ROOT")" \
    HOSTESS7_TEAM_FIELD="$tmp_team" HOSTESS7_ROOT="${tmp_team}/h7" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-non-fielded-safety.py" gate-publish 2>/dev/null 2>/dev/null || true); echo "$out" | grep -q 'nested_field_on_drive'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$(dirname "$ROOT")" \
    HOSTESS7_TEAM_FIELD="$tmp_team" HOSTESS7_ROOT="${tmp_team}/h7" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-drive-system.py" json 2>/dev/null 2>/dev/null || true); echo "$out" | grep -q 'host_mirror_only'
  rm -rf "$tmp_state" "$tmp_team"

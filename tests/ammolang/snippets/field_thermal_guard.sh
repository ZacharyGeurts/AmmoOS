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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-thermal-guard.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-global-redata.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-thermal-guard-doctrine.json" ]]
  grep -q 'NEXUS_FIELD_THERMAL_GUARD' "/home/default/Desktop/SG/NewLatest/config/nexus.conf"
  grep -q 'NEXUS_FIELD_MAX_JOULES_PER_SEC' "/home/default/Desktop/SG/NewLatest/config/nexus.conf"
  grep -q 'NEXUS_FIELD_REDATA_CHUNK' "/home/default/Desktop/SG/NewLatest/config/nexus.conf"
  grep -q 'nexus_boot_impl_thermal_guard_init' "/home/default/Desktop/SG/NewLatest/lib/nexus-boot-impl.sh"
  grep -q 'nexus_boot_impl_bounded_redata' "/home/default/Desktop/SG/NewLatest/lib/nexus-boot-impl.sh"
  grep -q 'field-thermal-guard' "/home/default/Desktop/SG/NewLatest/lib/nexus-daemon.sh"
  grep -q 'safe_global_redata' "/home/default/Desktop/SG/NewLatest/lib/field-thermal-guard.py"
  grep -q 'headroom_pct' "/home/default/Desktop/SG/NewLatest/lib/field-thermal-guard.py"
  grep -q 'gatekeeper_tighten' "/home/default/Desktop/SG/NewLatest/lib/field-thermal-guard.py"
  grep -q '_field_thermal_meta' "/home/default/Desktop/SG/NewLatest/lib/connection-gatekeeper.py"
  grep -q 'field_thermal_guard' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'monolithic_blast' "/home/default/Desktop/SG/NewLatest/lib/field-global-redata.py"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-thermal-guard.py" json 2>/dev/null 2>/dev/null || true); echo "$out" | grep -q 'headroom_pct'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-global-redata.py" boot-test 2>/dev/null 2>/dev/null || true); echo "$out" | grep -q 'incremental'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-global-redata.py" boot-test 2>/dev/null 2>/dev/null || true); echo "$out" | grep -q 'monolithic_blast'
  rm -rf "$tmp_state"

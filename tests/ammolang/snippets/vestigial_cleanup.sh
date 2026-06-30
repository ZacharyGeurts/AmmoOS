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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/nexus-vestigial-cleanup.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/nexus-vestigial-cleanup.sh" ]]
  grep -q 'nexus_vestigial_cleanup_run' "/home/default/Desktop/SG/NewLatest/lib/nexus-vestigial-cleanup.sh"
  grep -q 'nexus_boot_impl_vestigial_cleanup' "/home/default/Desktop/SG/NewLatest/lib/nexus-boot-impl.sh"
  grep -q 'nexus_vestigial_cleanup_run' "/home/default/Desktop/SG/NewLatest/nexus.sh"
  grep -q 'nexus_znetwork_startup_with_us' "/home/default/Desktop/SG/NewLatest/lib/znetwork-field.sh"
  grep -q 'Bypassed OS Networking' "/home/default/Desktop/SG/NewLatest/lib/panel-tray.py"
  grep -q 'Bypassed OS Networking' "/home/default/Desktop/SG/NewLatest/lib/panel-tray.sh"
  grep -q 'nexus-shield.desktop' "/home/default/Desktop/SG/NewLatest/lib/nexus-vestigial-cleanup.py"
  grep -q 'ammocode-stack.desktop' "/home/default/Desktop/SG/NewLatest/lib/nexus-vestigial-cleanup.py"
  grep -q 'never_harm_os' "/home/default/Desktop/SG/NewLatest/lib/nexus-vestigial-cleanup.py"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/nexus-vestigial-cleanup.py" json 2>/dev/null || true); echo "$out" | grep -q 'nexus-vestigial-cleanup/v1'
  rm -rf "$tmp_state"

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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/nexus-field-early-boot.sh" ]]
  [[ -x "/home/default/Desktop/SG/NewLatest/scripts/nexus-field-early-boot.sh" ]]
  grep -q 'nexus_field_early_boot_run' "/home/default/Desktop/SG/NewLatest/lib/nexus-field-early-boot.sh"
  grep -q 'nexus_field_early_kilroy_unified' "/home/default/Desktop/SG/NewLatest/lib/nexus-field-early-boot.sh"
  grep -q 'nexus_boot_impl_underlay_early' "/home/default/Desktop/SG/NewLatest/lib/nexus-boot-impl.sh"
  grep -q 'early_boot_before_guest_os' "/home/default/Desktop/SG/NewLatest/data/field-underlay-doctrine.json"
  grep -q 'kilroy_kernel_first' "/home/default/Desktop/SG/NewLatest/data/field-underlay-doctrine.json"
  grep -q 'nexus-field-early' "/home/default/Desktop/SG/NewLatest/scripts/field-mint-boot-ready.sh"
  grep -q 'nexus-field-early-boot.sh' "/home/default/Desktop/SG/NewLatest/scripts/field-mint-boot-ready.sh"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" NEXUS_ZNETWORK_NO_SUDO=1 \
    ZNETWORK_FAST=1 NEXUS_FIELD_EARLY_TIMEOUT=45 NEXUS_FRONT_HOOK=1 NEXUS_SELF_DEFENSE=0 \
    bash "/home/default/Desktop/SG/NewLatest/scripts/nexus-field-early-boot.sh" >/dev/null 2>&1 || true
  [[ -f "${tmp_state}/field-underlay-early.json" ]]
  grep -q 'kilroy_kernel' "${tmp_state}/field-underlay-early.json"
  grep -q 'unified_device_field' "${tmp_state}/field-underlay-early.json"
  grep -q 'guest_field_grant' "${tmp_state}/field-underlay-early.json"
  rm -rf "$tmp_state"

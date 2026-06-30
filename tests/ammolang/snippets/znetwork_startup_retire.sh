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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/znetwork-startup-retire.py" ]]
  grep -q 'startup_retire' "/home/default/Desktop/SG/NewLatest/data/znetwork-doctrine.json"
  grep -q 'nexus_znetwork_startup_retire_host' "/home/default/Desktop/SG/NewLatest/lib/znetwork-field.sh"
  grep -q 'startup_retire_host' "/home/default/Desktop/SG/NewLatest/data/znetwork-doctrine.json"
  grep -q 'disable_startup_only_no_live_stop' "/home/default/Desktop/SG/NewLatest/data/znetwork-doctrine.json"
  grep -q 'nexus_install_reboot_prompt' "/home/default/Desktop/SG/NewLatest/lib/installer.sh"
  grep -q 'nexus_install_reboot_prompt' "/home/default/Desktop/SG/NewLatest/lib/nxf-install.sh"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/znetwork-startup-retire.py" detect 2>/dev/null || true); echo "$out" | grep -q '"schema": "znetwork-startup-retire/v1"'
  printf 'running=1\n' >"${tmp_state}/znetwork-running.marker"
  printf '{"schema":"znetwork-relayer/v1","active":true}\n' >"${tmp_state}/znetwork-relayer.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/znetwork-startup-retire.py" takeover 2>/dev/null || true); echo "$out" | grep -q '"ok": true'
  rm -rf "$tmp_state"

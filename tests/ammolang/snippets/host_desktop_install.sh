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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/nexus-host-desktop-install.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/nexus-host-desktop-install.sh" ]]
  grep -q 'nexus_field_os_install_host_desktop' "/home/default/Desktop/SG/NewLatest/lib/nexus-field-os.sh"
  grep -q 'nexus_field_os_install_host_desktop' "/home/default/Desktop/SG/NewLatest/nexus.sh"
  grep -q 'nexus-host-desktop/v1' "/home/default/Desktop/SG/NewLatest/lib/nexus-host-desktop-install.py"
  grep -q 'ammocode-stack' "/home/default/Desktop/SG/NewLatest/lib/nexus-host-desktop-install.py"
  grep -q 'pinned-apps' "/home/default/Desktop/SG/NewLatest/lib/nexus-host-desktop-install.py"
  tmp_state="$(mktemp -d)"
  tmp_home="$(mktemp -d)"
  mkdir -p "${tmp_home}/.local/share/applications"
  printf '[Desktop Entry]\nType=Application\nName=Old\nExec=true\n' >"${tmp_home}/.local/share/applications/ammocode-stack.desktop"
  NEXUS_HOST_DESKTOP_HOME="$tmp_home" NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
    NEXUS_HOST_DESKTOP_PIN=0 NEXUS_HOST_DESKTOP_FORCE=1 \
    python3 "/home/default/Desktop/SG/NewLatest/lib/nexus-host-desktop-install.py" run | grep -q 'nexus-host-desktop/v1'
  [[ ! -f "${tmp_home}/.local/share/applications/ammocode-stack.desktop" ]]
  [[ -f "${tmp_home}/.local/share/applications/nexus-field.desktop" ]]
  rm -rf "$tmp_state" "$tmp_home"

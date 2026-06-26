#!/bin/bash
# Field underlay switch — Tristate installer hooks + F9 hotkey service.
set -euo pipefail

nexus_underlay_switch_board() {
  [[ "${NEXUS_FIELD_UNDERLAY:-1}" == "1" ]] || return 0
  local root="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
  local py="${root}/lib/field-underlay-switch.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${root}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}" \
    SG_ROOT="${SG_ROOT:-}" KILROY_ROOT="${KILROY_ROOT:-}" \
    pythong "$py" board 2>/dev/null || true
}

nexus_underlay_hotkey_install() {
  local root="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
  local user="${1:-${SUDO_USER:-$USER}}"
  local home py
  [[ -f "${root}/lib/field-underlay-hotkey.py" ]] || return 0
  home="$(getent passwd "$user" 2>/dev/null | cut -d: -f6)"
  [[ -n "$home" ]] || home="${HOME:-/home/$user}"
  py="${root}/lib/field-underlay-hotkey.py"
  local autostart="${home}/.config/autostart"
  mkdir -p "$autostart" 2>/dev/null || return 0
  cat >"${autostart}/nexus-underlay-hotkey.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=NEXUS Underlay Hotkey (F9)
Comment=Opens 2026 Tristate Installer — permanent underlay switch
Exec=env NEXUS_INSTALL_ROOT=${root} NEXUS_STATE_DIR=${NEXUS_STATE_DIR:-/var/lib/nexus-shield} pythong ${py}
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
EOF
  chown "${user}:${user}" "${autostart}/nexus-underlay-hotkey.desktop" 2>/dev/null || true
  chmod 644 "${autostart}/nexus-underlay-hotkey.desktop" 2>/dev/null || true
}

nexus_tristate_installer_url() {
  local port="${NEXUS_THREAT_PANEL_PORT:-9477}"
  printf 'http://127.0.0.1:%s/tristate-installer' "$port"
}
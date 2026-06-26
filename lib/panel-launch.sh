#!/bin/bash
# Panel launch — desktop entries + boot browser open (delegates to panel-browser.sh).

# shellcheck source=/dev/null
[[ -f "${NEXUS_INSTALL_ROOT}/lib/panel-browser.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/panel-browser.sh"

nexus_panel_open_browser() {
  declare -f nexus_panel_open_on_boot >/dev/null 2>&1 \
    && nexus_panel_open_on_boot "${1:-$(nexus_panel_url 2>/dev/null || echo "http://127.0.0.1:${NEXUS_THREAT_PANEL_PORT:-9477}/field")}"
}

nexus_panel_install_desktop() {
  local root="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
  local port="${NEXUS_THREAT_PANEL_PORT:-9477}"
  local icon_src="${root}/assets/nexus-shield.png"
  local apps_dir="/usr/share/applications"
  local icon_dir="/usr/share/icons/hicolor/256x256/apps"
  local ver
  ver="$(nexus_read_version 2>/dev/null || echo "10.4.0")"

  [[ -f "$icon_src" ]] || return 0
  install -d -m 755 "$icon_dir" 2>/dev/null || return 0
  install -m 644 "$icon_src" "${icon_dir}/nexus-shield.png" 2>/dev/null || true

  install -m 755 "${root}/nexus.sh" /usr/local/bin/nexus.sh 2>/dev/null || true
  cat >"${apps_dir}/nexus-shield.desktop" <<EOF
[Desktop Entry]
Version=${ver}
Type=Application
Name=Underlay F9 — NEXUS Field
GenericName=Underlay F9
Comment=Full field underlay command — opens panel in browser on start
Exec=/usr/local/bin/nexus.sh
Icon=nexus-shield
Terminal=false
Categories=Security;Network;System;
Keywords=security;firewall;network;nexus;field;znetwork;
StartupNotify=true
EOF
  chmod 644 "${apps_dir}/nexus-shield.desktop" 2>/dev/null || true

  local tristate_exec="/usr/local/bin/nexus-install-gui.sh"
  [[ -x "${root}/nexus-install-gui.sh" ]] || tristate_exec="/usr/local/bin/nexus.sh --tab underlay"
  cat >"${apps_dir}/nexus-tristate-installer.desktop" <<EOF
[Desktop Entry]
Version=${ver}
Type=Application
Name=2026 Tristate Installer
GenericName=Field Underlay Install
Comment=Underlay F9 installer — KILROY · World_Redata WRDT1 · F9 hotkey
Exec=${tristate_exec}
Icon=nexus-shield
Terminal=false
Categories=System;Settings;Security;
Keywords=nexus;underlay;kilroy;tristate;install;field;
StartupNotify=true
EOF
  chmod 644 "${apps_dir}/nexus-tristate-installer.desktop" 2>/dev/null || true
  command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database /usr/share/applications 2>/dev/null || true
  nexus_log "INFO" "panel-launch" "DESKTOP_ENTRY installed nexus-shield + tristate"
}
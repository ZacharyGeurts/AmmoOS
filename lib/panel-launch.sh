#!/bin/bash
# Open NEXUS threat panel in default browser once per boot (operator UX).

NEXUS_PANEL_LAUNCH_MARKER="${NEXUS_PANEL_LAUNCH_MARKER:-${NEXUS_STATE_DIR}/panel-launched.marker}"
NEXUS_THREAT_PANEL_PORT="${NEXUS_THREAT_PANEL_PORT:-9477}"

nexus_panel_open_browser() {
  [[ "${NEXUS_PANEL_AUTO_OPEN:-1}" == "1" ]] || return 0
  local url="https://127.0.0.1:${NEXUS_THREAT_PANEL_PORT}/"
  local today
  today="$(date -u '+%Y-%m-%d' 2>/dev/null || date '+%Y-%m-%d')"

  if [[ -f "$NEXUS_PANEL_LAUNCH_MARKER" ]] && grep -q "^${today}$" "$NEXUS_PANEL_LAUNCH_MARKER" 2>/dev/null; then
    return 0
  fi

  local uid user home
  uid="$(id -u default 2>/dev/null || echo "")"
  [[ -n "$uid" ]] || uid="$(getent passwd "${SUDO_USER:-$USER}" 2>/dev/null | cut -d: -f3)"
  user="$(getent passwd "${SUDO_USER:-default}" 2>/dev/null | cut -d: -f1)"
  [[ -z "$user" || "$user" == "root" ]] && user="default"
  home="$(getent passwd "$user" 2>/dev/null | cut -d: -f6)"
  [[ -n "$home" ]] || home="/home/default"

  local opened=0 i
  for i in $(seq 1 30); do
    if curl -sk --connect-timeout 1 "$url" >/dev/null 2>&1; then
      opened=1
      break
    fi
    sleep 1
  done
  [[ "$opened" -eq 1 ]] || {
    nexus_log "WARN" "panel-launch" "PANEL_OPEN_SKIP panel not ready url=${url}"
    return 0
  }

  if [[ -n "$uid" && "$uid" != "0" ]]; then
    sudo -u "$user" DISPLAY="${DISPLAY:-:0}" XAUTHORITY="${XAUTHORITY:-$home/.Xauthority}" \
      xdg-open "$url" >/dev/null 2>&1 &
  else
    DISPLAY="${DISPLAY:-:0}" xdg-open "$url" >/dev/null 2>&1 &
  fi

  printf '%s\n' "$today" >"$NEXUS_PANEL_LAUNCH_MARKER"
  chmod 640 "$NEXUS_PANEL_LAUNCH_MARKER" 2>/dev/null || true
  nexus_log "INFO" "panel-launch" "PANEL_OPENED url=${url} user=${user}"
}

nexus_panel_install_desktop() {
  local root="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
  local port="${NEXUS_THREAT_PANEL_PORT:-9477}"
  local icon_src="${root}/assets/nexus-shield.png"
  local apps_dir="/usr/share/applications"
  local icon_dir="/usr/share/icons/hicolor/256x256/apps"
  local url="https://127.0.0.1:${port}/"

  [[ -f "$icon_src" ]] || return 0
  install -d -m 755 "$icon_dir" 2>/dev/null || return 0
  install -m 644 "$icon_src" "${icon_dir}/nexus-shield.png" 2>/dev/null || true

  install -m 755 "${root}/nexus.sh" /usr/local/bin/nexus.sh 2>/dev/null || true
  cat >"${apps_dir}/nexus-shield.desktop" <<EOF
[Desktop Entry]
Version=2.4.1
Type=Application
Name=NEXUS-Shield
GenericName=Network Gatekeeper
Comment=Open NEXUS connection gatekeeper panel
Exec=/usr/local/bin/nexus.sh
Icon=nexus-shield
Terminal=false
Categories=Security;Network;System;
Keywords=security;firewall;network;nexus;shield;
StartupNotify=true
EOF
  chmod 644 "${apps_dir}/nexus-shield.desktop" 2>/dev/null || true
  command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database /usr/share/applications 2>/dev/null || true
  nexus_log "INFO" "panel-launch" "DESKTOP_ENTRY installed nexus-shield.desktop"
}
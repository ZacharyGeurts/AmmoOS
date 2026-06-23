#!/bin/bash
# AMOURANTHRTX field learnings — whitelist common devices and consumer processes.

NEXUS_DEVICE_WHITELIST_COMM=(
  systemd
  systemd-logind
  dbus-daemon
  pipewire
  pipewire-pulse
  pulseaudio
  wireplumber
  bluetoothd
  NetworkManager
  wpa_supplicant
  Xorg
  Xwayland
  gnome-shell
  kwin_x11
  kwin_wayland
  sway
  hyprland
  firefox
  chrome
  chromium
  code
  cursor
  steam
  gamemoded
  cupsd
  colord
  udisksd
  upowerd
  ModemManager
  containerd
  dockerd
  nexus-daemon
)

nexus_device_whitelist_load() {
  if [[ -f "${NEXUS_INSTALL_ROOT}/config/device-whitelist.conf" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/config/device-whitelist.conf"
  fi
}

nexus_is_whitelisted_process() {
  local comm="${1:-}"
  local exe="${2:-}"
  nexus_device_whitelist_load
  local allowed
  for allowed in "${NEXUS_DEVICE_WHITELIST_COMM[@]}"; do
    [[ "$comm" == "$allowed" ]] && return 0
  done
  case "$exe" in
    /usr/bin/*|/usr/lib/*|/usr/libexec/*|/opt/*) return 0 ;;
  esac
  case "$comm" in
    nexus-*|stealth_*) return 0 ;;
  esac
  return 1
}

nexus_is_whitelisted_device_path() {
  local path="${1:-}"
  case "$path" in
    /dev/input/*|/dev/snd/*|/dev/dri/*|/dev/video*|/dev/tty*|/dev/usb/*|/dev/bus/usb/*) return 0 ;;
    /run/udev/*|/sys/class/input/*|/sys/class/sound/*) return 0 ;;
  esac
  return 1
}
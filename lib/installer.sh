#!/bin/bash
# NEXUS Field installer — Linux / macOS / Windows portable + system paths.
set -euo pipefail

nexus_install_detect_os() {
  case "$(uname -s)" in
    Linux) printf '%s' "linux" ;;
    Darwin) printf '%s' "macos" ;;
    MINGW*|MSYS*|CYGWIN*) printf '%s' "windows" ;;
    *) printf '%s' "unknown" ;;
  esac
}

nexus_install_check_deps() {
  local missing=0
  command -v python3 >/dev/null 2>&1 || command -v pythong >/dev/null 2>&1 || {
    echo "MISSING: python3 or pythong"
    missing=1
  }
  command -v curl >/dev/null 2>&1 || { echo "MISSING: curl"; missing=1; }
  case "$(nexus_install_detect_os)" in
    linux)
      for bin in zenity yad kdialog; do
        command -v "$bin" >/dev/null 2>&1 && break
      done || echo "OPTIONAL: zenity or yad (ZNetwork Yes/No/Skip dialog)"
      ;;
  esac
  return "$missing"
}

nexus_install_znetwork_src() {
  local root="${1:-}"
  local sg
  sg="$(cd "${root}/.." 2>/dev/null && pwd)" || sg="${SG_ROOT:-}"
  local zn=""
  for zn in "${sg}/ZNetwork" "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../ZNetwork" 2>/dev/null && pwd)"; do
    [[ -d "$zn" ]] || continue
    printf '%s' "$zn"
    return 0
  done
  return 1
}

nexus_install_build_znetwork() {
  local sg_root="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
  local zn
  zn="$(nexus_install_znetwork_src "$sg_root/NewLatest" 2>/dev/null || nexus_install_znetwork_src "$sg_root" 2>/dev/null || true)"
  [[ -n "$zn" && -d "$zn" ]] || return 0
  command -v cmake >/dev/null 2>&1 || {
    echo "OPTIONAL: cmake (build ZNetwork for Yes/No/Skip startup dialog)"
    return 0
  }
  echo "Building ZNetwork…"
  (
    cd "$zn"
    cmake -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build
  ) && echo "ZNetwork: ${zn}/build/znetwork"
}

nexus_install_ship_znetwork() {
  local dest_root="$1" zn="$2"
  [[ -n "$zn" && -d "$zn" ]] || return 0
  local ship="${dest_root}/znetwork"
  install -d -m 755 "${dest_root}/bin" "$ship/data"
  cp -a "${zn}/scripts" "$ship/" 2>/dev/null || true
  [[ -f "${zn}/data/review-checklist.json" ]] && \
    install -m 644 "${zn}/data/review-checklist.json" "$ship/data/" 2>/dev/null || true
  if [[ -x "${zn}/build/znetwork" ]]; then
    install -m 755 "${zn}/build/znetwork" "${dest_root}/bin/znetwork"
    echo "ZNetwork binary: ${dest_root}/bin/znetwork"
  fi
}

nexus_install_copy_payload() {
  local src="$1" dest="$2"
  install -d -m 755 "$dest"
  local dirs=(lib config panel data assets bin tests scripts Queen)
  local d
  for d in "${dirs[@]}"; do
    [[ -e "${src}/${d}" ]] || continue
    rm -rf "${dest}/${d}" 2>/dev/null || true
    cp -a "${src}/${d}" "${dest}/"
  done
  for f in nexus.sh nexus-launch.sh install.sh genius_shield.sh LICENSE README.md; do
    [[ -f "${src}/${f}" ]] || continue
    install -m 755 "${src}/${f}" "${dest}/${f}" 2>/dev/null || cp -a "${src}/${f}" "${dest}/"
  done
  chmod +x "${dest}/nexus.sh" "${dest}/nexus-launch.sh" "${dest}/install.sh" \
    "${dest}/genius_shield.sh" "${dest}/scripts/"*.sh 2>/dev/null || true
}

nexus_install_linux_desktop_user() {
  local root="$1" user="${2:-${SUDO_USER:-$USER}}"
  local home icon apps exec path
  home="$(getent passwd "$user" 2>/dev/null | cut -d: -f6)"
  [[ -n "$home" ]] || home="${HOME:-/home/$user}"
  icon="${root}/panel/assets/nexus-tray-us-64.png"
  [[ -f "$icon" ]] || icon="${root}/panel/assets/nexus-shield.png"
  if [[ -x /usr/local/bin/nexus.sh && "$root" == /usr/local/lib/nexus-shield ]]; then
    exec="/usr/local/bin/nexus.sh"
    path="/usr/local/lib/nexus-shield"
  else
    exec="${root}/nexus-launch.sh"
    path="${root}"
  fi
  apps="${home}/.local/share/applications"
  install -d -m 755 "$apps"
  cat >"${apps}/nexus-shield.desktop" <<EOF
[Desktop Entry]
Version=10.0
Type=Application
Name=NEXUS Field Command Center
GenericName=Field C2
Comment=Guarding Humanity — loopback HTTP panel + ZNetwork
Exec=${exec}
Icon=${icon}
Path=${path}
Terminal=false
Categories=Security;Network;System;
Keywords=security;firewall;nexus;field;znetwork;
StartupNotify=true
EOF
  chmod 644 "${apps}/nexus-shield.desktop"
  local tristate_exec="${exec}"
  [[ -f "${root}/nexus-install-gui.sh" ]] && tristate_exec="${root}/nexus-install-gui.sh"
  cat >"${apps}/nexus-tristate-installer.desktop" <<EOF
[Desktop Entry]
Version=10.0
Type=Application
Name=2026 Tristate Installer
GenericName=Field Underlay Install
Comment=Move under NEXUS/KILROY permanently — World_Redata WRDT1 · F9 hotkey
Exec=${tristate_exec}
Icon=${icon}
Path=${path}
Terminal=false
Categories=System;Settings;Security;
Keywords=nexus;underlay;kilroy;tristate;install;field;
StartupNotify=true
EOF
  chmod 644 "${apps}/nexus-tristate-installer.desktop"
  command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$apps" 2>/dev/null || true
  echo "Start menu: ${apps}/nexus-shield.desktop"
  echo "Start menu: ${apps}/nexus-tristate-installer.desktop"
}

nexus_install_macos_app() {
  local root="$1"
  local app="${HOME}/Applications/NEXUS-Field.app"
  local contents="${app}/Contents"
  install -d -m 755 "${contents}/MacOS" "${contents}/Resources"
  cat >"${contents}/MacOS/nexus-launch" <<EOF
#!/bin/bash
cd "${root}" && exec "${root}/nexus-launch.sh"
EOF
  chmod 755 "${contents}/MacOS/nexus-launch"
  [[ -f "${root}/panel/assets/nexus-tray-us-64.png" ]] && \
    cp "${root}/panel/assets/nexus-tray-us-64.png" "${contents}/Resources/nexus-field.png" 2>/dev/null || true
  cat >"${contents}/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>NEXUS Field</string>
  <key>CFBundleExecutable</key><string>nexus-launch</string>
  <key>CFBundleIdentifier</key><string>com.nexus.field</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleVersion</key><string>10.0.0</string>
</dict></plist>
EOF
  echo "Applications: ${app}"
}

nexus_install_portable() {
  local root="$1"
  local sg zn=""
  sg="$(cd "${root}/.." && pwd)"
  export SG_ROOT="${sg}"
  mkdir -p "${root}/.nexus-state"
  zn="$(nexus_install_znetwork_src "$root" 2>/dev/null || true)"
  nexus_install_build_znetwork "$sg" || true
  [[ -n "$zn" ]] && nexus_install_ship_znetwork "$root" "$zn" || true
  case "$(nexus_install_detect_os)" in
    linux) nexus_install_linux_desktop_user "$root" ;;
    macos) nexus_install_macos_app "$root" ;;
    windows)
      if command -v powershell.exe >/dev/null 2>&1; then
        powershell.exe -ExecutionPolicy Bypass -File "${root}/install/windows/install.ps1" -Portable -Root "$root"
      fi
      ;;
  esac
  echo "PORTABLE_OK root=${root}"
  echo "Launch: ${root}/nexus-launch.sh"
  echo "Panel:  http://127.0.0.1:9477/field"
}
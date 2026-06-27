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
  for f in nexus.sh install-all.sh install.sh LICENSE README.md; do
    [[ -f "${src}/${f}" ]] || continue
    install -m 755 "${src}/${f}" "${dest}/${f}" 2>/dev/null || cp -a "${src}/${f}" "${dest}/"
  done
  chmod +x "${dest}/nexus.sh" "${dest}/install-all.sh" "${dest}/install.sh" \
    "${dest}/scripts/"*.sh 2>/dev/null || true
}

nexus_install_resolve_launcher() {
  local root="$1"
  if [[ -x /usr/local/bin/nexus.sh && "$root" == /usr/local/lib/nexus-shield ]]; then
    printf '%s' "/usr/local/bin/nexus.sh"
  else
    printf '%s' "${root}/nexus.sh"
  fi
}

nexus_install_icon_src() {
  local root="$1"
  local candidate
  for candidate in \
    "${root}/Queen/world/assets/branding/amouranth-gentle.png" \
    "${root}/panel/assets/queen-browser.png" \
    "${root}/assets/nexus-field.png" \
    "${root}/panel/assets/nexus-field.png" \
    "${root}/panel/assets/nexus-field-256.png" \
    "${root}/panel/assets/nexus-shield.png" \
    "${root}/assets/nexus-shield.png"; do
    [[ -f "$candidate" ]] && printf '%s' "$candidate" && return 0
  done
  return 1
}

nexus_install_icon_theme() {
  local root="$1" scope="${2:-user}" user="${3:-${SUDO_USER:-$USER}}"
  local src sizes=(48 64 128 256) sz dir
  src="$(nexus_install_icon_src "$root" 2>/dev/null || true)"
  [[ -n "$src" ]] || return 0

  if [[ "$scope" == "system" && "$(id -u)" -eq 0 ]]; then
    for sz in "${sizes[@]}"; do
      local sized="${root}/panel/assets/nexus-field-${sz}.png"
      [[ -f "$sized" ]] || sized="$src"
      dir="/usr/share/icons/hicolor/${sz}x${sz}/apps"
      install -d -m 755 "$dir"
      install -m 644 "$sized" "${dir}/nexus-field.png" 2>/dev/null || true
    done
    command -v gtk-update-icon-cache >/dev/null 2>&1 && \
      gtk-update-icon-cache -f /usr/share/icons/hicolor 2>/dev/null || true
    return 0
  fi

  local home
  home="$(getent passwd "$user" 2>/dev/null | cut -d: -f6)"
  [[ -n "$home" ]] || home="${HOME:-/home/$user}"
  for sz in "${sizes[@]}"; do
    sized="${root}/panel/assets/nexus-field-${sz}.png"
    [[ -f "$sized" ]] || sized="$src"
    dir="${home}/.local/share/icons/hicolor/${sz}x${sz}/apps"
    mkdir -p "$dir" 2>/dev/null || true
    cp -f "$sized" "${dir}/nexus-field.png" 2>/dev/null || true
    chmod 644 "${dir}/nexus-field.png" 2>/dev/null || true
  done
  command -v gtk-update-icon-cache >/dev/null 2>&1 && \
    gtk-update-icon-cache -f "${home}/.local/share/icons/hicolor" 2>/dev/null || true
}

nexus_install_write_desktop() {
  local dest="$1" root="$2" exec="$3" ver="${4:-10.4.1}"
  cat >"$dest" <<EOF
[Desktop Entry]
Version=${ver}
Type=Application
Name=NEXUS Field Command Center
GenericName=Field C2
Comment=Queen field browser — NEXUS opens in Queen tabs — tray + ZNetwork
Exec=${exec}
Icon=queen-browser
Path=${root}
Terminal=false
Categories=Security;Network;System;
Keywords=security;firewall;nexus;field;znetwork;underlay;
StartupNotify=true
Actions=Underlay;Tray;

[Desktop Action Underlay]
Name=2026 Tristate Installer
Exec=${exec} --underlay

[Desktop Action Tray]
Name=Show Taskbar Icon
Exec=${exec} --tray
EOF
  chmod 644 "$dest" 2>/dev/null || true
}

nexus_install_desktop_shortcut() {
  local home="$1" exec="$2" root="$3"
  local desktop_dir="${home}/Desktop"
  [[ -d "$desktop_dir" ]] || return 0
  nexus_install_write_desktop "${desktop_dir}/nexus-field.desktop" "$root" "$exec"
  chmod +x "${desktop_dir}/nexus-field.desktop" 2>/dev/null || true
  command -v gio >/dev/null 2>&1 && \
    gio set "${desktop_dir}/nexus-field.desktop" metadata::trusted true 2>/dev/null || true
}

nexus_install_linux_desktop() {
  local root="$1" user="${2:-${SUDO_USER:-$USER}}" scope="${3:-user}"
  [[ -n "$user" && "$user" != "root" ]] || scope="system"
  local home exec path ver apps
  home="$(getent passwd "$user" 2>/dev/null | cut -d: -f6)"
  [[ -n "$home" ]] || home="${HOME:-/home/$user}"
  exec="$(nexus_install_resolve_launcher "$root")"
  path="${root}"
  ver="$(grep -o 'NEXUS_VERSION="[^"]*"' "${root}/lib/nexus-common.sh" 2>/dev/null | head -1 | cut -d'"' -f2)"
  ver="${ver:-10.4.1}"

  nexus_install_icon_theme "$root" "$scope" "$user"

  if [[ "$scope" == "system" && "$(id -u)" -eq 0 ]]; then
    apps="/usr/share/applications"
    install -d -m 755 "$apps"
    nexus_install_write_desktop "${apps}/nexus-field.desktop" "$root" "$exec" "$ver"
    rm -f "${apps}/nexus-shield.desktop" "${apps}/nexus-tristate-installer.desktop" 2>/dev/null || true
    command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$apps" 2>/dev/null || true
    echo "Start menu: ${apps}/nexus-field.desktop"
  fi

  apps="${home}/.local/share/applications"
  install -d -m 755 "$apps" 2>/dev/null || mkdir -p "$apps" 2>/dev/null || true
  nexus_install_write_desktop "${apps}/nexus-field.desktop" "$root" "$exec" "$ver"
  rm -f "${apps}/nexus-shield.desktop" "${apps}/nexus-tristate-installer.desktop" 2>/dev/null || true
  command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$apps" 2>/dev/null || true
  nexus_install_desktop_shortcut "$home" "$exec" "$root"
  echo "Start menu: ${apps}/nexus-field.desktop"
  echo "Launcher: ${exec}"
}

# Back-compat alias
nexus_install_linux_desktop_user() {
  nexus_install_linux_desktop "$1" "${2:-${SUDO_USER:-$USER}}" "user"
}

nexus_install_macos_app() {
  local root="$1"
  local app="${HOME}/Applications/NEXUS-Field.app"
  local contents="${app}/Contents"
  install -d -m 755 "${contents}/MacOS" "${contents}/Resources"
  cat >"${contents}/MacOS/nexus-launch" <<EOF
#!/bin/bash
cd "${root}" && exec "${root}/nexus.sh"
EOF
  chmod 755 "${contents}/MacOS/nexus-launch"
  local icon
  icon="$(nexus_install_icon_src "$root" 2>/dev/null || true)"
  [[ -n "$icon" ]] && cp "$icon" "${contents}/Resources/nexus-field.png" 2>/dev/null || true
  cat >"${contents}/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>NEXUS Field</string>
  <key>CFBundleExecutable</key><string>nexus-launch</string>
  <key>CFBundleIdentifier</key><string>com.nexus.field</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleVersion</key><string>10.4.1</string>
  <key>CFBundleIconFile</key><string>nexus-field</string>
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
  if [[ -f "${root}/Queen/scripts/queen-icon-kit.py" ]]; then
    python3 "${root}/Queen/scripts/queen-icon-kit.py" >/dev/null 2>&1 \
      || pythong "${root}/Queen/scripts/queen-icon-kit.py" >/dev/null 2>&1 || true
  fi
  zn="$(nexus_install_znetwork_src "$root" 2>/dev/null || true)"
  nexus_install_build_znetwork "$sg" || true
  [[ -n "$zn" ]] && nexus_install_ship_znetwork "$root" "$zn" || true
  case "$(nexus_install_detect_os)" in
    linux) nexus_install_linux_desktop "$root" "${USER:-}" "user" ;;
    macos) nexus_install_macos_app "$root" ;;
    windows)
      if command -v powershell.exe >/dev/null 2>&1; then
        powershell.exe -ExecutionPolicy Bypass -File "${root}/install/windows/install.ps1" -Portable -Root "$root"
      fi
      ;;
  esac
  echo "PORTABLE_OK root=${root}"
  echo "Launch: ${root}/nexus.sh"
  echo "Panel:  http://127.0.0.1:9477/field"
}
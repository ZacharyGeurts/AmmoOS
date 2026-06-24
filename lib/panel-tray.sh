#!/bin/bash
# NEXUS panel system tray — taskbar icon; click opens fast-track tab picker.

nexus_panel_tray_icon_path() {
  local state_icon="${NEXUS_STATE_DIR}/nexus-tray.png"
  local src=""
  for candidate in \
    "${NEXUS_INSTALL_ROOT}/panel/assets/nexus-tray-amouranth-24.png" \
    "${NEXUS_INSTALL_ROOT}/panel/assets/nexus-tray-amouranth.png" \
    "${NEXUS_INSTALL_ROOT}/panel/assets/amouranth-twitch-avatar.png" \
    "${NEXUS_INSTALL_ROOT}/panel/assets/nexus-shield.png" \
    "${NEXUS_INSTALL_ROOT}/assets/nexus-shield.png"; do
    if [[ -s "$candidate" ]]; then
      src="$candidate"
      break
    fi
  done
  if [[ -n "$src" ]] && command -v python3 >/dev/null 2>&1; then
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_TRAY_SRC="$src" \
      python3 -c "
from pathlib import Path
import os
from PIL import Image
install = Path(os.environ['NEXUS_INSTALL_ROOT'])
state = Path(os.environ['NEXUS_STATE_DIR'])
src = Path(os.environ.get('NEXUS_TRAY_SRC') or '')
if not src.is_file():
    for rel in ('panel/assets/nexus-tray-amouranth-24.png', 'panel/assets/nexus-tray-amouranth.png', 'panel/assets/amouranth-twitch-avatar.png'):
        p = install / rel
        if p.is_file():
            src = p
            break
out = state / 'nexus-tray.png'
stamp = state / 'nexus-tray-icon.stamp'
out.parent.mkdir(parents=True, exist_ok=True)
if src.is_file():
    st = src.stat()
    tag = f'{src}:{st.st_mtime_ns}:{st.st_size}'
    need = (not out.is_file()) or (not stamp.is_file()) or stamp.read_text(encoding='utf-8', errors='replace').strip() != tag
    if need:
        img = Image.open(src).convert('RGBA').resize((24, 24), Image.Resampling.LANCZOS)
        img.save(out, format='PNG')
        stamp.write_text(tag + '\n', encoding='utf-8')
" 2>/dev/null || true
  fi
  if [[ -s "$state_icon" ]]; then
    printf '%s' "$state_icon"
    return 0
  fi
}

nexus_panel_tray_icon_refresh() {
  rm -f "${NEXUS_STATE_DIR}/nexus-tray.png" "${NEXUS_STATE_DIR}/nexus-tray-icon.stamp" 2>/dev/null || true
  nexus_panel_tray_icon_path >/dev/null 2>&1 || true
}

nexus_panel_tray_is_running() {
  local pid_file="${NEXUS_STATE_DIR}/panel-tray.pid"
  [[ -f "$pid_file" ]] || return 1
  local pid
  pid="$(cat "$pid_file" 2>/dev/null || true)"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null \
    && pgrep -af "panel-tray.py" 2>/dev/null | grep -qE "(^|[[:space:]])${pid}([[:space:]]|$)"
}

nexus_panel_tray_prune_duplicates() {
  local keep_pid="${1:-}"
  local line pid
  while IFS= read -r line; do
    pid="${line%% *}"
    [[ -n "$pid" && "$pid" != "$keep_pid" ]] || continue
    kill "$pid" 2>/dev/null || true
  done < <(pgrep -f "${NEXUS_INSTALL_ROOT}/lib/panel-tray.py" 2>/dev/null || true)
}

nexus_panel_tray_start() {
  [[ "${NEXUS_PANEL_TRAY:-1}" == "1" ]] || return 0
  local script="${NEXUS_INSTALL_ROOT}/lib/panel-tray.py"
  [[ -f "$script" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]] || return 0

  nexus_panel_tray_icon_refresh

  if nexus_panel_tray_is_running; then
    local old_pid
    old_pid="$(cat "${NEXUS_STATE_DIR}/panel-tray.pid" 2>/dev/null || true)"
    nexus_panel_tray_prune_duplicates "$old_pid"
    nexus_log "INFO" "panel-tray" "TRAY_ALREADY_RUNNING pid=${old_pid}"
    return 0
  fi

  nexus_panel_tray_prune_duplicates ""

  local pid_file="${NEXUS_STATE_DIR}/panel-tray.pid"
  nohup env \
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    NEXUS_THREAT_PANEL_PORT="${NEXUS_THREAT_PANEL_PORT:-9477}" \
    NEXUS_PANEL_TLS="${NEXUS_PANEL_TLS:-1}" \
    NEXUS_TRAY_ICON_REFRESH=1 \
    DISPLAY="${DISPLAY:-:0}" \
    XDG_CURRENT_DESKTOP="${XDG_CURRENT_DESKTOP:-}" \
    python3 "$script" >>"${NEXUS_STATE_DIR}/panel-tray.log" 2>&1 &
  local pid=$!
  printf '%s\n' "$pid" >"$pid_file" 2>/dev/null || true
  sleep 0.4
  if kill -0 "$pid" 2>/dev/null; then
    nexus_log "INFO" "panel-tray" "TRAY_STARTED pid=${pid} port=${NEXUS_THREAT_PANEL_PORT:-9477}"
    echo "NEXUS tray icon active — click near the clock to pick a panel tab."
    return 0
  fi
  nexus_log "WARN" "panel-tray" "TRAY_START_FAILED see ${NEXUS_STATE_DIR}/panel-tray.log"
  return 1
}

nexus_panel_tray_stop() {
  pkill -f "${NEXUS_INSTALL_ROOT}/lib/panel-tray.py" 2>/dev/null || pkill -f "panel-tray.py" 2>/dev/null || true
  rm -f "${NEXUS_STATE_DIR}/panel-tray.pid" 2>/dev/null || true
}

nexus_panel_tray_watchdog_start() {
  [[ "${NEXUS_PANEL_TRAY:-1}" == "1" ]] || return 0
  [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]] || return 0
  local wd_pid="${NEXUS_STATE_DIR}/panel-tray-watchdog.pid"
  if [[ -f "$wd_pid" ]]; then
    local old
    old="$(cat "$wd_pid" 2>/dev/null || true)"
    if [[ -n "$old" ]] && kill -0 "$old" 2>/dev/null; then
      return 0
    fi
  fi
  nohup env \
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    NEXUS_THREAT_PANEL_PORT="${NEXUS_THREAT_PANEL_PORT:-9477}" \
    NEXUS_PANEL_TLS="${NEXUS_PANEL_TLS:-1}" \
    DISPLAY="${DISPLAY:-:0}" \
    bash -c '
      while true; do
        if ! source "'"${NEXUS_INSTALL_ROOT}"'/lib/nexus-common.sh" 2>/dev/null; then
          sleep 20
          continue
        fi
        # shellcheck source=/dev/null
        source "'"${NEXUS_INSTALL_ROOT}"'/lib/panel-tray.sh"
        if ! nexus_panel_tray_is_running; then
          nexus_panel_tray_start >/dev/null 2>&1 || true
        fi
        sleep 15
      done
    ' >>"${NEXUS_STATE_DIR}/panel-tray-watchdog.log" 2>&1 &
  printf '%s\n' "$!" >"$wd_pid" 2>/dev/null || true
}

nexus_panel_tray_install_autostart() {
  [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]] || return 0
  local home="${HOME:-/home/default}"
  local autostart="${home}/.config/autostart"
  local root="${NEXUS_INSTALL_ROOT}"
  local desktop="${autostart}/nexus-panel-tray.desktop"
  mkdir -p "$autostart" 2>/dev/null || return 0
  cat >"$desktop" <<EOF
[Desktop Entry]
Type=Application
Name=NEXUS-Shield Tray
Comment=NEXUS panel taskbar icon — fast tab picker
Exec=env NEXUS_INSTALL_ROOT=${root} NEXUS_STATE_DIR=${NEXUS_STATE_DIR:-/var/lib/nexus-shield} DISPLAY=:0 bash -c 'source ${root}/lib/nexus-common.sh; source ${root}/lib/panel-tray.sh; nexus_panel_tray_icon_refresh; nexus_panel_tray_start; nexus_panel_tray_watchdog_start'
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=3
StartupNotify=false
EOF
  chmod 644 "$desktop" 2>/dev/null || true
  nexus_log "INFO" "panel-tray" "AUTOSTART installed ${desktop}"
}

nexus_panel_open_tab() {
  local route="${1:-command}"
  local script="${NEXUS_INSTALL_ROOT}/lib/panel-tray.py"
  if [[ -f "$script" ]]; then
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    NEXUS_THREAT_PANEL_PORT="${NEXUS_THREAT_PANEL_PORT:-9477}" \
    NEXUS_PANEL_TLS="${NEXUS_PANEL_TLS:-1}" \
    DISPLAY="${DISPLAY:-:0}" \
      python3 "$script" open "$route" 2>/dev/null && return 0
  fi
  local url
  url="$(nexus_panel_url)#${route}"
  DISPLAY="${DISPLAY:-:0}" xdg-open "$url" >/dev/null 2>&1 &
}
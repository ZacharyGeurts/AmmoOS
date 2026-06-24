#!/bin/bash
# NEXUS panel system tray — taskbar icon with right-click tab picker.

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
out.parent.mkdir(parents=True, exist_ok=True)
if src.is_file():
    need = (not out.is_file()) or out.stat().st_mtime < src.stat().st_mtime
    if need:
        img = Image.open(src).convert('RGBA').resize((24, 24), Image.Resampling.LANCZOS)
        img.save(out, format='PNG')
" 2>/dev/null || true
  fi
  if [[ -s "$state_icon" ]]; then
    printf '%s' "$state_icon"
    return 0
  fi
}

nexus_panel_tray_start() {
  [[ "${NEXUS_PANEL_TRAY:-1}" == "1" ]] || return 0
  local script="${NEXUS_INSTALL_ROOT}/lib/panel-tray.py"
  [[ -f "$script" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]] || return 0

  nexus_panel_tray_icon_path >/dev/null 2>&1 || true

  local pid_file="${NEXUS_STATE_DIR}/panel-tray.pid"
  if [[ -f "$pid_file" ]]; then
    local old_pid
    old_pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null \
      && pgrep -af "panel-tray.py" 2>/dev/null | grep -q "$old_pid"; then
      nexus_log "INFO" "panel-tray" "TRAY_ALREADY_RUNNING pid=${old_pid}"
      return 0
    fi
  fi

  nohup env \
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    NEXUS_THREAT_PANEL_PORT="${NEXUS_THREAT_PANEL_PORT:-9477}" \
    NEXUS_PANEL_TLS="${NEXUS_PANEL_TLS:-1}" \
    DISPLAY="${DISPLAY:-:0}" \
    XDG_CURRENT_DESKTOP="${XDG_CURRENT_DESKTOP:-}" \
    python3 "$script" >>"${NEXUS_STATE_DIR}/panel-tray.log" 2>&1 &
  local pid=$!
  printf '%s\n' "$pid" >"$pid_file" 2>/dev/null || true
  sleep 0.3
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
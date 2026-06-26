#!/bin/bash
# NEXUS panel system tray — taskbar icon; click opens fast-track tab picker.

nexus_panel_tray_icon_path() {
  local state_icon="${NEXUS_STATE_DIR}/nexus-tray.png"
  local src=""
  for candidate in \
    "${NEXUS_INSTALL_ROOT}/panel/assets/nexus-field-24.png" \
    "${NEXUS_INSTALL_ROOT}/panel/assets/nexus-tray-us-24.png" \
    "${NEXUS_INSTALL_ROOT}/panel/assets/nexus-field.png" \
    "${NEXUS_INSTALL_ROOT}/assets/nexus-field.png" \
    "${NEXUS_INSTALL_ROOT}/panel/assets/nexus-tray-us.png" \
    "${NEXUS_INSTALL_ROOT}/panel/assets/nexus-shield.png" \
    "${NEXUS_INSTALL_ROOT}/assets/nexus-shield.png"; do
    if [[ -s "$candidate" ]]; then
      src="$candidate"
      break
    fi
  done
  if command -v pythong >/dev/null 2>&1 && [[ -f "${NEXUS_INSTALL_ROOT}/lib/panel-tray-icon.py" ]]; then
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
      pythong "${NEXUS_INSTALL_ROOT}/lib/panel-tray-icon.py" >/dev/null 2>&1 || true
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

# PIDs of long-running tray daemons (exclude short-lived `open` helper).
nexus_panel_tray_pids() {
  local line pid rest
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    pid="${line%% *}"
    rest="${line#"$pid" }"
    [[ "$rest" == *"panel-tray.py open"* ]] && continue
    [[ "$rest" == *"panel-tray.py"* ]] || continue
    printf '%s\n' "$pid"
  done < <(pgrep -af "[p]anel-tray\.py" 2>/dev/null || true)
}

nexus_panel_tray_is_running() {
  local pid
  while IFS= read -r pid; do
    [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null && return 0
  done < <(nexus_panel_tray_pids)
  return 1
}

nexus_panel_tray_prune_duplicates() {
  local keep_pid="${1:-}"
  local pid_file="${NEXUS_STATE_DIR}/panel-tray.pid"
  local -a pids=()
  mapfile -t pids < <(nexus_panel_tray_pids)
  if [[ ${#pids[@]} -eq 0 ]]; then
    rm -f "$pid_file" 2>/dev/null || true
    return 0
  fi
  if [[ -z "$keep_pid" ]]; then
    keep_pid="$(cat "$pid_file" 2>/dev/null || true)"
  fi
  if [[ -n "$keep_pid" ]] && ! kill -0 "$keep_pid" 2>/dev/null; then
    keep_pid=""
  fi
  if [[ -z "$keep_pid" ]]; then
    keep_pid="${pids[0]}"
  fi
  for pid in "${pids[@]}"; do
    [[ "$pid" == "$keep_pid" ]] && continue
    kill "$pid" 2>/dev/null || true
    sleep 0.1
    kill -9 "$pid" 2>/dev/null || true
  done
  printf '%s\n' "$keep_pid" >"$pid_file" 2>/dev/null || true
}

nexus_panel_tray_watchdog_pids() {
  local line pid
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    pid="${line%% *}"
    if [[ "$line" == *"nexus-panel-tray-watchdog"* ]] \
      || { [[ "$line" == *"while true"* ]] && [[ "$line" == *"panel-tray.sh"* ]] && [[ "$line" == *"nexus_panel_tray_start"* ]]; }; then
      printf '%s\n' "$pid"
    fi
  done < <(pgrep -af "bash -c" 2>/dev/null || true)
}

nexus_panel_tray_watchdog_prune() {
  local keep_pid="${1:-}"
  local wd_pid="${NEXUS_STATE_DIR}/panel-tray-watchdog.pid"
  local -a pids=()
  mapfile -t pids < <(nexus_panel_tray_watchdog_pids)
  if [[ ${#pids[@]} -eq 0 ]]; then
    rm -f "$wd_pid" 2>/dev/null || true
    return 0
  fi
  if [[ -z "$keep_pid" ]]; then
    keep_pid="$(cat "$wd_pid" 2>/dev/null || true)"
  fi
  if [[ -n "$keep_pid" ]] && ! kill -0 "$keep_pid" 2>/dev/null; then
    keep_pid=""
  fi
  if [[ -z "$keep_pid" ]]; then
    keep_pid="${pids[0]}"
  fi
  for pid in "${pids[@]}"; do
    [[ "$pid" == "$keep_pid" ]] && continue
    kill "$pid" 2>/dev/null || true
    sleep 0.1
    kill -9 "$pid" 2>/dev/null || true
  done
  printf '%s\n' "$keep_pid" >"$wd_pid" 2>/dev/null || true
}

nexus_panel_tray_start() {
  [[ "${NEXUS_PANEL_TRAY:-1}" == "1" ]] || return 0
  local script="${NEXUS_INSTALL_ROOT}/lib/panel-tray.py"
  [[ -f "$script" ]] || return 0
  command -v pythong >/dev/null 2>&1 || return 0
  [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]] || return 0

  local start_lock="${NEXUS_STATE_DIR}/panel-tray.start.lock"
  (
    flock -n 9 || {
      nexus_log "INFO" "panel-tray" "TRAY_START_SKIPPED flock_busy"
      exit 0
    }
    nexus_panel_tray_icon_refresh
    nexus_panel_tray_prune_duplicates ""

    if nexus_panel_tray_is_running; then
      local old_pid
      old_pid="$(cat "${NEXUS_STATE_DIR}/panel-tray.pid" 2>/dev/null || true)"
      nexus_log "INFO" "panel-tray" "TRAY_ALREADY_RUNNING pid=${old_pid}"
      exit 0
    fi

    local pid_file="${NEXUS_STATE_DIR}/panel-tray.pid"
    nohup env \
      NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
      NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
      NEXUS_THREAT_PANEL_PORT="${NEXUS_THREAT_PANEL_PORT:-9477}" \

      NEXUS_TRAY_ICON_REFRESH=1 \
      DISPLAY="${DISPLAY:-:0}" \
      XDG_CURRENT_DESKTOP="${XDG_CURRENT_DESKTOP:-}" \
      pythong "$script" >>"${NEXUS_STATE_DIR}/panel-tray.log" 2>&1 &
    local pid=$!
    printf '%s\n' "$pid" >"$pid_file" 2>/dev/null || true
    sleep 0.5
    nexus_panel_tray_prune_duplicates "$pid"
    if kill -0 "$pid" 2>/dev/null; then
      nexus_log "INFO" "panel-tray" "TRAY_STARTED pid=${pid} port=${NEXUS_THREAT_PANEL_PORT:-9477}"
      echo "NEXUS tray icon active — click near the clock to pick a panel tab."
      exit 0
    fi
    nexus_log "WARN" "panel-tray" "TRAY_START_FAILED see ${NEXUS_STATE_DIR}/panel-tray.log"
    exit 1
  ) 9>"$start_lock"
}

nexus_panel_tray_stop() {
  local pid
  for pid in $(nexus_panel_tray_pids); do
    kill "$pid" 2>/dev/null || true
    kill -9 "$pid" 2>/dev/null || true
  done
  pkill -f "${NEXUS_INSTALL_ROOT}/lib/panel-tray.py" 2>/dev/null || pkill -f "panel-tray.py" 2>/dev/null || true
  for pid in $(nexus_panel_tray_watchdog_pids); do
    kill "$pid" 2>/dev/null || true
    kill -9 "$pid" 2>/dev/null || true
  done
  pkill -f "nexus-panel-tray-watchdog" 2>/dev/null || true
  rm -f \
    "${NEXUS_STATE_DIR}/panel-tray.pid" \
    "${NEXUS_STATE_DIR}/panel-tray.lock" \
    "${NEXUS_STATE_DIR}/panel-tray.start.lock" \
    "${NEXUS_STATE_DIR}/panel-tray-watchdog.pid" \
    "${NEXUS_STATE_DIR}/panel-tray-watchdog.lock" \
    2>/dev/null || true
}

nexus_panel_tray_watchdog_start() {
  [[ "${NEXUS_PANEL_TRAY:-1}" == "1" ]] || return 0
  [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]] || return 0
  local wd_lock="${NEXUS_STATE_DIR}/panel-tray-watchdog.lock"
  if [[ -f "${NEXUS_STATE_DIR}/panel-tray-watchdog.pid" ]]; then
    local old
    old="$(cat "${NEXUS_STATE_DIR}/panel-tray-watchdog.pid" 2>/dev/null || true)"
    if [[ -n "$old" ]] && kill -0 "$old" 2>/dev/null; then
      nexus_panel_tray_watchdog_prune "$old"
      return 0
    fi
  fi
  nexus_panel_tray_watchdog_prune ""
  nohup env \
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    NEXUS_THREAT_PANEL_PORT="${NEXUS_THREAT_PANEL_PORT:-9477}" \

    DISPLAY="${DISPLAY:-:0}" \
    bash -c '
      # nexus-panel-tray-watchdog
      exec 9>"'"${wd_lock}"'"
      flock -n 9 || exit 0
      printf "%s\n" "$$" > "'"${NEXUS_STATE_DIR}/panel-tray-watchdog.pid"'"
      while true; do
        if ! source "'"${NEXUS_INSTALL_ROOT}"'/lib/nexus-common.sh" 2>/dev/null; then
          sleep 20
          continue
        fi
        # shellcheck source=/dev/null
        source "'"${NEXUS_INSTALL_ROOT}"'/lib/panel-tray.sh"
        nexus_panel_tray_watchdog_prune "$$"
        if ! nexus_panel_tray_is_running; then
          nexus_panel_tray_start >/dev/null 2>&1 || true
        else
          nexus_panel_tray_prune_duplicates "$(cat "'"${NEXUS_STATE_DIR}/panel-tray.pid"'" 2>/dev/null || true)"
        fi
        nexus_await_seconds 15 "'"${NEXUS_STATE_DIR}"'" 2>/dev/null || sleep 15
      done
    ' >>"${NEXUS_STATE_DIR}/panel-tray-watchdog.log" 2>&1 &
  sleep 0.2
  nexus_panel_tray_watchdog_prune "$!"
}

# Single entry: prune duplicates, one tray, one watchdog.
nexus_panel_tray_ensure_once() {
  nexus_panel_tray_prune_duplicates ""
  if ! nexus_panel_tray_is_running; then
    nexus_panel_tray_start 2>/dev/null || true
  fi
  nexus_panel_tray_watchdog_start 2>/dev/null || true
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
Name=NEXUS Field Tray
Comment=NEXUS Field taskbar icon — fast tab picker
Icon=nexus-field
Exec=env NEXUS_INSTALL_ROOT=${root} NEXUS_STATE_DIR=${NEXUS_STATE_DIR:-/var/lib/nexus-shield} DISPLAY=:0 bash -c 'source ${root}/lib/nexus-common.sh; source ${root}/lib/panel-tray.sh; nexus_panel_tray_icon_refresh; nexus_panel_tray_ensure_once'
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

    DISPLAY="${DISPLAY:-:0}" \
      pythong "$script" open "$route" 2>/dev/null && return 0
  fi
  local url
  url="$(nexus_panel_url)#${route}"
  DISPLAY="${DISPLAY:-:0}" xdg-open "$url" >/dev/null 2>&1 &
}
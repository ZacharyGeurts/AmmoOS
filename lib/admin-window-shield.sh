#!/bin/bash
# Admin window shield — interdict keyboard hooks and capture tools near operator admin UI.

nexus_admin_window_shield_enabled() {
  [[ "${NEXUS_ADMIN_WINDOW_SHIELD:-1}" == "1" ]]
}

nexus_admin_window_shield_once() {
  nexus_admin_window_shield_enabled || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/admin-window-shield.py"
  [[ -f "$py" ]] || return 0
  local pythong_bin="${NEXUS_PYTHONG:-$(nexus_resolve_pythong 2>/dev/null || true)}"
  [[ -n "$pythong_bin" ]] || return 0
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    "$pythong_bin" "$py" enforce >/dev/null 2>&1 || true
}

nexus_admin_window_shield_loop() {
  nexus_admin_window_shield_enabled || return 0
  while true; do
    nexus_admin_window_shield_once
    if declare -f nexus_field_loop_wait >/dev/null 2>&1; then
      nexus_field_loop_wait "${NEXUS_ADMIN_SHIELD_INTERVAL:-5}" "${NEXUS_STATE_DIR}"
    else
      local interval="${NEXUS_ADMIN_SHIELD_INTERVAL:-5}"
      nexus_await_seconds "$interval" "${NEXUS_STATE_DIR}" 2>/dev/null || sleep "$interval"
    fi
  done
}
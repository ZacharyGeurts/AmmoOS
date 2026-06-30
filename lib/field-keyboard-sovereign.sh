#!/bin/bash
# C2 keyboard sovereignty — engage on front-hook board, release on panel shutdown/kill.

nexus_keyboard_sovereign_enabled() {
  [[ "${NEXUS_KEYBOARD_SOVEREIGN:-1}" == "1" ]]
}

nexus_keyboard_sovereign_engage() {
  nexus_keyboard_sovereign_enabled || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-keyboard-sovereign.py"
  [[ -f "$py" ]] || return 0
  local runner="${NEXUS_PYTHONG:-pythong}"
  command -v "$runner" >/dev/null 2>&1 || runner="python3"
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    DISPLAY="${DISPLAY:-:0}" \
    "$runner" "$py" engage >/dev/null 2>&1 || true
  nexus_log "INFO" "keyboard-sovereign" "ENGAGE display=${DISPLAY:-:0}"
}

nexus_keyboard_sovereign_release() {
  local py="${NEXUS_INSTALL_ROOT}/lib/field-keyboard-sovereign.py"
  [[ -f "$py" ]] || return 0
  local runner="${NEXUS_PYTHONG:-pythong}"
  command -v "$runner" >/dev/null 2>&1 || runner="python3"
  local reason="${1:-shutdown}"
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    DISPLAY="${DISPLAY:-:0}" \
    "$runner" "$py" release "$reason" >/dev/null 2>&1 || true
  nexus_log "INFO" "keyboard-sovereign" "RELEASE reason=${reason}"
}
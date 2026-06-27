#!/bin/bash
# Field underlay — board drop-in replacement posture (guest inside protections).
set -euo pipefail

nexus_field_underlay_board() {
  [[ "${NEXUS_FIELD_UNDERLAY:-1}" == "1" ]] || return 0
  local root="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
  local py="${root}/lib/field-underlay.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${root}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}" \
    SG_ROOT="${SG_ROOT:-}" KILROY_ROOT="${KILROY_ROOT:-}" QUEEN_ROOT="${QUEEN_ROOT:-}" \
    pythong "$py" board 2>/dev/null || pythong "$py" json >/dev/null || true
  if [[ -f "${root}/lib/field-underlay-switch.sh" ]]; then
    # shellcheck source=/dev/null
    source "${root}/lib/field-underlay-switch.sh"
    nexus_underlay_switch_board
    [[ "${NEXUS_UNDERLAY_HOTKEY:-1}" == "1" ]] && nexus_underlay_hotkey_install "${SUDO_USER:-$USER}" 2>/dev/null || true
  fi
}
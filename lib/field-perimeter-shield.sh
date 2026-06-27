#!/bin/bash
# NEXUS Field Perimeter Shield — board network/wifi/BT/USB/ethernet/power/physical layers.
set -euo pipefail

nexus_perimeter_shield_board() {
  local root="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
  local py="${root}/lib/field-perimeter-shield.py"
  local enforce="${root}/lib/field-perimeter-enforce.sh"
  [[ -f "$py" ]] || return 0
  if [[ "$(id -u)" -eq 0 && "${NEXUS_PERIMETER_APPLY:-0}" == "1" && -f "$enforce" ]]; then
    # shellcheck source=/dev/null
    source "$enforce"
    nexus_perimeter_apply_all 2>/dev/null || true
  fi
  NEXUS_INSTALL_ROOT="${root}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}" \
    NEXUS_PERIMETER_APPLY="${NEXUS_PERIMETER_APPLY:-0}" \
    pythong "$py" board 2>/dev/null || pythong "$py" json >/dev/null || true
}

nexus_perimeter_shield_cycle() {
  [[ "${NEXUS_FIELD_PERIMETER:-1}" == "1" ]] || return 0
  nexus_perimeter_shield_board
}
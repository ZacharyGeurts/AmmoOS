#!/bin/bash
# Field wave strip — board voltage-is-voltage doctrine.
set -euo pipefail

nexus_wave_strip_board() {
  local root="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
  local py="${root}/lib/field-wave-strip.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${root}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}" \
    pythong "$py" board 2>/dev/null || pythong "$py" json >/dev/null || true
}

nexus_wave_shed_excess() {
  local root="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
  local py="${root}/lib/field-wave-shed.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${root}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}" \
    NEXUS_WAVE_SHED_APPLY="${NEXUS_WAVE_SHED_APPLY:-0}" \
    pythong "$py" shed 2>/dev/null || true
}


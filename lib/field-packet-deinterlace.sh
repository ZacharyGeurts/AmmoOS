#!/bin/bash
# Packet deinterlace — multi-path inspect/strip/clean/reconverge cycle.

nexus_packet_deinterlace_enabled() {
  [[ "${NEXUS_PACKET_DEINTERLACE:-1}" == "1" ]]
}

nexus_packet_deinterlace_cycle() {
  nexus_packet_deinterlace_enabled || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-packet-deinterlace.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    pythong "$py" cycle >/dev/null 2>&1 || true
}
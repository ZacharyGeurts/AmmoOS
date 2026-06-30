#!/bin/bash
# Firmware threat removal — scan + safe strip each vigil cycle.

nexus_firmware_threat_enabled() {
  [[ "${NEXUS_FIRMWARE_THREAT:-1}" == "1" ]]
}

nexus_firmware_threat_cycle() {
  nexus_firmware_threat_enabled || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-firmware-threat-removal.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    SG_ROOT="${SG_ROOT:-}" KILROY_ROOT="${KILROY_ROOT:-}" \
    NEXUS_FIRMWARE_APPLY="${NEXUS_FIRMWARE_APPLY:-1}" \
    pythong "$py" cycle >/dev/null 2>&1 || true
}
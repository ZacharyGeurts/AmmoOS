#!/bin/bash
# Plate meld — fuse all plates under flock each vigil cycle.

nexus_plate_meld_enabled() {
  [[ "${NEXUS_PLATE_MELD:-1}" == "1" ]]
}

nexus_plate_meld_cycle() {
  nexus_plate_meld_enabled || return 0
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/field-sense-package.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/field-sense-package.sh"
    nexus_sense_package_cycle
  fi
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/field-firmware-threat.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/field-firmware-threat.sh"
    nexus_firmware_threat_cycle
  fi
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/field-kernel-meld.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/field-kernel-meld.sh"
    nexus_kernel_meld_cycle
  fi
  local py="${NEXUS_INSTALL_ROOT}/lib/field-plate-meld.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    pythong "$py" meld >/dev/null 2>&1 || true
}
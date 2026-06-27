#!/bin/bash
# NEXUS Native Layer — THE native down to BIOS witness; no flash; everything lives with us.

nexus_native_layer_enabled() {
  [[ "${NEXUS_NATIVE_LAYER:-1}" == "1" ]]
}

nexus_native_layer_board() {
  nexus_native_layer_enabled || return 0
  mkdir -p "${NEXUS_STATE_DIR}" 2>/dev/null || true
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/native-layer.py" ]]; then
    SG_ROOT="${SG_ROOT:-$(cd "${NEXUS_INSTALL_ROOT}/.." 2>/dev/null && pwd)}"
    KILROY_ROOT="${KILROY_ROOT:-${SG_ROOT}/KILROY}"
    QUEEN_ROOT="${QUEEN_ROOT:-${SG_ROOT}/NewLatest/Queen}"
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    SG_ROOT="${SG_ROOT}" \
    KILROY_ROOT="${KILROY_ROOT}" \
    QUEEN_ROOT="${QUEEN_ROOT}" \
      pythong "${NEXUS_INSTALL_ROOT}/lib/native-layer.py" board >/dev/null 2>&1 || true
  fi
  nexus_log "INFO" "native-layer" "BOARD_HIT policy=witness_bios_no_flash lives_with_us=1"
}
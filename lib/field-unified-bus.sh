#!/bin/bash
# Unified field bus — pack data_bus[64] + copilot all lanes.

nexus_unified_bus_enabled() {
  [[ "${NEXUS_UNIFIED_BUS:-1}" == "1" ]]
}

nexus_unified_bus_cycle() {
  nexus_unified_bus_enabled || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-unified-bus.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    pythong "$py" cycle >/dev/null 2>&1 || true
}
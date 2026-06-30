#!/bin/bash
# NEXUS Smart Wire — secure keyboard path; no third-party middlemen.

nexus_smart_wire_enabled() {
  [[ "${NEXUS_SMART_WIRE:-1}" == "1" ]]
}

nexus_smart_wire_once() {
  nexus_smart_wire_enabled || return 0
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/hardware-wire.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/hardware-wire.sh"
    nexus_hardware_wire_once
    return 0
  fi
  local py="${NEXUS_INSTALL_ROOT}/lib/smart-wire.py"
  [[ -f "$py" ]] || return 0
  local pythong_bin="${NEXUS_PYTHONG:-$(nexus_resolve_pythong 2>/dev/null || true)}"
  [[ -n "$pythong_bin" ]] || return 0
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    "$pythong_bin" "$py" enforce >/dev/null 2>&1 || true
}

nexus_smart_wire_loop() {
  nexus_smart_wire_enabled || return 0
  while true; do
    nexus_smart_wire_once
    if declare -f nexus_field_loop_wait >/dev/null 2>&1; then
      nexus_field_loop_wait "${NEXUS_SMART_WIRE_INTERVAL:-5}" "${NEXUS_STATE_DIR}"
    else
      local interval="${NEXUS_SMART_WIRE_INTERVAL:-5}"
      nexus_await_seconds "$interval" "${NEXUS_STATE_DIR}" 2>/dev/null || sleep "$interval"
    fi
  done
}
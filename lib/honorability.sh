#!/bin/bash
# Honorability + browser awareness + operator location — panel publish helpers.

nexus_honorability_json() {
  local script="${NEXUS_INSTALL_ROOT}/lib/browser-awareness.py"
  if [[ ! -f "$script" ]]; then
    printf '{"active_sites":[],"honorability":{"entries":[]}}'
    return 0
  fi
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    python3 "$script" json 2>/dev/null || printf '{"active_sites":[],"honorability":{"entries":[]}}'
}

nexus_operator_location_json() {
  local script="${NEXUS_INSTALL_ROOT}/lib/operator-location.py"
  if [[ ! -f "$script" ]]; then
    printf '{"lat":null,"lon":null,"source":"unset"}'
    return 0
  fi
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    python3 "$script" json 2>/dev/null || printf '{"lat":null,"lon":null,"source":"unset"}'
}
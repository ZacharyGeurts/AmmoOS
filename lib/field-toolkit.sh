#!/bin/bash
# Field toolkit — attack study + automated defense panel helpers.

nexus_field_toolkit_json() {
  local script="${NEXUS_INSTALL_ROOT}/lib/field-toolkit-db.py"
  if [[ ! -f "$script" ]]; then
    script="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/field-toolkit-db.py"
  fi
  if [[ ! -f "$script" ]]; then
    printf '{"attack_count":0,"defenses":[]}'
    return 0
  fi
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    python3 "$script" json 2>/dev/null || printf '{"attack_count":0,"defenses":[]}'
}
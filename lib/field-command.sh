#!/bin/bash
# Field Command — unified Good Guy vs Bad Guy dashboard publish.

nexus_field_command_json() {
  local script="${NEXUS_INSTALL_ROOT}/lib/field-command.py"
  if [[ ! -f "$script" ]]; then
    printf '{"good_guy":{"count":0},"bad_guy":{"count":0},"pulse":{}}'
    return 0
  fi
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    pythong "$script" json 2>/dev/null \
    || printf '{"good_guy":{"count":0},"bad_guy":{"count":0},"pulse":{}}'
}
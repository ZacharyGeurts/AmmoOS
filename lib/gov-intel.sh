#!/bin/bash
# Government / law / police intel — panel publish helpers.

nexus_gov_intel_json() {
  local script="${NEXUS_INSTALL_ROOT}/lib/gov-intel-db.py"
  if [[ ! -f "$script" ]]; then
    printf '{"merge_only":true,"record_count":0}'
    return 0
  fi
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    pythong "$script" json 2>/dev/null || printf '{"merge_only":true,"record_count":0}'
}
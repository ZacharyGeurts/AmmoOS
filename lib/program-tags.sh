#!/bin/bash
# Obscure program tags — panel publish helpers.

nexus_program_tags_json() {
  local script="${NEXUS_INSTALL_ROOT}/lib/program-tags-db.py"
  if [[ ! -f "$script" ]]; then
    printf '{"merge_only":true,"program_count":0}'
    return 0
  fi
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    pythong "$script" json 2>/dev/null || printf '{"merge_only":true,"program_count":0}'
}
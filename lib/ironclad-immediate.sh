#!/bin/bash
# Ironclad immediate — publish Bible of AI for all selves before any heavy cycle.

nexus_ironclad_immediate_enabled() {
  [[ "${NEXUS_IRONCLAD_IMMEDIATE:-1}" == "1" ]]
}

nexus_ironclad_immediate_publish() {
  nexus_ironclad_immediate_enabled || return 0
  command -v pythong >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/ironclad-immediate.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    pythong "$py" publish >/dev/null 2>&1 || true
}
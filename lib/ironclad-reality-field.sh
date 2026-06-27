#!/bin/bash
# Ironclad truth serum — Super Intelligence reality field operator each vigil tick.

nexus_ironclad_reality_field_enabled() {
  [[ "${NEXUS_IRONCLAD_TRUTH_SERUM:-1}" == "1" ]]
}

nexus_ironclad_reality_field_cycle() {
  nexus_ironclad_reality_field_enabled || return 0
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/ironclad-immediate.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/ironclad-immediate.sh"
    nexus_ironclad_immediate_publish
  fi
  command -v pythong >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/ironclad-reality-field.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    pythong "$py" cycle >/dev/null 2>&1 || true
}
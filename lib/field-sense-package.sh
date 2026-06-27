#!/bin/bash
# Sense package meld — witness Final_Eye · Final_Ear · ZOCR · World_Redata each cycle.

nexus_sense_package_enabled() {
  [[ "${NEXUS_SENSE_PACKAGE:-1}" == "1" ]]
}

nexus_sense_package_cycle() {
  nexus_sense_package_enabled || return 0
  # Plate → eye/ear/mouth goldmine hot-read before sense witness meld
  if declare -F nexus_ironclad_immediate_publish >/dev/null 2>&1; then
    nexus_ironclad_immediate_publish
  elif [[ -f "${NEXUS_INSTALL_ROOT}/lib/ironclad-immediate.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/ironclad-immediate.sh"
    nexus_ironclad_immediate_publish
  fi
  local py="${NEXUS_INSTALL_ROOT}/lib/field-sense-package-meld.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    SG_ROOT="${SG_ROOT:-}" \
    FINAL_EYE_ROOT="${FINAL_EYE_ROOT:-}" \
    FINAL_EAR_ROOT="${FINAL_EAR_ROOT:-}" \
    ZOCR_ROOT="${ZOCR_ROOT:-}" \
    ZNEWOCR_ROOT="${ZNEWOCR_ROOT:-}" \
    WORLD_REDATA_ROOT="${WORLD_REDATA_ROOT:-}" \
    HOSTESS7_ROOT="${HOSTESS7_ROOT:-}" \
    HOSTESS7_TEAM_FIELD="${HOSTESS7_TEAM_FIELD:-}" \
    HOSTESS7_TEAM1_FIELD="${HOSTESS7_TEAM1_FIELD:-}" \
    HOSTESS7_NEXUS_CACHE="${HOSTESS7_NEXUS_CACHE:-}" \
    ZOCR_PORT="${ZOCR_PORT:-${FINAL_EYE_PORT:-9479}}" \
    WORLD_REDATA_WEB_PORT="${WORLD_REDATA_WEB_PORT:-9478}" \
    pythong "$py" meld >/dev/null 2>&1 || true
}
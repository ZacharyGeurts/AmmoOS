#!/bin/bash
# Hostess7 operator — autonomous NEXUS-Shield GitHub sync and field publish.

HOSTESS7_ROOT="${HOSTESS7_ROOT:-/home/default/Desktop/SG/Hostess7}"
# shellcheck source=/dev/null
[[ -f "${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}/lib/hostess7-field.sh" ]] \
  && source "${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}/lib/hostess7-field.sh"

nexus_hostess7_available() {
  [[ "${NEXUS_HOSTESS7_OPERATOR:-1}" == "1" ]] \
    && [[ -x "${HOSTESS7_ROOT}/Hostess7.sh" ]]
}

nexus_hostess7_sync_field() {
  nexus_hostess7_available || return 0
  [[ -x "${HOSTESS7_ROOT}/Hostess7.sh" ]] || return 0
  (
    cd "${HOSTESS7_ROOT}" || exit 0
    ./Hostess7.sh team-sync 2>/dev/null || true
  )
}

nexus_hostess7_nexus_update_plan() {
  nexus_hostess7_available || return 0
  local src
  src="$(hostess7_nexus_source 2>/dev/null || true)"
  [[ -n "$src" ]] || return 0
  NEXUS_SHIELD_SOURCE="$src" python3 "${HOSTESS7_ROOT}/scripts/field_nexus_shield.py" update 2>/dev/null || true
}

nexus_hostess7_autonomous_cycle() {
  [[ "${NEXUS_HOSTESS7_AUTONOMOUS:-1}" == "1" ]] || return 0
  nexus_hostess7_sync_field
  if declare -f nexus_hostess7_corroborate_integrity >/dev/null 2>&1; then
    nexus_hostess7_corroborate_integrity || true
  fi
  nexus_hostess7_nexus_update_plan
}
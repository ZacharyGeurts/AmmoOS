#!/bin/bash
# Police / public-safety interop — panel publish helpers.

nexus_police_agency_json() {
  local script="${NEXUS_INSTALL_ROOT}/lib/police-agency-db.py"
  if [[ ! -f "$script" ]]; then
    printf '{"agencies":[],"selected":null,"import_packs":[]}'
    return 0
  fi
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    python3 "$script" json 2>/dev/null \
    || printf '{"agencies":[],"selected":null,"import_packs":[]}'
}
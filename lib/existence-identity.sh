#!/bin/bash
# Persistent existence identity — panel publish helpers.

nexus_existence_identity_publish() {
  [[ "${NEXUS_EXISTENCE_IDENTITY:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local script="${NEXUS_INSTALL_ROOT}/lib/existence-identity.py"
  [[ -f "$script" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$script" build >/dev/null 2>&1 || true
}

nexus_existence_identity_json() {
  local script="${NEXUS_INSTALL_ROOT}/lib/existence-identity.py"
  if [[ ! -f "$script" ]]; then
    printf '{"table":[],"stats":{}}'
    return 0
  fi
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$script" json 2>/dev/null \
    || printf '{"table":[],"stats":{}}'
}
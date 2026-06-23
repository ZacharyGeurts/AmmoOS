#!/bin/bash
# NEXUS Host Attack Map — global threat globe for the panel.

nexus_host_attack_publish() {
  [[ "${NEXUS_HOST_ATTACK_MAP:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local script="${NEXUS_INSTALL_ROOT}/lib/host-attack-map.py"
  [[ -f "$script" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$script" build >/dev/null 2>&1 || true
}

nexus_host_attacks_json() {
  command -v python3 >/dev/null 2>&1 || { printf '{}'; return 0; }
  local script="${NEXUS_INSTALL_ROOT}/lib/host-attack-map.py"
  [[ -f "$script" ]] || { printf '{}'; return 0; }
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$script" json 2>/dev/null || printf '{}'
}
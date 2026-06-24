#!/bin/bash
# NEXUS panel plugins — registry publish helpers.

nexus_plugins_json() {
  local script="${NEXUS_INSTALL_ROOT}/lib/nexus-plugins.py"
  if [[ ! -f "$script" ]]; then
    printf '{"schema":"nexus.plugins/v1","registry":[],"outputs":{}}'
    return 0
  fi
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    python3 "$script" json 2>/dev/null \
    || printf '{"schema":"nexus.plugins/v1","registry":[],"outputs":{}}'
}

nexus_plugins_merge_panel() {
  local script="${NEXUS_INSTALL_ROOT}/lib/nexus-plugins.py"
  local panel="${NEXUS_THREAT_PANEL_JSON:-${NEXUS_STATE_DIR}/threat-panel.json}"
  [[ -f "$script" && -f "$panel" ]] || return 0
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    python3 "$script" merge "$panel" >/dev/null 2>&1 || true
}
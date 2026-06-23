#!/bin/bash
# NEXUS Kill Detect — zero-overhead execution when harm signature changes only.

nexus_kill_detect_execute() {
  [[ "${NEXUS_KILL_DETECT:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/kill-detect.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$py" execute >/dev/null 2>&1 || true
}

nexus_kill_detect_json() {
  local py="${NEXUS_INSTALL_ROOT}/lib/kill-detect.py"
  if [[ ! -f "$py" ]]; then
    printf '{"kill_count":0,"zero_cost_skip":true}'
    return 0
  fi
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$py" scan 2>/dev/null || printf '{"kill_count":0,"zero_cost_skip":true}'
}
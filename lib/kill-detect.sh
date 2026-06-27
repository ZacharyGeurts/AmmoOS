#!/bin/bash
# NEXUS Kill Detect — zero-overhead execution when harm signature changes only.

nexus_kill_detect_execute() {
  [[ "${NEXUS_KILL_DETECT:-1}" == "1" ]] || return 0
  if declare -f nexus_heavyboi_pending >/dev/null 2>&1; then
    nexus_heavyboi_pending >/dev/null 2>&1 || true
  fi
  command -v pythong >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/kill-detect.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$py" execute >/dev/null 2>&1 || true
  if declare -f nexus_field_attack_rekill_cycle >/dev/null 2>&1; then
    nexus_field_attack_rekill_cycle 1
  elif declare -f nexus_field_attack_auto_rekill >/dev/null 2>&1; then
    nexus_field_attack_auto_rekill >/dev/null 2>&1 || true
  fi
  if declare -f nexus_heaven_hell_rip >/dev/null 2>&1; then
    nexus_heaven_hell_rip
  fi
}

nexus_kill_detect_json() {
  local py="${NEXUS_INSTALL_ROOT}/lib/kill-detect.py"
  if [[ ! -f "$py" ]]; then
    printf '{"kill_count":0,"zero_cost_skip":true}'
    return 0
  fi
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$py" scan 2>/dev/null || printf '{"kill_count":0,"zero_cost_skip":true}'
}
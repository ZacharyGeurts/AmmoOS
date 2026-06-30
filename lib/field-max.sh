#!/bin/bash
# NEXUS Field Powered — smooth + cool; event-driven loops, workstation quota unlocked.

nexus_field_max_enabled() {
  [[ "${NEXUS_FIELD_MAX:-0}" == "1" ]]
}

nexus_field_loop_interval() {
  local fallback="${1:-5}"
  if nexus_field_max_enabled; then
    printf '%s' "${NEXUS_FIELD_LOOP_SEC:-2}"
    return 0
  fi
  printf '%s' "$fallback"
}

# Event-driven tick — inotify on state dir; no blocking sleep() in field-max mode.
nexus_field_loop_wait() {
  local interval watch
  interval="$(nexus_field_loop_interval "${1:-5}")"
  watch="${2:-${NEXUS_STATE_DIR:-/tmp}}"
  [[ -d "$watch" ]] || watch="/tmp"
  nexus_await_seconds "$interval" "$watch" 2>/dev/null || {
    nexus_field_max_enabled || sleep "$interval"
  }
}

nexus_field_cpu_wait() {
  if nexus_field_max_enabled; then
    nexus_field_loop_wait 2 "${NEXUS_STATE_DIR}"
    return 0
  fi
  sleep "${1:-15}"
}
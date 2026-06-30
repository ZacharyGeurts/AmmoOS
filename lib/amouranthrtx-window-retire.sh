#!/bin/bash
# Retire the legacy AMOURANTHRTX RTX window (queen-browser comp shader) — Queen web shell only.

amouranthrtx_window_retire_enabled() {
  [[ "${NEXUS_RETIRE_AMOURANTHRTX_WINDOW:-1}" == "1" || "${QUEEN_RETIRE_RTX_WINDOW:-1}" == "1" ]]
}

amouranthrtx_window_retire_patterns() {
  printf '%s\n' \
    'build/rtx/bin/Linux/queen-browser' \
    'build/rtx/bin/queen-browser' \
    'Queen/build/rtx/bin/Linux/queen-browser'
}

amouranthrtx_window_kill_by_wm() {
  command -v wmctrl >/dev/null 2>&1 || return 0
  local id title
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    id="${line%% *}"
    title="${line#* }"
    case "$title" in
      *AMOURANTHRTX*) wmctrl -ic "$id" 2>/dev/null || true ;;
    esac
  done < <(wmctrl -l 2>/dev/null || true)
}

amouranthrtx_window_kill_procs() {
  local pat killed=0
  for pat in $(amouranthrtx_window_retire_patterns); do
    if pgrep -f "$pat" >/dev/null 2>&1; then
      pkill -TERM -f "$pat" 2>/dev/null || true
      killed=1
    fi
  done
  if [[ "$killed" -eq 1 ]]; then
    sleep 0.35
    for pat in $(amouranthrtx_window_retire_patterns); do
      pkill -KILL -f "$pat" 2>/dev/null || true
    done
  fi
  amouranthrtx_window_kill_by_wm
}

amouranthrtx_window_retire_cycle() {
  amouranthrtx_window_retire_enabled || return 0
  amouranthrtx_window_kill_procs
}
#!/usr/bin/env bash
# Grok16 monitored runner — heartbeat + stall/timeout drop-out (no empty waits).
# Usage:
#   g16-run-monitored.sh <label> <timeout_sec> <command...>
#   g16-run-monitored.sh fn <label> <timeout_sec> <bash_function_name>
set -uo pipefail

GROK16_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MONITOR_PY="${GROK16_ROOT}/lib/g16_self_monitor.py"
HEARTBEAT_SEC="${G16_MONITOR_HEARTBEAT_SEC:-10}"
STALL_SEC="${G16_MONITOR_STALL_SEC:-}"

log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }

g16_monitor_cmd() {
  local label="$1" timeout_sec="$2"
  shift 2
  local stall="${STALL_SEC:-$((timeout_sec / 2))}"
  if (( stall < 30 )); then stall=30; fi
  python3 "$MONITOR_PY" run \
    --label "$label" \
    --timeout "$timeout_sec" \
    --stall "$stall" \
    --heartbeat "$HEARTBEAT_SEC" \
    -- "$@"
  return $?
}

g16_monitor_fn() {
  local label="$1" timeout_sec="$2" fn="$3"
  local stall="${STALL_SEC:-$((timeout_sec / 2))}"
  if (( stall < 30 )); then stall=30; fi
  local start last_activity pid rc out rc_file
  start=$(date +%s)
  last_activity=$start
  out="$(mktemp)"
  rc_file="${out}.rc"

  log "MONITOR START $label (timeout ${timeout_sec}s stall ${stall}s)"
  (
    "$fn" >"$out" 2>&1
    echo $? >"$rc_file"
  ) &
  pid=$!

  while kill -0 "$pid" 2>/dev/null; do
    local now elapsed stall_age mtime
    now=$(date +%s)
    elapsed=$((now - start))
    mtime=$(stat -c %Y "$out" 2>/dev/null || echo "$start")
    if (( mtime > last_activity )); then
      last_activity=$mtime
    fi
    stall_age=$((now - last_activity))

    if (( elapsed >= timeout_sec )); then
      log "MONITOR TIMEOUT $label after ${timeout_sec}s — dropping pid=$pid"
      kill -TERM "$pid" 2>/dev/null || true
      sleep 1
      kill -KILL "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
      rm -f "$out" "$rc_file"
      return 124
    fi

    if (( stall_age >= stall )) && (( elapsed >= HEARTBEAT_SEC )); then
      log "MONITOR STALL $label no output ${stall_age}s — dropping pid=$pid"
      kill -TERM "$pid" 2>/dev/null || true
      sleep 1
      kill -KILL "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
      rm -f "$out" "$rc_file"
      return 125
    fi

    if (( elapsed > 0 )) && (( elapsed % HEARTBEAT_SEC == 0 )); then
      log "MONITOR HEARTBEAT $label elapsed=${elapsed}s stall_age=${stall_age}s pid=$pid"
    fi
    sleep 1
  done

  wait "$pid" 2>/dev/null || true
  rc=1
  [[ -f "$rc_file" ]] && rc="$(cat "$rc_file")"
  cat "$out"
  rm -f "$out" "$rc_file"
  if [[ $rc -eq 0 ]]; then
    log "MONITOR PASS $label"
  else
    log "MONITOR FAIL $label exit=$rc"
  fi
  return "$rc"
}

case "${1:-}" in
  fn)
    shift
    g16_monitor_fn "$@"
    ;;
  cmd|"")
    if [[ "${1:-}" == "cmd" ]]; then shift; fi
    g16_monitor_cmd "$@" || exit $?
    ;;
  -h|--help|help)
    sed -n '2,6p' "$0"
    ;;
  *)
    g16_monitor_cmd "$@"
    ;;
esac
#!/usr/bin/env bash
# grok16-speed-demo — all toolchains: host g++ vs g16 belt/field profiles
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=grok16-config.sh
source "$SCRIPT_DIR/grok16-config.sh"

TARGET_SEC="${SPEED_DEMO_TARGET_SEC:-10}"
DASH_PORT="${SPEED_DASHBOARD_PORT:-9416}"

usage() {
  cat >&2 <<EOF
Usage: $0 [run|panel|dashboard|stage|exec|exec-dashboard]

  run            — wave-convert to single plane + field execution (~${TARGET_SEC}s each)
  panel          — terminal live dashboard
  dashboard      — open web UI + run benchmark
  stage          — one-time stage C/C++/CMake/Python runners (wave convert, not timed)
  exec           — field execution only from staged manifest (~${TARGET_SEC}s each)
  exec-dashboard — web UI + exec compare (no compile in timed path)

Environment:
  SPEED_DEMO_TARGET_SEC   seconds per runner (default: 10)
  SPEED_DASHBOARD_PORT    web UI port (default: 9416)
  SPEED_DEMO_BASELINE     baseline id for speedup (default: host_gcc_o2)
  FIELD_EXEC_BASELINE     exec compare baseline (default: cxx_host_o2)
EOF
  exit 2
}

launch_dashboard() {
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://127.0.0.1:${DASH_PORT}/" >/dev/null 2>&1 &
  fi
}

launch_panel_window() {
  if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal --title="Grok16 Speed Demo" -- bash -lc \
      "cd '$GROK16_ROOT' && python3 scripts/speed-demo-panel.py; echo; read -p 'Press Enter to close…'"
  elif command -v xterm >/dev/null 2>&1; then
    xterm -title "Grok16 Speed Demo" -e bash -lc \
      "cd '$GROK16_ROOT' && python3 scripts/speed-demo-panel.py; echo; read -p 'Press Enter…'" &
  else
    python3 "$SCRIPT_DIR/speed-demo-panel.py" &
  fi
}

cmd_run() {
  export GROK16_ROOT G16_PREFIX SPEED_DEMO_TARGET_SEC="${TARGET_SEC}"
  exec python3 "$SCRIPT_DIR/speed-demo-run.py"
}

cmd_stage() {
  export GROK16_ROOT G16_PREFIX
  exec python3 "$SCRIPT_DIR/field-exec-stage.py"
}

cmd_exec() {
  export GROK16_ROOT G16_PREFIX SPEED_DEMO_TARGET_SEC="${TARGET_SEC}"
  exec python3 "$SCRIPT_DIR/field-exec-compare.py"
}

cmd_dashboard() {
  export GROK16_ROOT G16_PREFIX SPEED_DEMO_TARGET_SEC="${TARGET_SEC}" SPEED_DASHBOARD_PORT="${DASH_PORT}"
  python3 "$SCRIPT_DIR/speed-dashboard-server.py" &
  local srv_pid=$!
  sleep 0.6
  launch_dashboard
  echo "speed-demo: dashboard http://127.0.0.1:${DASH_PORT}/"
  cmd_run
  kill "$srv_pid" 2>/dev/null || true
}

cmd_exec_dashboard() {
  export GROK16_ROOT G16_PREFIX SPEED_DEMO_TARGET_SEC="${TARGET_SEC}" SPEED_DASHBOARD_PORT="${DASH_PORT}"
  export SPEED_DEMO_MODE=exec
  python3 "$SCRIPT_DIR/speed-dashboard-server.py" &
  local srv_pid=$!
  sleep 0.6
  launch_dashboard
  echo "speed-demo: exec dashboard http://127.0.0.1:${DASH_PORT}/"
  cmd_exec
  kill "$srv_pid" 2>/dev/null || true
}

case "${1:-run}" in
  run)
    launch_panel_window
    sleep 0.5
    cmd_run
    ;;
  panel) exec python3 "$SCRIPT_DIR/speed-demo-panel.py" ;;
  dashboard) cmd_dashboard ;;
  stage) cmd_stage ;;
  exec) cmd_exec ;;
  exec-dashboard) cmd_exec_dashboard ;;
  *) usage ;;
esac
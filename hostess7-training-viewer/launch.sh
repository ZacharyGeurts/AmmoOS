#!/usr/bin/env bash
# Hostess 7 Training Viewer — personal side project. Opens in its own browser window.
set -euo pipefail

VIEWER_ROOT="$(cd "$(dirname "$0")" && pwd)"
NEXUS_TREE="$(cd "${VIEWER_ROOT}/.." && pwd)"

export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-${NEXUS_TREE}}"
export SG_ROOT="${SG_ROOT:-${NEXUS_INSTALL_ROOT}}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-${NEXUS_INSTALL_ROOT}/.nexus-state}"
export HOSTESS7_ROOT="${HOSTESS7_ROOT:-${NEXUS_INSTALL_ROOT}/Hostess7}"
export GROK16_ROOT="${GROK16_ROOT:-${NEXUS_INSTALL_ROOT}/Grok16}"
export H7_TRAINING_VIEWER_PORT="${H7_TRAINING_VIEWER_PORT:-9488}"

PY="${PY:-pythong}"
if ! command -v "$PY" >/dev/null 2>&1; then
  PY=python3
fi

URL="http://127.0.0.1:${H7_TRAINING_VIEWER_PORT}/"
PID_FILE="${VIEWER_ROOT}/.viewer.pid"
LOG="${VIEWER_ROOT}/viewer.log"

mkdir -p "${NEXUS_STATE_DIR}"

_running() {
  [[ -f "$PID_FILE" ]] || return 1
  local pid
  pid="$(cat "$PID_FILE" 2>/dev/null)" || return 1
  kill -0 "$pid" 2>/dev/null
}

if ! _running; then
  : >"$LOG"
  nohup "$PY" "${VIEWER_ROOT}/serve.py" >>"$LOG" 2>&1 &
  echo $! >"$PID_FILE"
  for _ in $(seq 1 30); do
    if curl -sf "${URL}api/health" >/dev/null 2>&1; then
      break
    fi
    sleep 0.2
  done
fi

_open() {
  local url="$1"
  if command -v google-chrome-stable >/dev/null 2>&1; then
    DISPLAY="${DISPLAY:-:0}" google-chrome-stable --app="$url" --window-size=1480,960 --new-window >/dev/null 2>&1 &
    return
  fi
  if command -v google-chrome >/dev/null 2>&1; then
    DISPLAY="${DISPLAY:-:0}" google-chrome --app="$url" --window-size=1480,960 --new-window >/dev/null 2>&1 &
    return
  fi
  if command -v chromium-browser >/dev/null 2>&1; then
    DISPLAY="${DISPLAY:-:0}" chromium-browser --app="$url" --window-size=1480,960 --new-window >/dev/null 2>&1 &
    return
  fi
  if command -v chromium >/dev/null 2>&1; then
    DISPLAY="${DISPLAY:-:0}" chromium --app="$url" --window-size=1480,960 --new-window >/dev/null 2>&1 &
    return
  fi
  if command -v firefox >/dev/null 2>&1; then
    DISPLAY="${DISPLAY:-:0}" firefox --new-window "$url" >/dev/null 2>&1 &
    return
  fi
  if command -v xdg-open >/dev/null 2>&1; then
    DISPLAY="${DISPLAY:-:0}" xdg-open "$url" >/dev/null 2>&1 &
    return
  fi
  echo "Open manually: $url"
}

case "${1:-open}" in
  stop)
    if _running; then
      kill "$(cat "$PID_FILE")" 2>/dev/null || true
      rm -f "$PID_FILE"
      echo "Training viewer stopped."
    else
      echo "Training viewer not running."
    fi
    ;;
  status)
    if _running; then
      echo "Running pid=$(cat "$PID_FILE") url=$URL"
      curl -sf "${URL}api/health" 2>/dev/null || true
    else
      echo "Stopped"
    fi
    ;;
  open|start|"")
    _open "$URL"
    echo "Hostess 7 Training Viewer → $URL"
    echo "STATE: $NEXUS_STATE_DIR"
    ;;
  *)
    echo "Usage: $0 [open|stop|status]" >&2
    exit 1
    ;;
esac
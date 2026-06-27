#!/usr/bin/env bash
# v10 baseline profiler — perf + py-spy under panel load (optional deps).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$ROOT/.nexus-state}"
OUT="${NEXUS_PROFILE_DIR:-$NEXUS_STATE_DIR/profile}"
mkdir -p "$OUT"

log() { echo "[$(date +%T)] $*"; }

log "Installing optional profilers (ignore failures)"
sudo apt-get install -y linux-perf bpftrace py-spy 2>/dev/null || true

log "Starting panel"
# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/panel-browser.sh"
"$ROOT/nexus.sh" --no-browser &
DAEMON_PID=$!
nexus_await_curl_ready "$(nexus_panel_app_url)" 5 5 || true

PANEL_PID="$(pgrep -f 'threat-panel-http.py' | head -1 || true)"
TARGET="${PANEL_PID:-$DAEMON_PID}"

if command -v perf >/dev/null 2>&1; then
  log "perf record 30s → $OUT/perf.data"
  sudo perf record -ag -o "$OUT/perf.data" -p "$TARGET" -- timeout 5s true 2>/dev/null || true
fi

if command -v py-spy >/dev/null 2>&1 && [[ -n "$TARGET" ]]; then
  log "py-spy → $OUT/profile.svg"
  py-spy record -o "$OUT/profile.svg" --duration 5 --pid "$TARGET" 2>/dev/null || true
fi

kill "$DAEMON_PID" 2>/dev/null || true
pkill -f 'threat-panel-http.py' 2>/dev/null || true

log "Done — inspect $OUT"

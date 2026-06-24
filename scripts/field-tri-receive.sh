#!/usr/bin/env bash
# 3-field GPS compare → pinpoint 83.1 MHz → play to your speakers.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"
export NEXUS_FIELD_CATCH_MHZ="${NEXUS_FIELD_CATCH_MHZ:-83.1}"
export NEXUS_FIELD_TRI_CONCEPT="${NEXUS_FIELD_TRI_CONCEPT:-1}"

PY="$ROOT/lib/field-tri-receive.py"
ORCH="$ROOT/lib/field-antenna-orchestrator.py"

usage() {
  cat <<EOF
NEXUS 3-field triangulation receive

  field-tri-receive.sh compare     Show 3 fields vs operator GPS
  field-tri-receive.sh pinpoint    Same as compare (pinpoint coords)
  field-tri-receive.sh listen      Pinpoint + capture + play (83.1 MHz)
  field-tri-receive.sh cycle       Full antenna cycle + listen

Requires RTL-SDR dongle for OTA audio:
  sudo apt install rtl-sdr sox pulseaudio-utils

Environment:
  NEXUS_STATE_DIR          State dir
  NEXUS_FIELD_CATCH_MHZ    Target MHz (default 83.1)
EOF
}

cmd="${1:-listen}"
shift || true

case "$cmd" in
  compare|pinpoint)
    exec python3 "$PY" compare "${NEXUS_FIELD_CATCH_MHZ}"
    ;;
  listen|receive|catch)
    echo "[field-tri] 3-field pinpoint → ${NEXUS_FIELD_CATCH_MHZ} MHz → speakers"
    if ! command -v rtl_fm >/dev/null 2>&1; then
      echo "[field-tri] WARN: rtl_fm not found — install: sudo apt install rtl-sdr sox"
    fi
    python3 "$ORCH" listen "{\"freq_mhz\":${NEXUS_FIELD_CATCH_MHZ},\"live_play\":true}"
    ;;
  cycle)
    python3 "$ORCH" cycle
    python3 "$PY" receive "{\"freq_mhz\":${NEXUS_FIELD_CATCH_MHZ}}"
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "Unknown: $cmd" >&2
    usage >&2
    exit 1
    ;;
esac
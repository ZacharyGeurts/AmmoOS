#!/bin/bash
# 93.1 WIMK — 3-field antenna catches OTA and plays station program.
set -euo pipefail
ROOT="${NEXUS_INSTALL_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$ROOT/.nexus-state}"
export NEXUS_FIELD_CATCH_MHZ="${NEXUS_FIELD_CATCH_MHZ:-93.1}"
export NEXUS_ANTENNA_MAX_ATTEMPTS="${NEXUS_ANTENNA_MAX_ATTEMPTS:-8}"

echo "=== 93.1 WIMK — 3-field antenna → play station ==="
pythong "$ROOT/lib/field-antenna-catch.py" catch \
  '{"freq_mhz":93.1,"station_id":"wimk-931","call_sign":"WIMK","play":true,"seconds":30}'
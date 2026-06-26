#!/bin/bash
# Field wave hardware — our field-wave-engine only (ported backends in lib/bin).
set -euo pipefail
ROOT="${NEXUS_INSTALL_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$ROOT/.nexus-state}"
export NEXUS_FIELD_CATCH_MHZ="${NEXUS_FIELD_CATCH_MHZ:-93.1}"

echo "=== Field wave engine — port backends ==="
NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
  pythong "$ROOT/lib/field-wave-engine.py" ensure

echo "=== Field wave ASM probe (field-fast) ==="
NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
  pythong "$ROOT/lib/field-wave-engine.py" probe

echo "=== Field instability @ ${NEXUS_FIELD_CATCH_MHZ} MHz ==="
NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
  pythong "$ROOT/lib/field-wave-tuner.py" tune \
  "{\"freq_mhz\":${NEXUS_FIELD_CATCH_MHZ},\"station_id\":\"wimk-931\",\"call_sign\":\"WIMK\",\"live_play\":true}"
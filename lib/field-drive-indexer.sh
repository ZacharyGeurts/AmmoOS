#!/usr/bin/env bash
# Field drive table indexer — prefetch all files, sovereign-now lookup.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${NEXUS_PYTHONG:-python3}"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$ROOT/.nexus-state}"
export SG_ROOT="${SG_ROOT:-$(cd "$ROOT/.." && pwd)}"

exec "$PY" "$ROOT/lib/field-drive-indexer.py" "$@"
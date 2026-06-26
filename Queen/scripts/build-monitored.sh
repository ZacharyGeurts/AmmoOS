#!/usr/bin/env bash
# Monitored native field build — delegates to live-build-field (g16 + ZOCR).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec "${ROOT}/scripts/live-build-field.sh" "$@"
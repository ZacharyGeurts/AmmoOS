#!/usr/bin/env bash
# Queen → Grok16 delegate — unified g16 @ 16.1.1, field_opt optimizations
set -euo pipefail
QUEEN="$(cd "$(dirname "$0")/.." && pwd)"
SG="$(cd "$QUEEN/../.." && pwd)"
GROK16_ROOT="${GROK16_ROOT:-$SG/Grok16}"
G16_SH="$GROK16_ROOT/scripts/grok16-toolchain.sh"

if [[ -f "$G16_SH" ]]; then
  export GROK16_ROOT GROK16_QUEEN_ROOT="${GROK16_QUEEN_ROOT:-$QUEEN}"
  export G16_PREFIX="${G16_PREFIX:-$GROK16_ROOT}"
  exec bash "$G16_SH" "${@:-status}"
fi

echo "Grok16 toolchain missing at $G16_SH — set GROK16_ROOT" >&2
exit 1
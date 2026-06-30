#!/usr/bin/env bash
# Regenerate all speed + comparison benchmarks and SVG charts.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=grok16-config.sh
source "$SCRIPT_DIR/grok16-config.sh"

export G16_BENCH_RUNS="${G16_BENCH_RUNS:-1}"
export G16_BENCH_PROFILE="${G16_BENCH_PROFILE:-field_opt}"
export SPEED_DEMO_TARGET_SEC="${SPEED_DEMO_TARGET_SEC:-3}"

log() { echo "[bench-refresh] $*"; }

if ! [[ -x "$G16_PREFIX/bin/g16" ]]; then
  log "WARN: g16 not ready — charts will use last JSON on disk"
fi

log "1/6 bench-triad (host gcc vs belt_1_0 vs belt_2_0)"
"$GROK16_SCRIPTS/grok16-bench-triad.sh" triad || log "triad skipped/failed"

log "2/6 bench-compare (field g16 vs host)"
"$GROK16_SCRIPTS/grok16-bench-compare.sh" compare || log "compare skipped/failed"

log "3/6 bench-all (profile suite)"
"$GROK16_SCRIPTS/grok16-toolchain.sh" bench-all || log "bench-all skipped/failed"

log "4/6 exec-comprehensive-bench (speed_demo full pipeline)"
python3 "$GROK16_SCRIPTS/field-exec-comprehensive-bench.py" || log "comprehensive bench partial"

log "5/6 bench-charts (SVG)"
python3 "$GROK16_SCRIPTS/grok16-bench-charts.py"

log "6/6 build-manual (HTML pages)"
python3 "$GROK16_ROOT/docs/build-manual.py" || true

log "DONE — charts in docs/assets/ · JSON in data/bench/ · docs/field-exec-full-bench.json"
#!/usr/bin/env bash
# Grok16 smoke battery — fast confirm (discern, smoke compile, hostess gate).
# Full verify + bench: grok16-toolchain.sh test-battery-full
# Host vs field speed: grok16-toolchain.sh bench-compare
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec "$ROOT/scripts/grok16-toolchain.sh" test-battery
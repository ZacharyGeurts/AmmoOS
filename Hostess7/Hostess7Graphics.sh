#!/usr/bin/env bash
# Hostess 7 Graphics — pixel + text window (GTK, not ASCII)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export NO_AT_BRIDGE=1 GTK_A11Y=none HOSTESS7_GFX_WINDOW=1
exec pythong "$ROOT/scripts/hostess7_gfx_window.py"
#!/usr/bin/env bash
# Prune old Grok harness terminal logs (PreToolUse hook — no env vars in hook JSON)
set -euo pipefail
TERMINALS="/home/default/.grok/projects/home-default-Desktop-SG/terminals"
mkdir -p "$TERMINALS" 2>/dev/null || exit 0
mapfile -t _old < <(ls -1t "$TERMINALS"/*.txt 2>/dev/null | tail -n +6) || true
((${#_old[@]})) && rm -f "${_old[@]}" || true
exit 0
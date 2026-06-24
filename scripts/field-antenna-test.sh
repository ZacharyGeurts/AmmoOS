#!/usr/bin/env bash
# Simple field tester — run on-site, adjust until blaster_ready.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export NEXUS_ROOT="$ROOT"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"

echo "=== NEXUS Field Antenna Tester ==="
echo "State: $NEXUS_STATE_DIR"
echo ""

"$ROOT/lib/field-antenna-launcher.sh" launch 12

echo ""
echo "--- Result ---"
"$ROOT/lib/field-antenna-launcher.sh" status

panel="$NEXUS_STATE_DIR/field-antenna-panel.json"
if python3 -c "
import json
p=json.load(open('$panel'))
ready=p.get('blaster_ready') or (p.get('readiness') or {}).get('blaster_ready')
raise SystemExit(0 if ready else 1)
" 2>/dev/null; then
  echo ""
  echo "BLASTER READY — all frequency knowledge online (RF, audio, laser, wired, BLE, sub-µm)"
  exit 0
fi

echo ""
echo "Not blaster-ready yet — run again in field or: sudo $ROOT/lib/field-antenna-launcher.sh launch 24"
exit 1
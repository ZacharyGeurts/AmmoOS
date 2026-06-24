#!/usr/bin/env bash
# Field antenna launcher — cycle, test, restart-until-blaster-ready.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ORCH="$ROOT/lib/field-antenna-orchestrator.py"
STATE="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"
export NEXUS_STATE_DIR="$STATE"
export NEXUS_ROOT="$ROOT"

usage() {
  cat <<'EOF'
NEXUS field antenna launcher

  field-antenna-launcher.sh cycle          One full detect + knowledge cycle
  field-antenna-launcher.sh test           Run blaster readiness test
  field-antenna-launcher.sh launch         Restart cycles until blaster_ready
  field-antenna-launcher.sh status         Print panel JSON summary
  field-antenna-launcher.sh blaster        Alias for launch (max 24 cycles)

Environment:
  NEXUS_STATE_DIR   State directory (default /var/lib/nexus-shield)
  NEXUS_ROOT        Project root
EOF
}

cmd="${1:-launch}"
shift || true

case "$cmd" in
  cycle)
    exec python3 "$ORCH" cycle "$@"
    ;;
  test)
    exec python3 "$ORCH" test "$@"
    ;;
  launch|blaster|restart)
    max="${1:-24}"
    echo "[field-antenna] Blaster launch — restart until ready (max $max cycles)"
    exec python3 "$ORCH" launch "$max"
    ;;
  status)
    panel="$STATE/field-antenna-panel.json"
    if [[ -f "$panel" ]]; then
      python3 -c "
import json,sys
p=json.load(open('$panel'))
print('blaster_ready:', p.get('blaster_ready') or (p.get('readiness') or {}).get('blaster_ready'))
print('cycles:', p.get('cycles'))
print('knowledge:', json.dumps(p.get('frequency_knowledge',{}), indent=2)[:2000])
print('test:', json.dumps(p.get('last_test',{}), indent=2)[:1500])
"
    else
      echo "No panel at $panel — run: $0 launch"
      exit 1
    fi
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "Unknown: $cmd" >&2
    usage >&2
    exit 1
    ;;
esac
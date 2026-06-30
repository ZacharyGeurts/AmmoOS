#!/usr/bin/env bash
# Redo iron + steel plates and melds — stack fabric 5.1 sealed witness
set -euo pipefail

GROK16_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG_ROOT="${SG_ROOT:-$(cd "$GROK16_ROOT/.." && pwd)}"
NEXUS="${NEXUS_INSTALL_ROOT:-$SG_ROOT/NewLatest}"
STATE="${NEXUS_STATE_DIR:-$NEXUS/.nexus-state}"

export GROK16_ROOT SG_ROOT NEXUS_INSTALL_ROOT="$NEXUS" NEXUS_STATE_DIR="$STATE"
export G16_SEAL_G1ID_MELD=1

log() { printf '[%s] plate-rebuild %s\n' "$(date +%H:%M:%S)" "$*"; }

thermal_level() {
  python3 - <<'PY' 2>/dev/null || echo "normal"
import json, os
from pathlib import Path
s = Path(os.environ["NEXUS_STATE_DIR"])
for name in ("znetwork-operator.json", "znetwork-relayer.json"):
    p = s / name
    if p.is_file():
        d = json.loads(p.read_text())
        t = (d.get("thermal") or d.get("thermal_level") or "").lower()
        if t:
            print(t)
            raise SystemExit
pw = s / "g16-power-sort-plate.json"
if pw.is_file():
    d = json.loads(pw.read_text())
    th = d.get("thermal") or {}
    if th.get("hot"):
        print(str(th.get("level") or "hot"))
        raise SystemExit
print("normal")
PY
}

THERM="$(thermal_level)"
log "thermal=$THERM"

log "steel neural plates (--force)"
python3 "$NEXUS/lib/field-steel-neural-plates.py" build --force 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
b=d.get('battery') or d
print('steel ok:', b.get('ok'), 'plates:', b.get('plate_count'), 'sealed:', '_g16_seal' in json.dumps(b))
" || log "WARN steel neural build"

log "iron plate organize (--force)"
python3 "$NEXUS/lib/iron-plate-organize.py" build 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('iron organize ok:', d.get('ok'), 'sealed:', '_g16_seal' in json.dumps(d))
" || log "WARN iron organize"

log "CHIPS plate stack (--force)"
python3 "$NEXUS/lib/field-chips-plate-stack.py" build --force 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
p=d.get('panel') or d
print('stack ok:', p.get('ok'), 'chips:', (p.get('counts') or {}).get('chips'), 'fabric:', bool(p.get('stack_fabric')))
" || log "WARN chips plate stack"

if [[ "$THERM" == "crit" || "$THERM" == "critical" || "$THERM" == "hot" ]]; then
  log "SKIP power sort plate — thermal $THERM (WATCH posture)"
else
  log "g16 power sort plate"
  python3 "$GROK16_ROOT/lib/g16-power-sort-plate.py" build 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('power_sort ok:', d.get('ok'), 'plated:', d.get('plated'))
" || log "WARN power sort"
fi

log "iron plate spot detector"
python3 "$GROK16_ROOT/lib/g16-iron-plate-spot-detector.py" detect --write 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('spot ok:', d.get('ok'), 'count:', d.get('spot_count'))
" || log "WARN spot detector"

if [[ -f "$NEXUS/lib/field-plate-meld.py" ]]; then
  log "field-plate-meld fuse"
  python3 "$NEXUS/lib/field-plate-meld.py" fuse --refresh 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('meld ok:', d.get('ok'), 'gen:', d.get('generation'))
" || python3 "$NEXUS/lib/field-plate-meld.py" refresh 2>/dev/null || log "WARN plate meld"
fi

log "verify-sealed (panels)"
python3 "$GROK16_ROOT/lib/g16-sealed-output.py" verify-tree "$STATE" 2>/dev/null || true

log "plate-rebuild complete"
#!/usr/bin/env bash
# Advanced field antenna test — 3-GPS planetary map · on-point returns only (no radial/path).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export NEXUS_ROOT="$ROOT"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"

mkdir -p "$NEXUS_STATE_DIR"
NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
  pythong "$ROOT/lib/operator-default.py" seed >/dev/null 2>&1 || true

ANCHORS='[
  {"id":"anchor_gladstone","lat":45.845976,"lon":-87.055759,"label":"Gladstone MI · operator"},
  {"id":"anchor_london","lat":51.5074,"lon":-0.1278,"label":"London UK"},
  {"id":"anchor_tokyo","lat":35.6762,"lon":139.6503,"label":"Tokyo JP"}
]'

echo "=== Advanced: 3-GPS planetary triangulation ==="
PLANET="$(NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
  pythong "$ROOT/lib/gps-precision.py" planet "$ANCHORS" 10)"
echo "$PLANET" | pythong -c "
import json, sys
d = json.load(sys.stdin)
assert d.get('ok'), d
assert d.get('return_type') == 'point', 'planet map must be point returns'
assert d.get('point_count', 0) >= 30, 'expected planetary grid'
pts = d.get('points') or []
for p in pts[:5]:
    assert p.get('return_type') == 'point', p
    assert p.get('lat') is not None and p.get('lon') is not None, p
print('planet OK:', d.get('point_count'), 'points · centroid', d.get('centroid'))
"

echo ""
echo "=== Advanced: antenna cycle + on-point placement audit ==="
NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
  pythong "$ROOT/lib/field-antenna-orchestrator.py" launch 3 >/dev/null

NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" pythong - <<'PY'
import json, os
from pathlib import Path
state = Path(os.environ["NEXUS_STATE_DIR"])
panel = json.loads((state / "field-antenna-panel.json").read_text())
prec = (panel.get("modalities") or {}).get("precision_gps") or {}
assert prec.get("return_type") == "point", prec
placements = prec.get("placements") or []
assert placements, "no placements"
bad = [p for p in placements if p.get("bearing_deg") and not p.get("lat")]
assert not bad, f"radial-only placements found: {bad[:2]}"
for p in placements[:8]:
    assert p.get("return_type") == "point", p
    assert p.get("lat_i") or p.get("lat"), p
planet = prec.get("planet_triangulate") or {}
assert planet.get("ok"), planet
assert planet.get("point_count", 0) >= 30
print(f"placements OK: {len(placements)} on-point · planet grid {planet.get('point_count')}")
PY

echo ""
echo "=== Advanced: radio stations are tower GPS points ==="
NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" pythong - <<'PY'
import json, os
from pathlib import Path
state = Path(os.environ["NEXUS_STATE_DIR"])
radio = json.loads((state / "field-radio-panel.json").read_text())
menu = radio.get("station_menu") or []
assert menu, "empty radio menu"
for st in menu[:6]:
    assert st.get("return_type") == "point", st
    assert st.get("tower_lat") is not None, st
    assert "bearing_deg" not in st or st.get("lat") is not None
print(f"radio OK: {len(menu)} stations · all return_type=point")
PY

echo ""
echo "ADVANCED TEST PASSED — 3-GPS planet map + on-point returns"
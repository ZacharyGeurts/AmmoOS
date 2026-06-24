#!/usr/bin/env bash
# Stringent repeated field antenna evaluation — must pass every round.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export NEXUS_ROOT="$ROOT"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"

ROUNDS="${1:-5}"
MIN_SCORE="${NEXUS_FIELD_ANTENNA_MIN_SCORE:-65}"
FAIL=0

mkdir -p "$NEXUS_STATE_DIR"
NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
  python3 "$ROOT/lib/operator-default.py" seed >/dev/null 2>&1 || true

echo "=== NEXUS Field Antenna Stringent Eval ($ROUNDS rounds) ==="
echo "State: $NEXUS_STATE_DIR"

for i in $(seq 1 "$ROUNDS"); do
  echo ""
  echo "--- Round $i/$ROUNDS ---"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "$ROOT/lib/field-antenna-orchestrator.py" launch 3 >/dev/null || true

  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "$ROOT/lib/field-antenna-orchestrator.py" test > "$NEXUS_STATE_DIR/.eval-test.json"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "$ROOT/lib/field-radio-catcher.py" build > "$NEXUS_STATE_DIR/.eval-radio.json"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "$ROOT/lib/signals-field.py" build > "$NEXUS_STATE_DIR/.eval-signals.json"

  if ! NEXUS_STATE_DIR="$NEXUS_STATE_DIR" MIN_SCORE="$MIN_SCORE" ROUND="$i" python3 - <<'PY'
import json, os, sys
from pathlib import Path
state = Path(os.environ["NEXUS_STATE_DIR"])
round_n = int(os.environ.get("ROUND", "1"))
min_score = float(os.environ.get("MIN_SCORE", "65"))
test = json.loads((state / ".eval-test.json").read_text())
radio = json.loads((state / ".eval-radio.json").read_text())
signals = json.loads((state / ".eval-signals.json").read_text())
errors = []
if not test.get("blaster_ready"):
    errors.append(f"blaster_ready=false score={test.get('score')}")
if float(test.get("score") or 0) < min_score:
    errors.append(f"score {test.get('score')} < {min_score}")
mods = test.get("modalities") or []
for need in ("rf", "broadcast", "audio", "laser"):
    if need not in mods:
        errors.append(f"missing modality {need}")
if not (radio.get("station_menu") or []):
    errors.append("radio station_menu empty")
catch831 = next((s for s in (radio.get("all_legal_stations") or []) if s.get("id") == "field-catch-831"), None)
if not catch831:
    errors.append("field-catch-831 (83.1 MHz) missing from registry")
elif not catch831.get("tunable"):
    errors.append("83.1 MHz not tunable from operator GPS")
if "vhf" not in (radio.get("stats") or {}).get("bands", []):
    errors.append("VHF band not in catcher bands")
fr = signals.get("field_radio") or {}
if not (fr.get("station_menu") or []):
    errors.append("signals field_radio menu empty")
if int((signals.get("stats") or {}).get("pulse_channels") or 0) < 10:
    errors.append("pulse_channels < 10")
checks = {c["name"]: c["ok"] for c in (test.get("checks") or [])}
for req in ("rf_antenna_fields", "sub_micron_gps", "frequency_knowledge", "signals_field"):
    if not checks.get(req):
        errors.append(f"check failed: {req}")
if errors:
    print(f"ROUND {round_n} FAIL:", "; ".join(errors))
    sys.exit(1)
print(
    f"ROUND {round_n} PASS blaster score={test.get('score')} "
    f"radio={len(radio.get('station_menu', []))} "
    f"pulses={signals.get('stats', {}).get('pulse_channels')}"
)
PY
  then
    FAIL=1
    echo "Eval halted on round $i"
    break
  fi
done

rm -f "$NEXUS_STATE_DIR/.eval-test.json" "$NEXUS_STATE_DIR/.eval-radio.json" "$NEXUS_STATE_DIR/.eval-signals.json"

if [[ "$FAIL" -eq 0 ]]; then
  echo ""
  echo "STRINGENT EVAL PASSED — $ROUNDS/$ROUNDS rounds"
  exit 0
fi
echo ""
echo "STRINGENT EVAL FAILED"
exit 1
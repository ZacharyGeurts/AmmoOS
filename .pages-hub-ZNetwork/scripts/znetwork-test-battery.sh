#!/usr/bin/env bash
# ZNetwork outside lab test battery — stringent smoke before SHADOW/field stream work.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE="${ZNETWORK_LAB_STATE:-$ROOT/.lab-state}"
RECEIPT="$STATE/test-battery-last.json"
BIN="${ZNETWORK_BIN:-$ROOT/build/znetwork}"
MATRIX="$ROOT/data/znetwork-lab-test-matrix.json"

mkdir -p "$STATE"
export ZNETWORK_OUTSIDE_LAB=1
PASS=0
FAIL=0
SKIP=0

log() { printf '[znetwork-battery] %s\n' "$*"; }
record() { python3 - "$@" <<'PY'
import json, sys, time
from pathlib import Path
receipt = Path(sys.argv[1])
rows = []
if receipt.is_file():
    try:
        rows = json.loads(receipt.read_text()).get("results") or []
    except json.JSONDecodeError:
        pass
rows.append(json.loads(sys.argv[2]))
receipt.write_text(json.dumps({
    "schema": "znetwork-test-battery/v1",
    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "results": rows,
}, indent=2) + "\n")
PY
}

run_probe() {
  if [[ ! -x "$BIN" ]]; then
    log "SKIP probe — binary missing (build with: cd build && CXX=g++ make)"
    SKIP=$((SKIP + 1))
    record "$RECEIPT" '{"id":"probe_json","status":"skip","reason":"binary_missing"}'
    return 0
  fi
  if "$BIN" probe --json | grep -q '"connection"'; then
    PASS=$((PASS + 1))
    record "$RECEIPT" '{"id":"probe_json","status":"pass"}'
    log "PASS probe_json"
  else
    FAIL=$((FAIL + 1))
    record "$RECEIPT" '{"id":"probe_json","status":"fail"}'
    log "FAIL probe_json"
    return 1
  fi
}

run_review_gate() {
  if bash "$ROOT/scripts/znetwork-review-gate.sh" >/dev/null 2>&1; then
    PASS=$((PASS + 1))
    record "$RECEIPT" '{"id":"review_gate","status":"pass"}'
    log "PASS review_gate"
  else
    FAIL=$((FAIL + 1))
    record "$RECEIPT" '{"id":"review_gate","status":"fail"}'
    log "FAIL review_gate"
    return 1
  fi
}

run_mode_active_blocked() {
  if [[ ! -x "$BIN" ]]; then
    SKIP=$((SKIP + 1))
    record "$RECEIPT" '{"id":"mode_active_blocked","status":"skip"}'
    return 0
  fi
  local out
  out="$(ZNETWORK_MODE=ACTIVE "$BIN" mode ACTIVE --json 2>/dev/null || true)"
  if echo "$out" | grep -q '"effective":"REVIEW_ONLY"'; then
    PASS=$((PASS + 1))
    record "$RECEIPT" '{"id":"mode_active_blocked","status":"pass"}'
    log "PASS mode_active_blocked"
  else
    FAIL=$((FAIL + 1))
    record "$RECEIPT" '{"id":"mode_active_blocked","status":"fail","out":'"$(python3 -c "import json; print(json.dumps('''$out'''))")"'}'
    log "FAIL mode_active_blocked (ACTIVE must not be effective)"
    return 1
  fi
}

run_mode_shadow_blocked_without_lab() {
  if [[ ! -x "$BIN" ]]; then
    SKIP=$((SKIP + 1))
    record "$RECEIPT" '{"id":"mode_shadow_blocked","status":"skip"}'
    return 0
  fi
  local out
  out="$(env -u ZNETWORK_OUTSIDE_LAB -u ZNETWORK_LAB_GATE_OK ZNETWORK_MODE=SHADOW "$BIN" mode SHADOW --json 2>/dev/null || true)"
  if echo "$out" | grep -qE '"effective":"(REVIEW_ONLY|SHADOW)"'; then
    # SHADOW without lab should downgrade to REVIEW_ONLY once mode.cpp updated; accept REVIEW_ONLY only as pass
    if echo "$out" | grep -q '"effective":"REVIEW_ONLY"'; then
      PASS=$((PASS + 1))
      record "$RECEIPT" '{"id":"mode_shadow_blocked","status":"pass"}'
      log "PASS mode_shadow_blocked_without_lab"
    else
      FAIL=$((FAIL + 1))
      record "$RECEIPT" '{"id":"mode_shadow_blocked","status":"fail","reason":"SHADOW effective without lab"}'
      log "FAIL SHADOW effective without lab gate"
      return 1
    fi
  else
    FAIL=$((FAIL + 1))
    log "FAIL mode_shadow_blocked — bad output"
    return 1
  fi
}

run_doctrine_wide_open_forbidden() {
  if python3 -c "import json; d=json.load(open('$ROOT/data/znetwork-outside-lab-doctrine.json')); assert d['policy']['wide_open_forbidden']"; then
    PASS=$((PASS + 1))
    record "$RECEIPT" '{"id":"wide_open_forbidden","status":"pass"}'
    log "PASS wide_open_forbidden doctrine"
  else
    FAIL=$((FAIL + 1))
    log "FAIL wide_open_forbidden"
    return 1
  fi
}

run_field_stream_locked() {
  if python3 -c "import json; d=json.load(open('$ROOT/data/review-checklist.json')); assert not d.get('field_stream_lab_approved')"; then
    PASS=$((PASS + 1))
    record "$RECEIPT" '{"id":"field_stream_locked","status":"pass"}'
    log "PASS field_stream_lab_approved is false (correct — not ready)"
  else
    FAIL=$((FAIL + 1))
    log "FAIL field_stream must stay locked in lab"
    return 1
  fi
}

run_python_sims() {
  for sim in handshake_sim fec_repair_sim thermal_vent_sim; do
    local py="$ROOT/tests/${sim}.py"
    if [[ ! -f "$py" ]]; then
      SKIP=$((SKIP + 1))
      record "$RECEIPT" "{\"id\":\"$sim\",\"status\":\"skip\"}"
      continue
    fi
    if python3 "$py"; then
      PASS=$((PASS + 1))
      record "$RECEIPT" "{\"id\":\"$sim\",\"status\":\"pass\"}"
      log "PASS $sim"
    else
      FAIL=$((FAIL + 1))
      record "$RECEIPT" "{\"id\":\"$sim\",\"status\":\"fail\"}"
      log "FAIL $sim"
      return 1
    fi
  done
}

log "=== ZNetwork outside lab test battery ==="
run_doctrine_wide_open_forbidden
run_field_stream_locked
run_review_gate
run_probe
run_mode_active_blocked
run_mode_shadow_blocked_without_lab
run_python_sims

python3 - <<PY
import json, time
from pathlib import Path
summary = {
    "schema": "znetwork-test-battery-summary/v1",
    "ok": $FAIL == 0,
    "pass": $PASS,
    "fail": $FAIL,
    "skip": $SKIP,
    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}
Path("$RECEIPT").write_text(json.dumps(summary, indent=2) + "\\n")
print(json.dumps(summary))
PY

if [[ "$FAIL" -gt 0 ]]; then
  log "BATTERY FAIL ($FAIL failures)"
  exit 1
fi
log "BATTERY OK ($PASS pass, $SKIP skip)"
export ZNETWORK_LAB_GATE_OK=1
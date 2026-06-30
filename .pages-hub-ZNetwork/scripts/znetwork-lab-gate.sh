#!/usr/bin/env bash
# ZNetwork outside lab gate — fails closed; no wide open, no field stream without lab approval.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE="${ZNETWORK_LAB_STATE:-$ROOT/.lab-state}"
RECEIPT="$STATE/lab-gate-last.json"
BIN="${ZNETWORK_BIN:-$ROOT/build/znetwork}"
CHECKLIST="$ROOT/data/review-checklist.json"

mkdir -p "$STATE"
export ZNETWORK_OUTSIDE_LAB=1

log() { printf '[znetwork-lab] %s\n' "$*"; }

fail() {
  log "BLOCKED: $*"
  python3 - <<PY
import json, time
from pathlib import Path
doc = {
    "schema": "znetwork-lab-gate/v1",
    "ok": False,
    "blocked": True,
    "reason": """$*""",
    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}
Path("$RECEIPT").write_text(json.dumps(doc, indent=2) + "\\n")
PY
  exit 1
}

# Wide-open / field stream hard blocks
if [[ "${ZNETWORK_FIELD_STREAM:-0}" == "1" ]]; then
  if ! python3 -c "import json; d=json.load(open('$CHECKLIST')); exit(0 if d.get('field_stream_lab_approved') else 1)"; then
    fail "FIELD_STREAM not lab-approved — set field_stream_lab_approved in checklist after FEC+thermal battery"
  fi
fi

if [[ "${ZNETWORK_MODE:-REVIEW_ONLY}" == "ACTIVE" ]]; then
  if ! grep -q '"approved": true' "$CHECKLIST" 2>/dev/null; then
    fail "ACTIVE requires approved=true in review-checklist.json"
  fi
  if [[ "${ZNETWORK_REVIEW_APPROVED:-0}" != "1" ]]; then
    fail "ACTIVE requires ZNETWORK_REVIEW_APPROVED=1"
  fi
fi

if [[ "${ZNETWORK_MODE:-REVIEW_ONLY}" == "SHADOW" ]]; then
  if [[ "${ZNETWORK_LAB_GATE_OK:-0}" != "1" ]]; then
    fail "SHADOW requires prior test battery — run scripts/znetwork-test-battery.sh"
  fi
fi

# Run test battery
if ! bash "$ROOT/scripts/znetwork-test-battery.sh"; then
  fail "test battery failed"
fi

python3 - <<PY
import json, time, os
from pathlib import Path
doc = {
    "schema": "znetwork-lab-gate/v1",
    "ok": True,
    "outside_lab": True,
    "wide_open_forbidden": True,
    "mode_requested": os.environ.get("ZNETWORK_MODE", "REVIEW_ONLY"),
    "field_stream": os.environ.get("ZNETWORK_FIELD_STREAM", "0") == "1",
    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}
Path("$RECEIPT").write_text(json.dumps(doc, indent=2) + "\\n")
PY

export ZNETWORK_LAB_GATE_OK=1
log "LAB GATE OK — NewLatest/ZNetwork (not wide open)"
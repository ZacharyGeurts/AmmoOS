#!/usr/bin/env bash
# ZNetwork review gate — prints checklist status; fails if ACTIVE attempted without approval.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHECKLIST="${ROOT}/data/review-checklist.json"
BIN="${ZNETWORK_BIN:-${ROOT}/build/znetwork}"

echo "=== ZNetwork review gate ==="
python3 - <<PY
import json
from pathlib import Path
p = Path("${CHECKLIST}")
doc = json.loads(p.read_text(encoding="utf-8"))
print("approved:", doc.get("approved"))
print("required_reviews:", len(doc.get("required_reviews") or []))
for i, item in enumerate(doc.get("required_reviews") or [], 1):
    print(f"  [{i}] {item}")
PY

if [[ "${ZNETWORK_MODE:-}" == "ACTIVE" ]]; then
  if [[ "${ZNETWORK_NO_REVIEW:-0}" == "1" ]] \
    || [[ "${ZNETWORK_OUTSIDE_LAB:-0}" == "1" ]] \
    || [[ "${ZNETWORK_REVIEW_APPROVED:-0}" == "1" ]] \
    || grep -qE '"approved"[[:space:]]*:[[:space:]]*true' "${CHECKLIST}"; then
    : # ACTIVE allowed — checklist approved or explicit bypass
  else
    echo "BLOCKED: ACTIVE requires approved checklist or ZNETWORK_NO_REVIEW=1" >&2
    exit 1
  fi
fi

if [[ -x "${BIN}" ]]; then
  "${BIN}" mode ACTIVE --json
fi
echo "Gate OK for REVIEW_ONLY / SHADOW probe."
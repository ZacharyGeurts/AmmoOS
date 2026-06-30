#!/usr/bin/env bash
# ZNetwork probe — REVIEW ONLY. Never replaces NetworkManager or touches links.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG="$(cd "${ROOT}/.." && pwd)"
BIN="${ZNETWORK_BIN:-${ROOT}/build/znetwork}"
CHECKLIST="${ROOT}/data/review-checklist.json"

export SG_ROOT="${SG}"
export ZNETWORK_MODE="${ZNETWORK_MODE:-REVIEW_ONLY}"

if [[ ! -x "${BIN}" ]]; then
  echo "ZNetwork binary missing — build first:" >&2
  echo "  cd ${ROOT} && cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build" >&2
  exit 1
fi

echo "=== ZNetwork probe (REVIEW_ONLY — no system mutation) ==="
"${BIN}" probe
echo ""
echo "Confirm dialog preview (JSON — run '${BIN} confirm' for Yes/No popup):"
"${BIN}" confirm --json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -30 || true
echo ""
"${BIN}" plan --json | python3 -m json.tool 2>/dev/null || "${BIN}" plan --json
echo ""
if grep -q '"approved": true' "${CHECKLIST}" 2>/dev/null; then
  echo "WARN: checklist approved=true — ACTIVE still needs ZNETWORK_REVIEW_APPROVED=1" >&2
else
  echo "Review gate: approved=false (safe — replacement disabled)" >&2
fi
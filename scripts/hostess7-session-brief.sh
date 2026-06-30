#!/usr/bin/env bash
# Brief Hostess 7 — operator Brief/Evaluate/Task + virtual workspace mandate.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-${ROOT}/.nexus-state}"
export HOSTESS7_ROOT="${HOSTESS7_ROOT:-${ROOT}/Hostess7}"
export PATH="${ROOT}/PythonG/bin:${PATH:-}"

PY="${NEXUS_PYTHONG:-pythong}"
command -v "$PY" >/dev/null 2>&1 || PY=python3

BRIEF='Hostess 7 mandate: Brief, Evaluate, Task. Edit yourself ONLY in virtual workspace — test CHIPS G16 Python die, debug, then promote with PROMOTE. Field tasks via ammolang-run.sh. AmmoOS: simple, informative, secure, protecting, no hostility.'

"$PY" "${ROOT}/lib/hostess7-operator.py" brief "$BRIEF" || true
"$PY" "${ROOT}/Hostess7/scripts/field_superintelligence.py" inbox "$BRIEF" || true
"$PY" "${ROOT}/lib/hostess7-virtual-workspace.py" ensure
"$PY" "${ROOT}/lib/hostess7-virtual-workspace.py" teach "virtual workspace chips debug"
"$PY" "${ROOT}/lib/hostess7-operator.py" catalog
"$PY" "${ROOT}/lib/hostess7-tasklist.py" seed
"$PY" "${ROOT}/lib/hostess7-tasklist.py" report
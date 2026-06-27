#!/usr/bin/env bash
# AmmoOS beta pipeline — wire SG, combinatronic rebalance, plate, engine build, integrate.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG_ROOT="${SG_ROOT:-$(cd "${ROOT}/.." && pwd)}"
export SG_ROOT NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$ROOT/.nexus-state}"
export TDIR="${TDIR:-${HOME}/.grok/projects/home-default-Desktop-SG/terminals}"
export GROK16_ROOT="${GROK16_ROOT:-$SG_ROOT/Grok16}"
export G16_PREFIX="${G16_PREFIX:-$GROK16_ROOT}"

log() { printf '[%s] ammooos %s\n' "$(date +%H:%M:%S)" "$*"; }

PY="${PY:-}"
if [[ -z "$PY" ]]; then
  if command -v pythong >/dev/null 2>&1; then PY=pythong
  elif command -v python3 >/dev/null 2>&1; then PY=python3
  else echo "no python" >&2; exit 1; fi
fi

log "wire SG stack siblings"
bash "${ROOT}/scripts/wire-stack.sh" || true

log "combinatronic optimal cycle (rebalance · condense · combine · connect)"
"$PY" "${ROOT}/lib/g16-combinatronic-rebalance.py" optimal > "${NEXUS_STATE_DIR}/ammoos-combinatronic-optimal.json" 2>/dev/null \
  || "$PY" "${ROOT}/lib/g16-combinatronic-rebalance.py" rebalance --force > "${NEXUS_STATE_DIR}/ammoos-combinatronic-rebalance.json" 2>/dev/null \
  || log "WARN combinatronic cycle partial"

if [[ -f "${ROOT}/lib/field-plate-meld.py" ]]; then
  log "plate meld fuse"
  "$PY" "${ROOT}/lib/field-plate-meld.py" fuse > "${NEXUS_STATE_DIR}/ammoos-plate-meld.json" 2>/dev/null || log "WARN plate meld skipped"
fi

if [[ -f "${GROK16_ROOT}/lib/field_combinatorics.py" ]]; then
  log "g16 combinatorics publish"
  python3 "${GROK16_ROOT}/lib/field_combinatorics.py" publish > "${NEXUS_STATE_DIR}/ammoos-g16-combinatorics.json" 2>/dev/null || true
fi

log "program combinatronic panel build"
"$PY" "${ROOT}/lib/field-program-combinatronic.py" build > "${NEXUS_STATE_DIR}/ammoos-program-panel.json" 2>/dev/null || true

log "integrate launch surfaces (browser + program registry)"
"$PY" - <<'PY'
import json
from pathlib import Path
import os

root = Path(os.environ["NEXUS_INSTALL_ROOT"])
state = Path(os.environ["NEXUS_STATE_DIR"])
ver = json.loads((root / "data/ammoos-version.json").read_text(encoding="utf-8"))

registry = {
    "schema": "ammoos-launch-registry/v1",
    "version": ver["version"],
    "browser": ver["surfaces"],
    "programs": [],
}
for rel in ver.get("native_programs", []):
    p = root / rel
    registry["programs"].append({
        "path": rel,
        "exists": p.is_file() or p.is_dir(),
        "kind": "native" if "Queen/build" in rel else "script",
    })

# Queen AmmoOS guest net plates
for fld in sorted((root / "Queen/AmmoOS/net").glob("*.fld")):
    registry.setdefault("plates", []).append({"plate": fld.name, "repo": "queen/ammoos"})

state.mkdir(parents=True, exist_ok=True)
out = state / "ammoos-launch-registry.json"
out.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"ok": True, "registry": str(out), "programs": len(registry["programs"])}, indent=2))
PY

QB="${ROOT}/Queen/build/rtx/bin/Linux/queen-browser"
if [[ ! -x "$QB" && -f "${ROOT}/Queen/lib/queen-forge.py" ]]; then
  log "engine build — queen-forge live_build_field (may take several minutes)"
  timeout 600 "$PY" "${ROOT}/Queen/lib/queen-forge.py" run live_build_field >> "${ROOT}/Queen/.queen-forge.log" 2>&1 \
    || log "WARN queen-forge build incomplete — browser surfaces still available via panel HTTP"
else
  log "engine ready — queen-browser $( [[ -x "$QB" ]] && echo present || echo absent )"
fi

if [[ -x "${ROOT}/scripts/ammoos-launch-verify.sh" ]]; then
  bash "${ROOT}/scripts/ammoos-launch-verify.sh" || log "WARN launch verify partial"
fi

log "pipeline complete — state in ${NEXUS_STATE_DIR}"
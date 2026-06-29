#!/usr/bin/env bash
# Compiler stack ready — Grok16 + AmmoCode + Vulkan OS doctrine + Queen probe.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUEEN="${QUEEN_ROOT:-${ROOT}/Queen}"
PY="${QUEEN}/scripts/queen-py"

# shellcheck source=/dev/null
source "${ROOT}/lib/sg-paths.sh"
sg_paths_export_defaults

log() { printf '[integrate-compiler] %s\n' "$*"; }

echo "=== Compiler stack integrate ==="
log "Grok16:   ${GROK16_ROOT}"
log "AmmoCode: ${AMMOCODE_ROOT:-${ROOT}/AmmoCode}"
log "Vulkan:   ${ROOT}/data/vulkan-os-doctrine.json"

bash "${ROOT}/scripts/wire-stack.sh" 2>&1 | tail -3

if [[ -x "${GROK16_ROOT}/scripts/grok16-integrate.sh" ]]; then
  bash "${GROK16_ROOT}/scripts/grok16-integrate.sh" integrate || log "WARN grok16 integrate partial"
fi

bash "${ROOT}/scripts/sync-programming-filetypes.sh" 2>&1 | tail -3 || true
bash "${ROOT}/scripts/integrate-ammocode.sh"

if [[ -f "${PY}" && -f "${QUEEN}/lib/queen-forge.py" ]]; then
  log "compiler_probe"
  "${PY}" "${QUEEN}/lib/queen-forge.py" run compiler_probe || log "WARN compiler_probe"
fi

python3 - <<PY
import json
from pathlib import Path
root = Path("${ROOT}")
doc = json.loads((root / "data/vulkan-os-doctrine.json").read_text(encoding="utf-8"))
state = Path("${ROOT}/.nexus-state")
state.mkdir(parents=True, exist_ok=True)
(state / "vulkan-os-doctrine.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
print("vulkan-os-doctrine mirrored to .nexus-state")
PY

if [[ -x "${ROOT}/scripts/integrate-amouranthrtx.sh" ]]; then
  bash "${ROOT}/scripts/integrate-amouranthrtx.sh" || log "WARN amouranthrtx integrate partial"
fi

log "compiler stack ready"
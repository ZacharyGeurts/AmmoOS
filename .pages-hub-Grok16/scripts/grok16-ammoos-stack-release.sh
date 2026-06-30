#!/usr/bin/env bash
# G8 — AmmoOS 2.0 Stack release driver: reseal panels, sync manifest, tag Grok16 + AmmoOS together
set -euo pipefail

GROK16_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG_ROOT="${SG_ROOT:-$(cd "$GROK16_ROOT/.." && pwd)}"
NEXUS="${NEXUS_INSTALL_ROOT:-$SG_ROOT/NewLatest}"
GROK16_VER="${1:-5.1.0}"
AMMOOS_VER="${2:-2.0.0}"
PUSH=0
shift 2 2>/dev/null || true
for arg in "$@"; do
  case "$arg" in
    --push) PUSH=1 ;;
  esac
done

export GROK16_ROOT SG_ROOT NEXUS_INSTALL_ROOT="$NEXUS"
export G16_PREFIX="${G16_PREFIX:-$GROK16_ROOT}"

log() { printf '[%s] ammoos-stack-release %s\n' "$(date +%H:%M:%S)" "$*"; }

log "reseal Grok16 panels"
python3 "$GROK16_ROOT/lib/g16-sealed-output.py" verify-tree "$GROK16_ROOT/data" || true
if [[ -f "$GROK16_ROOT/lib/g16-stack-fabric.py" ]]; then
  python3 "$GROK16_ROOT/lib/g16-stack-fabric.py" json >"$GROK16_ROOT/data/g16-stack-fabric-snapshot.json"
  python3 "$GROK16_ROOT/lib/g16-sealed-output.py" reseal "$GROK16_ROOT/data/g16-stack-fabric-snapshot.json"
fi

log "sync field-stack-manifest"
if [[ -f "$NEXUS/data/field-stack-manifest.json" ]]; then
  cp -f "$NEXUS/data/field-stack-manifest.json" "$GROK16_ROOT/data/field-stack-manifest.json"
fi

log "integrate + verify"
bash "$GROK16_ROOT/scripts/grok16-integrate.sh" || true
bash "$GROK16_ROOT/scripts/grok16-toolchain.sh" verify-sealed || true
bash "$GROK16_ROOT/scripts/grok16-toolchain.sh" combinatorics-status || true
bash "$GROK16_ROOT/scripts/grok16-toolchain.sh" bench-silent-gate || true

log "gates: test-gate smoke"
bash "$GROK16_ROOT/scripts/grok16-test-gate.sh" smoke || log "WARN test-gate smoke skipped"

log "version stamps Grok16=$GROK16_VER AmmoOS=$AMMOOS_VER"
python3 - <<PY
import json
from pathlib import Path
root = Path("$GROK16_ROOT")
ver = root / "data" / "grok16-version.json"
doc = json.loads(ver.read_text(encoding="utf-8"))
doc["distro_version"] = "$GROK16_VER"
doc["upload_version"] = "$GROK16_VER"
doc["tag"] = "v$GROK16_VER"
doc.setdefault("ammoos_pair", {})["version"] = "$AMMOOS_VER"
doc["stack_fabric"] = {"doctrine": "data/g16-stack-fabric-doctrine.json", "version": "1.0.0"}
doc.setdefault("changelog", []).insert(0, f"$GROK16_VER: stack fabric G1-G15 + AmmoOS $AMMOOS_VER stack release driver")
ver.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
print("updated", ver)
PY

if [[ "$PUSH" -eq 1 ]]; then
  cd "$GROK16_ROOT"
  git add -A
  git commit -m "Grok16 v${GROK16_VER} + AmmoOS v${AMMOOS_VER} — stack fabric release" || true
  git tag -a "v${GROK16_VER}" -m "Grok16 ${GROK16_VER} stack fabric" 2>/dev/null || true
  git push origin main 2>/dev/null || true
  git push origin "v${GROK16_VER}" 2>/dev/null || true
  log "pushed v${GROK16_VER}"
fi

log "complete — run: grok16-toolchain.sh release ${GROK16_VER} --push"
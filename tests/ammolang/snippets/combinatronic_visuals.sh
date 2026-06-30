#!/bin/bash
set -euo pipefail
set +o pipefail
ROOT="/home/default/Desktop/SG/NewLatest"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/home/default/Desktop/SG/NewLatest/.nexus-state}"
export SG_ROOT="${SG_ROOT:-/home/default/Desktop/SG}"
export AML_INLINE=1
PY=python3
if [[ "${AML_TEST_DIRECT:-0}" != "1" ]] && command -v pythong >/dev/null 2>&1; then
  PY=pythong
fi
mkdir -p "$NEXUS_STATE_DIR"
source "$ROOT/lib/nexus-common.sh" 2>/dev/null || true
source "$ROOT/lib/eternal-vigil.sh" 2>/dev/null || true
source "$ROOT/lib/entropy-oracle.sh" 2>/dev/null || true
source "$ROOT/lib/shadow-reality.sh" 2>/dev/null || true
source "$ROOT/lib/self-defense.sh" 2>/dev/null || true
source "$ROOT/lib/device-whitelist.sh" 2>/dev/null || true
source "$ROOT/lib/ultra-stealth.sh" 2>/dev/null || true
source "$ROOT/lib/predictive-guard.sh" 2>/dev/null || true
source "$ROOT/lib/network-lockdown.sh" 2>/dev/null || true
source "$ROOT/lib/threat-vectors.sh" 2>/dev/null || true
source "$ROOT/lib/packet-oracle.sh" 2>/dev/null || true
source "$ROOT/lib/threat-panel.sh" 2>/dev/null || true
source "$ROOT/lib/firewall-sentinel.sh" 2>/dev/null || true
source "$ROOT/lib/firewall-trust.sh" 2>/dev/null || true
source "$ROOT/lib/seal-vault.sh" 2>/dev/null || true
source "$ROOT/lib/tamper-guard.sh" 2>/dev/null || true
source "$ROOT/lib/znetwork-field.sh" 2>/dev/null || true
source "$ROOT/lib/nexus-settings.sh" 2>/dev/null || true
source "$ROOT/lib/adblock-loader.sh" 2>/dev/null || true
source "$ROOT/lib/host-attack.sh" 2>/dev/null || true
source "$ROOT/lib/field-attack-kit.sh" 2>/dev/null || true
nexus_ensure_dirs 2>/dev/null || true
panel="$ROOT/panel/threat-panel.html"

[[ -f "$ROOT/lib/field-combinatronic-visuals.py" ]]
[[ -f "$ROOT/data/field-combinatronic-chip-catalog.json" ]]
[[ -f "$ROOT/data/field-combinatronic-visuals-doctrine.json" ]]
grep -q '/api/combinatronic/visuals' "$ROOT/lib/threat-panel-http.py"
grep -q '/api/combinatronic/visuals' "$ROOT/Queen/lib/queen-world.py"
grep -q 'inventory' "$ROOT/lib/field-combinatronic-visuals.py"
grep -q 'build_registry' "$ROOT/lib/field-combinatronic-visuals.py"
grep -q 'qcc-chip-gallery' "$ROOT/Queen/world/queen-chips-cores.html"
grep -q 'qcc-book-gallery' "$ROOT/Queen/world/queen-chips-cores.js"
[[ -f "$ROOT/data/field-combinatronic-visuals-manifest.json" ]]
[[ -f "$ROOT/data/combinatronic-visuals/chips/cyrix_6x86.png" ]]
[[ -f "$ROOT/data/combinatronic-visuals/books/python.png" ]]
[[ -f "$ROOT/Queen/world/assets/combinatronic/chips/cyrix_6x86.png" ]]
if [[ ! -f "$ROOT/library/dewey/000-computer-science/explaining_python/explaining_python.h7c" ]]; then
  out=$(NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    "$PY" "$ROOT/lib/field-dewey-library.py" migrate 2>/dev/null || true)
  grep -qF '"ok": true' <<<"$out"
fi
out=$(NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
  "$PY" "$ROOT/lib/field-combinatronic-visuals.py" manifest 2>/dev/null || true)
grep -qF 'field-combinatronic-visuals' <<<"$out"
out=$(NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
  "$PY" "$ROOT/lib/field-combinatronic-visuals.py" chip mame_m6502 2>/dev/null || true)
grep -qF '"pins": 40' <<<"$out"
out=$(NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
  "$PY" "$ROOT/lib/field-combinatronic-visuals.py" book qbasic 2>/dev/null || true)
grep -qF 'explaining_qbasic' <<<"$out"
out=$(NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
  "$PY" "$ROOT/lib/field-combinatronic-visuals.py" registry 2>/dev/null || true)
grep -qF 'field-combinatronic-visuals-registry/v1' <<<"$out"
out=$(NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" AML_INLINE=1 \
  "$PY" "$ROOT/lib/field-combinatronic-visuals.py" verify 2>/dev/null || true)
grep -qF '"ok": true' <<<"$out"
out=$(NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
  "$PY" "$ROOT/lib/field-combinatronic-visuals.py" pattern chip_png 2>/dev/null || true)
grep -qF '"pattern_id": "chip_png"' <<<"$out"
rm -f "$ROOT/data/combinatronic-visuals/chips/mame_m6502.png"
out=$(NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
  "$PY" "$ROOT/lib/field-combinatronic-visuals.py" repair 2>/dev/null || true)
grep -qF '"ok": true' <<<"$out"
[[ -f "$ROOT/data/combinatronic-visuals/chips/mame_m6502.png" ]]
[[ -f "$ROOT/data/field-combinatronic-visuals-registry.json" ]]

#!/usr/bin/env bash
# KILROY field recompile — after field-stack updates: gen → substrate → kernel → optional Queen seal.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SG="$(cd "$ROOT/.." && pwd)"
QUEEN="${QUEEN_ROOT:-$SG/NewLatest/Queen}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  KILROY Field Recompile — #1 stack after field updates       ║"
echo "╚══════════════════════════════════════════════════════════════╝"

chmod +x "$ROOT/scripts/check-field-stack.sh" \
         "$ROOT/scripts/gen-field-stack.sh" \
         "$ROOT/scripts/kilroy-become-substrate.sh" \
         "$ROOT/scripts/build-kilroy.sh" 2>/dev/null || true

echo "[1/5] check field stack repos"
"$ROOT/scripts/check-field-stack.sh" || {
    echo "[field-recompile] fix missing repos before continuing"
    exit 1
}

echo "[2/5] gen field-stack header + Hostess7 AI wishes"
"$ROOT/scripts/gen-field-stack.sh"
chmod +x "$ROOT/scripts/gen-ai-wishes.sh" 2>/dev/null || true
"$ROOT/scripts/gen-ai-wishes.sh"
chmod +x "$ROOT/scripts/gen-hostess-comfort.sh" 2>/dev/null || true
"$ROOT/scripts/gen-hostess-comfort.sh"

echo "[3/5] FIELDC manifest (compile with Grok16 after RTX build)"
if [[ -f "$SG/Final_Eye/zocr_field_compiler.py" ]]; then
    pythong -c "
import sys, json
sys.path.insert(0, '$SG/Final_Eye')
from zocr_field_compiler import field_compiler_status
s = field_compiler_status()
print('  Grok16 ready:', (s.get('grok16') or {}).get('ready'))
print('  FIELDC:', (s.get('field_compiler') or {}).get('version'))
" 2>/dev/null || echo "  [WARN] field compiler probe skipped"
fi
ls -1 "$ROOT/field/compiler/"*.fld 2>/dev/null | sed 's/^/  fld: /'

echo "[4/5] sync substrate + rebuild KILROY bzImage"
export GROK_IMAGE="${GROK_IMAGE:-0}"
"$ROOT/scripts/kilroy-become-substrate.sh"
"$ROOT/scripts/build-kilroy.sh"

echo "[5/5] Queen field kernel seal (optional)"
if [[ -f "$QUEEN/lib/queen-forge.py" ]]; then
    pythong "$QUEEN/lib/queen-forge.py" run field_kernel 2>/dev/null \
        && echo "  Queen forge:field_kernel OK" \
        || echo "  [WARN] Queen field_kernel skipped"
fi

echo ""
echo "[field-recompile] complete"
echo "  bzImage: $ROOT/build/bzImage"
echo "  stack:   cat /proc/kilroy_field/stack  (when running KILROY kernel)"
echo "  full OS: $SG/NewLatest/AMOURANTHRTX/scripts/build_kilroy_os.sh all"
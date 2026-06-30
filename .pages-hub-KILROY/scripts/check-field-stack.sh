#!/usr/bin/env bash
# Verify KILROY #1 field stack repos — Field_Primer, Final_Eye, World_Redata, AMOURANTHRTX, Queen.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SG="$(cd "$ROOT/.." && pwd)"

check_repo() {
    local name="$1" path="$2" github="$3"
    local ok=0
    if [[ -d "$path" ]]; then
        echo "[OK]   $name — $path"
        ok=1
    else
        echo "[MISS] $name — $path"
    fi
    if [[ -n "$github" && -d "$path/.git" ]]; then
        local remote
        remote="$(git -C "$path" remote get-url origin 2>/dev/null || true)"
        if [[ "$remote" == *"$github"* ]]; then
            echo "       git: $remote"
            git -C "$path" log -1 --oneline 2>/dev/null | sed 's/^/       head: /' || true
        fi
    fi
    return $((1 - ok))
}

fail=0
check_repo "KILROY" "$ROOT" "" || fail=1
check_repo "Field_Primer" "$SG/Field_Primer" "Field_Primer" || fail=1
check_repo "Final_Eye" "$SG/Final_Eye" "Final_Eye" || fail=1
check_repo "World_Redata" "$SG/World_Redata" "World_Redata" || fail=1
check_repo "AMOURANTHRTX" "${AMOURANTHRTX_ROOT:-$SG/AMOURANTHRTX}" "AMOURANTHRTX" || fail=1
check_repo "Queen" "${QUEEN_ROOT:-$SG/Queen}" "" || fail=1
check_repo "Grok16" "${GROK16_ROOT:-$SG/Grok16}" "" || fail=1

for fld in FieldStackCore FieldPrimer FinalEye WorldRedata; do
    if [[ -f "$ROOT/field/compiler/${fld}.fld" ]]; then
        echo "[OK]   FIELDC $fld.fld"
    else
        echo "[MISS] FIELDC $fld.fld"
        fail=1
    fi
done

if [[ -f "$ROOT/data/field-stack-mandate.json" ]]; then
    echo "[OK]   field-stack-mandate.json"
else
    echo "[MISS] field-stack-mandate.json"
    fail=1
fi

if [[ -f "$ROOT/build/bzImage" ]]; then
    echo "[OK]   build/bzImage ($(du -h "$ROOT/build/bzImage" | cut -f1))"
else
    echo "[WARN] build/bzImage — run ./scripts/field-recompile.sh"
fi

# Final_Eye field compiler probe (best-effort)
if [[ -f "$SG/Final_Eye/zocr_field_compiler.py" ]]; then
    pythong -c "
import sys
sys.path.insert(0, '$SG/Final_Eye')
from zocr_field_compiler import field_compiler_status
s = field_compiler_status()
g = s.get('grok16') or {}
print('[OK]   Grok16 ready=%s fieldc=%s' % (g.get('ready'), s.get('field_compiler',{}).get('version','?')))
" 2>/dev/null || echo "[WARN] Final_Eye field compiler probe skipped"
fi

# World_Redata smoke
if [[ -f "$SG/World_Redata/tests/test_core.py" ]]; then
    (cd "$SG/World_Redata" && PYTHONPATH=. pythong tests/test_core.py -q 2>/dev/null) \
        && echo "[OK]   World_Redata test_core" \
        || echo "[WARN] World_Redata test_core"
fi

exit "$fail"
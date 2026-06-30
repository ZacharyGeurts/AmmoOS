#!/usr/bin/env bash
# Verify compat substrate readiness for KILROY Field OS overlay.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=kilroy-compat-path.sh
source "$ROOT/scripts/kilroy-compat-path.sh"
COMPAT="$KILROY_COMPAT_SRC"
TARBALL="${KILROY_COMPAT_TARBALL:-$ROOT/../linux-kernel/linux-7.1.1.tar.xz}"

echo "=== KILROY Field OS — compat substrate check ==="
echo "    Field source: $ROOT"
echo "    substrate:    $COMPAT"

missing=0

if [[ ! -f "$COMPAT/Makefile" ]]; then
    if [[ -f "$TARBALL" ]]; then
        echo "[stage] extracting compat substrate ..."
        mkdir -p "$(dirname "$COMPAT")"
        tar -xJf "$TARBALL" -C "$(dirname "$COMPAT")"
    else
        echo "[FAIL] substrate missing; no tarball at $TARBALL"
        missing=1
    fi
fi

check() {
    if [[ -e "$2" ]]; then echo "[OK]   $1"; else echo "[MISS] $1 -> $2"; missing=1; fi
}

check "Field UAPI" "$ROOT/include/uapi/kilroy/rtx_field.h"
check "Field Die" "$ROOT/kernel/rtx/rtx_core.c"
check "NEXUS guard" "$ROOT/kernel/rtx/kilroy_nexus_guard.c"
check "substrate Makefile" "$COMPAT/Makefile"

if grep -q 'CONFIG_RTX_FIELD_DIE' "$COMPAT/Makefile" 2>/dev/null; then
    echo "[OK]   Field Die merged in substrate Makefile"
else
    echo "[WARN] run kilroy-sync-compat.sh to overlay Field source"
fi

echo ""
if [[ "$missing" -eq 0 ]]; then
    echo "[stage] READY — KILROY Field OS can build:"
    echo "  ./scripts/build-kilroy.sh"
    exit 0
fi
echo "[stage] INCOMPLETE"
exit 1
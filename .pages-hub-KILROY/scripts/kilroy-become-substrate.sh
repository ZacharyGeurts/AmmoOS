#!/usr/bin/env bash
# Transform compat substrate into KILROY Field OS build tree.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=kilroy-compat-path.sh
source "$ROOT/scripts/kilroy-compat-path.sh"
SUBSTRATE="$KILROY_COMPAT_SRC"

echo "=== KILROY become-substrate ==="
echo "    Field source: $ROOT"
echo "    substrate:    $SUBSTRATE"

[[ -f "$SUBSTRATE/Makefile" ]] || { echo "[FAIL] substrate missing"; exit 1; }

"$ROOT/scripts/kilroy-sync-compat.sh" "$ROOT" "$SUBSTRATE"

# rtx/ only in kernel/Makefile
if grep -q 'CONFIG_RTX_FIELD_DIE.*rtx' "$SUBSTRATE/Makefile" 2>/dev/null; then
    echo "[fix] removing erroneous rtx/ from root Makefile"
    sed -i '/# KILROY Field Die/,+2d' "$SUBSTRATE/Makefile"
fi
if ! grep -q 'CONFIG_RTX_FIELD_DIE.*rtx' "$SUBSTRATE/kernel/Makefile" 2>/dev/null; then
    {
        echo ""
        echo "# KILROY Field Die"
        echo 'obj-$(CONFIG_RTX_FIELD_DIE) += rtx/'
    } >>"$SUBSTRATE/kernel/Makefile"
fi

"$ROOT/scripts/kilroy-apply-identity.sh" "$SUBSTRATE"
cp -f "$ROOT/compat/PORT_MAP.md" "$SUBSTRATE/Documentation/kilroy/PORT_MAP.md"
cp -f "$ROOT/Documentation/kilroy/porting.rst" "$SUBSTRATE/Documentation/kilroy/"

echo "[kilroy] substrate identity applied"
"$ROOT/scripts/kilroy-verify-substrate.sh" || true
"$ROOT/scripts/kilroy-port-verify.sh" || true
"$ROOT/scripts/kilroy-port-complete.sh" || true
echo "[kilroy] KILROY 1.0 substrate ready — full Linux + Field overlay"
echo "[kilroy] next: $ROOT/scripts/build-kilroy.sh"
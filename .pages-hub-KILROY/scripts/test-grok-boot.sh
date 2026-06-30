#!/usr/bin/env bash
# Offline Grok bootloader structure tests + optional image build.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

check() {
    local label="$1" path="$2"
    if [[ -e "$path" ]]; then
        echo "[PASS] $label"
    else
        echo "[FAIL] $label — $path"
        FAIL=1
    fi
}

echo "=== Grok bootloader tests ==="

check "Grok manifest" "$ROOT/boot/grok/GROK.md"
check "HELP" "$ROOT/boot/grok/HELP.md"
check "WISHES" "$ROOT/boot/grok/WISHES.md"
check "security MANIFEST" "$ROOT/boot/grok/security/MANIFEST"
check "speedups MANIFEST" "$ROOT/boot/grok/speedups/MANIFEST"
check "grok-compose.sh" "$ROOT/scripts/grok-compose.sh"
check "grok-firmware-audit.sh" "$ROOT/scripts/grok-firmware-audit.sh"

"$ROOT/scripts/grok-compose.sh"
check "composed grok.conf" "$ROOT/boot/grok/grok.conf"

for t in field midnight dawn mono; do
    check "theme $t" "$ROOT/boot/grok/themes/$t/theme.conf"
done

if grep -q 'editor_validation: yes' "$ROOT/boot/grok/grok.conf"; then
    echo "[PASS] in-place editor validation on"
else
    echo "[FAIL] editor_validation missing"
    FAIL=1
fi

if grep -q 'hash_mismatch_panic: yes' "$ROOT/boot/grok/grok.conf"; then
    echo "[PASS] mandatory hash mismatch panic"
else
    echo "[FAIL] hash_mismatch_panic missing"
    FAIL=1
fi

if grep -q 'grok.security=strict' "$ROOT/boot/grok/grok.conf"; then
    echo "[PASS] strict security cmdline"
else
    echo "[FAIL] strict security missing"
    FAIL=1
fi

if grep -q 'grok.security=waived' "$ROOT/boot/grok/grok.conf"; then
    echo "[PASS] explicit waived entry"
else
    echo "[FAIL] waived entry missing"
    FAIL=1
fi

if grep -q 'interface_branding: GROK' "$ROOT/boot/grok/grok.conf"; then
    echo "[PASS] Grok branding"
else
    echo "[FAIL] Grok branding missing"
    FAIL=1
fi

if grep -q 'Memtest (RAM check)' "$ROOT/boot/grok/grok.conf"; then
    echo "[PASS] memtest menu entry (wish #83)"
else
    echo "[FAIL] memtest entry missing — run grok-compose.sh"
    FAIL=1
fi

pythong "$ROOT/boot/grok/theme/generate_wallpapers.py"
check "field wallpaper" "$ROOT/boot/grok/themes/field/wallpaper.bmp"

wish_count="$(grep -cE '^\| [0-9]+ \|' "$ROOT/boot/grok/WISHES.md" || true)"
if [[ "$wish_count" -ge 100 ]]; then
    echo "[PASS] 100 wishes documented ($wish_count rows)"
else
    echo "[FAIL] expected 100 wishes, got $wish_count"
    FAIL=1
fi

if [[ "${GROK_FULL_BUILD:-0}" == "1" ]]; then
    "$ROOT/scripts/grok-mkimage.sh"
    check "Grok disk image" "$ROOT/build/grok-kilroy.img"
    [[ -f "$ROOT/build/grok-kilroy.iso" ]] && check "Grok ISO" "$ROOT/build/grok-kilroy.iso"
fi

echo "=== Grok tests complete ==="
exit "$FAIL"
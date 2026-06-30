#!/usr/bin/env bash
# Compose grok.conf from base + active theme + entries (DRY, in-place edit friendly).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GROK="$ROOT/boot/grok"
OUT="${OUT:-$GROK/grok.conf}"
THEME="${GROK_THEME:-$(tr -d '[:space:]' <"$GROK/themes/ACTIVE" 2>/dev/null || echo field)}"
THEME_DIR="$GROK/themes/$THEME"

[[ -f "$THEME_DIR/theme.conf" ]] || {
    echo "[grok-compose] unknown theme: $THEME"
    exit 1
}

theme_val() {
    local key="$1"
    grep -E "^${key}=" "$THEME_DIR/theme.conf" | head -1 | cut -d= -f2-
}

GROK_THEME_WALLPAPER="$(theme_val wallpaper)"
GROK_THEME_BACKDROP="$(theme_val backdrop)"
GROK_THEME_PALETTE="$(theme_val palette)"
GROK_THEME_PALETTE_BRIGHT="$(theme_val palette_bright)"
GROK_THEME_BG="$(theme_val bg)"
GROK_THEME_FG="$(theme_val fg)"
GROK_THEME_BG_BRIGHT="$(theme_val bg_bright)"
GROK_THEME_FG_BRIGHT="$(theme_val fg_bright)"

python3 "$GROK/theme/generate_wallpapers.py" >/dev/null

substitute() {
    local line="$1"
    line="${line//\$\{GROK_THEME_WALLPAPER\}/$GROK_THEME_WALLPAPER}"
    line="${line//\$\{GROK_THEME_BACKDROP\}/$GROK_THEME_BACKDROP}"
    line="${line//\$\{GROK_THEME_PALETTE\}/$GROK_THEME_PALETTE}"
    line="${line//\$\{GROK_THEME_PALETTE_BRIGHT\}/$GROK_THEME_PALETTE_BRIGHT}"
    line="${line//\$\{GROK_THEME_BG\}/$GROK_THEME_BG}"
    line="${line//\$\{GROK_THEME_FG\}/$GROK_THEME_FG}"
    line="${line//\$\{GROK_THEME_BG_BRIGHT\}/$GROK_THEME_BG_BRIGHT}"
    line="${line//\$\{GROK_THEME_FG_BRIGHT\}/$GROK_THEME_FG_BRIGHT}"
    printf '%s\n' "$line"
}

TMP="$(mktemp)"
{
    echo "# Grok Bootloader — composed $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "# theme=$THEME — edit themes/ACTIVE + grok-compose.sh (source: grok.base.conf)"
    echo ""
    while IFS= read -r line || [[ -n "$line" ]]; do
        substitute "$line"
    done <"$GROK/grok.base.conf"
    echo ""
    cat "$GROK/grok.entries.conf"
} >"$TMP"

mv "$TMP" "$OUT"
chmod 644 "$OUT" 2>/dev/null || true
echo "[grok-compose] theme=$THEME -> $OUT"
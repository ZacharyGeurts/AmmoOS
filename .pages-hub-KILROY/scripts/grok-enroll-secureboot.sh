#!/usr/bin/env bash
# Limine enroll-config for Secure Boot (Grok mandatory integrity).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ESP="${ESP:-/boot/efi}"
LIMINE="$ROOT/boot/grok/vendor/limine/limine"

if [[ ! -x "$LIMINE" ]]; then
    LIMINE="$(find "$ROOT/boot/grok/vendor" -name limine -type f -executable 2>/dev/null | head -1)"
fi

[[ -n "$LIMINE" && -x "$LIMINE" ]] || {
    echo "[grok-enroll] limine binary missing — run ./scripts/grok-fetch.sh"
    exit 1
}

[[ -d "$ESP" ]] || { echo "[grok-enroll] ESP not mounted: $ESP"; exit 1; }

echo "[grok-enroll] enrolling $ESP (requires firmware SB in setup mode)"
sudo "$LIMINE" enroll-config --yes "$ESP" 2>/dev/null || \
    sudo "$LIMINE" enroll-config "$ESP" || {
    echo "[grok-enroll] enroll failed — enter firmware setup mode and retry"
    exit 1
}
echo "[grok-enroll] enrolled — Grok config changes now require SB approval"
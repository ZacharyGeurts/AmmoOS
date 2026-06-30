#!/usr/bin/env bash
# Fetch Memtest86+ EFI for Grok wish #83 (Ubuntu package or manual).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/boot/grok/memtest/memtest86+.efi"
mkdir -p "$(dirname "$DEST")"

if [[ -f "$DEST" ]]; then
    echo "[memtest] already present: $DEST"
    exit 0
fi

if [[ -f /boot/memtest86+x64.efi ]]; then
    cp -f /boot/memtest86+x64.efi "$DEST"
    echo "[memtest] copied from /boot/memtest86+x64.efi"
    exit 0
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if command -v apt-get >/dev/null 2>&1; then
    echo "[memtest] downloading memtest86+ package"
    (cd "$TMP" && apt-get download memtest86+ 2>/dev/null) || true
    DEB="$(find "$TMP" -name 'memtest86+*.deb' | head -1)"
    if [[ -n "$DEB" ]]; then
        dpkg-deb -x "$DEB" "$TMP/extract"
        if [[ -f "$TMP/extract/boot/memtest86+x64.efi" ]]; then
            cp -f "$TMP/extract/boot/memtest86+x64.efi" "$DEST"
            echo "[memtest] installed $DEST from apt package"
            exit 0
        fi
    fi
fi

echo "[memtest] auto-fetch failed — place memtest86+.efi at $DEST"
echo "[memtest] sudo apt install memtest86+  OR  see boot/grok/memtest/README.md"
exit 0
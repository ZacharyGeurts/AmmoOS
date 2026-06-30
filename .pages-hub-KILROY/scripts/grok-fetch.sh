#!/usr/bin/env bash
# Fetch and build Grok compat engine (Limine 9.x-binary).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR="${GROK_LIMINE_SRC:-$ROOT/boot/grok/vendor/limine}"
BRANCH="${GROK_LIMINE_BRANCH:-v9.x-binary}"
JOBS="${JOBS:-$(nproc)}"

need() {
    command -v "$1" >/dev/null 2>&1 || {
        echo "[grok-fetch] missing: $1"
        exit 1
    }
}

need git
need make
need gcc

echo "=== Grok fetch (compat engine) ==="
echo "    dest:   $VENDOR"
echo "    branch: $BRANCH"

mkdir -p "$(dirname "$VENDOR")"

if [[ ! -d "$VENDOR/.git" ]]; then
    git clone https://codeberg.org/Limine/Limine.git \
        --branch "$BRANCH" --depth 1 "$VENDOR"
else
    echo "[grok-fetch] vendor present — git pull"
    git -C "$VENDOR" fetch origin "$BRANCH" --depth 1
    git -C "$VENDOR" checkout -f FETCH_HEAD
fi

make -C "$VENDOR" -j"$JOBS"

for bin in limine limine-bios.sys BOOTX64.EFI limine-bios-cd.bin limine-uefi-cd.bin; do
    [[ -e "$VENDOR/$bin" ]] || [[ -e "$VENDOR/$bin".EFI ]] || {
        found="$(find "$VENDOR" -maxdepth 3 -name "$bin" -print -quit 2>/dev/null || true)"
        [[ -n "$found" ]] || echo "[grok-fetch] warn: $bin not in tree root (may be in subdir)"
    }
done

echo "[grok-fetch] compat engine ready: $VENDOR"
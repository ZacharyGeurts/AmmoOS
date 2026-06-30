#!/usr/bin/env bash
# Create compat/linux-7.1.1 symlink to legacy linux-kernel tree (path unification).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPAT_DIR="$ROOT/../compat"
LEGACY="$ROOT/../linux-kernel/linux-7.1.1"
LINK="$COMPAT_DIR/linux-7.1.1"

mkdir -p "$COMPAT_DIR"

if [[ -L "$LINK" ]]; then
    echo "[compat-link] already linked: $(readlink "$LINK")"
    exit 0
fi

if [[ -d "$LINK" ]]; then
    echo "[compat-link] $LINK exists as directory — not replacing"
    exit 0
fi

if [[ ! -f "$LEGACY/Makefile" ]]; then
    echo "[compat-link] legacy substrate missing: $LEGACY"
    echo "[compat-link] run kilroy-stage-compat.sh first"
    exit 1
fi

ln -sfn "$(cd "$(dirname "$LEGACY")" && pwd)/$(basename "$LEGACY")" "$LINK"
echo "[compat-link] $LINK -> $(readlink "$LINK")"
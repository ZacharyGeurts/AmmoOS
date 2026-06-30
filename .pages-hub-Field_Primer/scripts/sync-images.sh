#!/bin/bash
# Sync assets/images → docs/assets/images for GitHub Pages
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
rsync -a --delete "${ROOT}/assets/images/" "${ROOT}/docs/assets/images/"
echo "Synced images to docs/assets/images/"
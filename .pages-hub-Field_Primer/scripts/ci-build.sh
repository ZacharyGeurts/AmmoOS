#!/bin/bash
# CI-safe HTML build — no image generation, no network fetches.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build-creditor-pages.py
python3 scripts/build-chapters.py
python3 scripts/build-index.py
python3 scripts/build-gallery.py
python3 scripts/verify_editorial.py
echo "ci build done — $(ls docs/chapters/*.html | wc -l) chapters"
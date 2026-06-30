#!/bin/bash
# Update Field Primer after editing content/chapters/*.html
set -euo pipefail
cd "$(dirname "$0")/.."
pythong scripts/voice_pass.py
pythong scripts/build-chapters.py
pythong scripts/publisher_read_first.py
pythong scripts/build-creditor-pages.py
pythong scripts/build-index.py
pythong scripts/build-gallery.py
pythong scripts/verify_editorial.py
pythong scripts/publisher_read_first.py
pythong scripts/sign_off_table.py --sync-comments
echo ""
echo "Updated. Open: docs/index.html"
echo "Chapters: $(ls docs/chapters/*.html | wc -l)"
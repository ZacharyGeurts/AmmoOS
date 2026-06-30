#!/bin/bash
# Build PDF textbook volumes into pdf/
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -x .venv-pdf/bin/python ]]; then
  python3 -m venv .venv-pdf
  .venv-pdf/bin/pip install -q playwright pypdf
  .venv-pdf/bin/playwright install chromium
fi
bash scripts/ci-build.sh
.venv-pdf/bin/python scripts/build-pdfs.py
echo "PDFs ready in pdf/"
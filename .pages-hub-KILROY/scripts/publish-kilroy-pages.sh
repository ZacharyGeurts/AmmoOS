#!/usr/bin/env bash
# Publish KILROY docs/ → gh-pages (zacharygeurts.github.io/KILROY).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NL_ROOT="$(cd "$ROOT/.." && pwd)"
VER="$(grep -m1 '^KILROY Field OS' "$ROOT/KILROY_VERSION" 2>/dev/null | awk '{print $4}' || echo 1.1.0)"
REMOTE="${KILROY_PAGES_REMOTE:-https://github.com/ZacharyGeurts/KILROY.git}"

if [[ -x "$NL_ROOT/scripts/publish-component-pages.sh" ]]; then
  exec "$NL_ROOT/scripts/publish-component-pages.sh" \
    --name KILROY \
    --docs "$ROOT/docs" \
    --remote "$REMOTE" \
    --version "$VER"
fi

echo "Missing publish-component-pages.sh — push docs/ and run GitHub Actions pages.yml" >&2
exit 1
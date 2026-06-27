#!/usr/bin/env bash
# Trim NewLatest dev cruft before release — GitHub-friendly tarball sizes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGGRESSIVE="${TRIM_AGGRESSIVE:-0}"

echo "=== trim-dev-tree @ ${ROOT} ==="

rm -f "${ROOT}/amouranth_engine.log" \
  "${ROOT}/Queen/amouranth_engine.log" \
  "${ROOT}/Queen/.queen-browser.log" \
  "${ROOT}/MANIFEST.sha256.bak" \
  "${ROOT}/hostess7-training-viewer/viewer.log" \
  "${ROOT}/hostess7-training-viewer/.viewer.pid" 2>/dev/null || true

rm -rf \
  "${ROOT}/state" \
  "${ROOT}/.nexus-state" \
  "${ROOT}/.nexus-state-test" \
  "${ROOT}/.nexus-field-drive" \
  "${ROOT}/cache" \
  "${ROOT}/Textbook/staging" \
  "${ROOT}/Queen/field-gecko/profile" \
  "${ROOT}/Queen/.venv-browser" \
  "${ROOT}/Queen/.venv-test" \
  "${ROOT}/Hostess7/cache" \
  "${ROOT}/Hostess7/zac" 2>/dev/null || true

# Stale pack staging (keep dist/*.tar.gz)
for stale in "${ROOT}"/dist/nexus-shield-*/; do
  [[ -d "$stale" ]] || continue
  case "$stale" in
    *-installers/) continue ;;
    *-source.tar.gz) continue ;;
  esac
  if [[ "$stale" == "${ROOT}/dist/nexus-shield-"*"/" ]]; then
    rm -rf "$stale"
    echo "removed stale staging: $stale"
  fi
done

if [[ "$AGGRESSIVE" == "1" ]]; then
  echo "=== aggressive trim (rebuild artifacts) ==="
  rm -rf \
    "${ROOT}/Queen/build" \
    "${ROOT}/Queen/build-"* \
    "${ROOT}/Queen/vendor" \
    "${ROOT}/Queen/cache" \
    "${ROOT}/Queen/field/sovereign" 2>/dev/null || true
fi

echo "=== post-trim size ==="
du -sh "${ROOT}" 2>/dev/null || true
echo "done — run: scripts/pack-release.sh"
#!/bin/bash
# NEXUS-Shield release — tag and publish GitHub release.
# Policy: every update is a full minor version (X.Y.0). Run bump-version.sh first.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"

if [[ ! "${NEXUS_VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Release requires NEXUS_VERSION=X.Y.Z (got ${NEXUS_VERSION}). Use scripts/bump-version.sh" >&2
  exit 1
fi

TAG="v${NEXUS_VERSION}"
NOTES="${ROOT}/RELEASE-${NEXUS_VERSION}.md"

if [[ ! -f "$NOTES" ]]; then
  cat >"$NOTES" <<EOF
# NEXUS-Shield ${NEXUS_VERSION}

- Hostess7 unified operator — autonomous field sync and GitHub update planning
- Panel: live fetch only — no client cache or field-snapshot stubs
- Hell Kit: sever wire, regional disable, human threat sweep
- Precision map & spiderweb with sub-micron GPS placement
- Dark dropdown styling across panel selects

Install: \`sudo ./stealth_install.sh\` from source tree.
Panel: https://127.0.0.1:9477/field
EOF
fi

cd "$ROOT"
git add -A
if ! git diff --cached --quiet; then
  git commit -m "release: NEXUS-Shield ${NEXUS_VERSION}" || true
fi

git tag -a "$TAG" -m "NEXUS-Shield ${NEXUS_VERSION}" 2>/dev/null || git tag -f "$TAG" -m "NEXUS-Shield ${NEXUS_VERSION}"
git push origin main
git push origin "$TAG" --force

if [[ -x "${ROOT}/scripts/pack-release.sh" ]]; then
  bash "${ROOT}/scripts/pack-release.sh"
fi

if command -v gh >/dev/null 2>&1; then
  assets=()
  for asset in "${ROOT}/dist/nexus-shield-${NEXUS_VERSION}-source.tar.gz" \
    "${ROOT}/dist/nexus-shield-${NEXUS_VERSION}-installers.tar.gz"; do
    [[ -f "$asset" ]] && assets+=("$asset")
  done
  if gh release view "$TAG" >/dev/null 2>&1; then
    gh release edit "$TAG" --title "NEXUS-Shield ${NEXUS_VERSION}" --notes-file "$NOTES" 2>/dev/null || true
    [[ ${#assets[@]} -gt 0 ]] && gh release upload "$TAG" "${assets[@]}" --clobber 2>/dev/null || true
  else
    if [[ ${#assets[@]} -gt 0 ]]; then
      gh release create "$TAG" --title "NEXUS-Shield ${NEXUS_VERSION}" --notes-file "$NOTES" "${assets[@]}"
    else
      gh release create "$TAG" --title "NEXUS-Shield ${NEXUS_VERSION}" --notes-file "$NOTES" 2>/dev/null \
        || gh release edit "$TAG" --notes-file "$NOTES" 2>/dev/null || true
    fi
  fi
  echo "Release ${TAG} published via gh"
else
  echo "Tagged ${TAG}. Install gh CLI to auto-publish release notes."
fi
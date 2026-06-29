#!/usr/bin/env bash
# AmmoOS beta release — pipeline, pack, publish to github.com/ZacharyGeurts/AmmoOS
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG_ROOT="${SG_ROOT:-$(cd "${ROOT}/.." && pwd)}"
AMMOOS_VERSION="${AMMOOS_VERSION:-2.0.0-beta3}"
TAG="v${AMMOOS_VERSION}"
PUSH=0

for arg in "$@"; do
  case "$arg" in
    --push) PUSH=1 ;;
    -v|--version) AMMOOS_VERSION="${2:-$AMMOOS_VERSION}"; TAG="v${AMMOOS_VERSION}" ;;
  esac
done

export SG_ROOT AMMOOS_VERSION NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$ROOT/.nexus-state}"

log() { printf '[%s] ammooos-release %s\n' "$(date +%H:%M:%S)" "$*"; }

if [[ "${SKIP_BETA_PIPELINE:-0}" != "1" ]]; then
  log "beta pipeline (AmmoLang)"
  bash "${ROOT}/scripts/ammoos-beta-pipeline.sh" || {
    log "WARN beta pipeline partial — continuing pack (SKIP_BETA_PIPELINE=1 to skip)"
  }
else
  log "SKIP beta pipeline"
fi

log "build manual"
if [[ -f "${ROOT}/docs/build-ammoos-manual.py" ]]; then
  python3 "${ROOT}/docs/build-ammoos-manual.py"
fi

need_pack=1
min_src_bytes=$((500 * 1024 * 1024))
if [[ "${SKIP_PACK:-0}" == "1" ]]; then
  src_arc="${ROOT}/dist/ammoos-${AMMOOS_VERSION}-source.tar.gz"
  inst_arc="${ROOT}/dist/ammoos-${AMMOOS_VERSION}-installers.tar.gz"
  src_ok=0
  if [[ -f "$src_arc" ]]; then
    sz=$(stat -c%s "$src_arc" 2>/dev/null || echo 0)
    [[ "$sz" -ge "$min_src_bytes" ]] && src_ok=1
  fi
  if [[ "$src_ok" -eq 1 && -f "$inst_arc" ]]; then
    need_pack=0
    log "SKIP pack — dist artifacts present ($(du -h "$src_arc" | awk '{print $1}') source)"
  elif [[ -d "${ROOT}/dist/ammoos-${AMMOOS_VERSION}" ]]; then
    log "SKIP full pack — retar source from stage (corrupt or missing archive)"
    bash "${ROOT}/scripts/pack-ammoos-release.sh" --version "$AMMOOS_VERSION" --tar-only
    need_pack=0
  else
    log "SKIP_PACK set but archives missing — full pack"
  fi
fi
if [[ "$need_pack" -eq 1 ]]; then
  log "pack archives"
  bash "${ROOT}/scripts/pack-ammoos-release.sh" --version "$AMMOOS_VERSION"
fi

DIST="${ROOT}/dist"
EXPORT="${DIST}/ammoos-export-${AMMOOS_VERSION}"
rm -rf "$EXPORT"
mkdir -p "$EXPORT"

log "stage export tree for AmmoOS repo"
rsync -a --delete \
  --exclude='.git' \
  --exclude='dist' \
  --exclude='.nexus-state' \
  --exclude='cache' \
  --exclude='state' \
  --exclude='.github' \
  "${DIST}/ammoos-${AMMOOS_VERSION}/" "$EXPORT/"

cd "$EXPORT"
if [[ ! -d .git ]]; then
  git init -b main
  git config user.email "gzac5314@users.noreply.github.com"
  git config user.name "ZacharyGeurts"
fi

git add -A
git commit -m "AmmoOS ${AMMOOS_VERSION} beta — combinatronic field OS" || true

if [[ "$PUSH" -eq 0 ]]; then
  log "export ready at ${EXPORT} (pass --push to publish)"
  exit 0
fi

REMOTE="https://github.com/ZacharyGeurts/AmmoOS.git"
if ! gh repo view ZacharyGeurts/AmmoOS >/dev/null 2>&1; then
  log "create GitHub repo AmmoOS"
  gh repo create AmmoOS --public --description "AmmoOS beta — field OS from SG/NewLatest. Browser + native launch surfaces." \
    --homepage "https://zacharygeurts.github.io/AmmoOS/"
fi

git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"
git push -u origin main --force

git tag -a "$TAG" -m "AmmoOS ${AMMOOS_VERSION}" 2>/dev/null || git tag -f "$TAG" -m "AmmoOS ${AMMOOS_VERSION}"
git push origin "$TAG" --force

NOTES="${ROOT}/RELEASE-${AMMOOS_VERSION}.md"
assets=()
for a in \
  "${DIST}/ammoos-${AMMOOS_VERSION}-source.tar.gz" \
  "${DIST}/ammoos-${AMMOOS_VERSION}-installers.tar.gz" \
  "${DIST}/ammoos-${AMMOOS_VERSION}-windows-x86_64.zip" \
  "${DIST}/ammoos-${AMMOOS_VERSION}-platforms.json" \
  "${DIST}/ammoos-${AMMOOS_VERSION}-PLATFORMS.md"; do
  [[ -f "$a" ]] && assets+=("$a")
done

if gh release view "$TAG" >/dev/null 2>&1; then
  gh release edit "$TAG" --title "AmmoOS ${AMMOOS_VERSION}" --notes-file "$NOTES"
  [[ ${#assets[@]} -gt 0 ]] && gh release upload "$TAG" "${assets[@]}" --clobber
else
  gh release create "$TAG" --title "AmmoOS ${AMMOOS_VERSION}" --notes-file "$NOTES" "${assets[@]}"
fi

log "publish GitHub Pages"
bash "${ROOT}/scripts/publish-ammoos-pages.sh" --version "$AMMOOS_VERSION" --remote "$REMOTE"

log "publish AmmoOS wiki"
AMMOOS_VERSION="$AMMOOS_VERSION" bash "${ROOT}/scripts/publish-ammoos-wiki.sh" || log "WARN wiki publish partial"

log "publish stack hub + component Pages"
STACK_VERSION="$AMMOOS_VERSION" bash "${ROOT}/scripts/publish-stack-pages.sh" || log "WARN stack pages partial"

if [[ -f "${ROOT}/lib/github-profile-sync.py" ]]; then
  log "sync GitHub profile + favorites manifest"
  python3 "${ROOT}/lib/github-profile-sync.py" sync || log "WARN profile sync partial"
fi

log "released ${TAG} → https://github.com/ZacharyGeurts/AmmoOS/releases/tag/${TAG}"
log "manual → https://zacharygeurts.github.io/AmmoOS/"
log "wiki → https://github.com/ZacharyGeurts/AmmoOS/wiki"
log "stack → https://zacharygeurts.github.io/ZacharyGeurts/stack.html"
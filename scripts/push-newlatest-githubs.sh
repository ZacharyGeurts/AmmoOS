#!/usr/bin/env bash
# Push NewLatest + wired sibling repos + stack Pages (after AmmoLang tests).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG="$(cd "${ROOT}/.." && pwd)"
VER="${AMMOOS_VERSION:-2.0.0-beta4}"
GROK_VER="${GROK16_VERSION:-5.2.0}"
KILROY_VER="${KILROY_VERSION:-1.1.0}"

export NEXUS_INSTALL_ROOT="${ROOT}"
export SG_ROOT="${SG}"
export AMMOOS_VERSION="${VER}"

log() { printf '[push-githubs] %s\n' "$*"; }

git_push_tree() {
  local dir="$1"
  local msg="$2"
  [[ -d "${dir}/.git" ]] || return 0
  if git -C "$dir" diff --quiet && git -C "$dir" diff --cached --quiet; then
    log "skip ${dir} (clean)"
    return 0
  fi
  git -C "$dir" add -A
  git -C "$dir" -c user.email="gzac5314@users.noreply.github.com" -c user.name="ZacharyGeurts" \
    commit -m "$msg" || true
  if git -C "$dir" push origin main 2>/dev/null || git -C "$dir" push origin master 2>/dev/null; then
    log "pushed ${dir}"
  else
    log "WARN push failed ${dir}" >&2
  fi
}

log "wire stack siblings"
bash "${ROOT}/scripts/wire-stack.sh" 2>/dev/null | tail -8 || true

log "AmmoOS (NewLatest) main"
git_push_tree "$ROOT" "AmmoOS ${VER} — stack v2 KILROY core · test gate"

for name in Grok16 KILROY AmmoCode Field_Primer Field_Research Final_Eye World_Redata ZNetwork Kill-Grok-Orphans; do
  target="${ROOT}/${name}"
  [[ -L "$target" ]] && target="$(readlink -f "$target" 2>/dev/null || readlink "$target")"
  [[ -d "$target" ]] || continue
  git_push_tree "$target" "${name} — AmmoOS ${VER} stack companion"
done

if [[ -d "${ROOT}/profile/queen-publish" ]]; then
  git_push_tree "${ROOT}/profile/queen-publish" "Queen — AmmoOS ${VER} stack companion"
fi

log "AmmoOS Pages (canonical manual)"
AMMOOS_VERSION="$VER" bash "${ROOT}/scripts/publish-ammoos-pages.sh" || log "WARN ammoos pages"

log "Stack redirect hubs"
AMMOOS_VERSION="$VER" bash "${ROOT}/scripts/publish-ammoos-hub-pages.sh" || log "WARN hub pages"

log "KILROY Pages (own docs)"
if [[ -x "${ROOT}/KILROY/scripts/publish-kilroy-pages.sh" ]]; then
  KILROY_PAGES_REMOTE="${KILROY_PAGES_REMOTE:-https://github.com/ZacharyGeurts/KILROY.git}" \
    bash "${ROOT}/KILROY/scripts/publish-kilroy-pages.sh" || log "WARN kilroy pages"
fi

log "Profile + stack hub"
bash "${ROOT}/scripts/publish-profile-pages.sh" || log "WARN profile pages"

log "Wiki"
AMMOOS_VERSION="$VER" bash "${ROOT}/scripts/publish-ammoos-wiki.sh" || log "WARN wiki"

log "Companion releases"
STACK_VERSION="$VER" bash "${ROOT}/scripts/publish-stack-releases.sh" || log "WARN stack releases"

if [[ -f "${ROOT}/lib/github-profile-sync.py" ]]; then
  python3 "${ROOT}/lib/github-profile-sync.py" sync || log "WARN profile sync"
fi

log "done — canonical https://zacharygeurts.github.io/AmmoOS/"
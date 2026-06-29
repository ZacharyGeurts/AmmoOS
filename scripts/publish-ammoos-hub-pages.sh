#!/usr/bin/env bash
# Publish thin gh-pages stubs for stack repos — all link to canonical AmmoOS code + manual.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER="${AMMOOS_VERSION:-2.0.0-beta3}"
STAGE="${ROOT}/.pages-hub-staging"
HUB_PY="${ROOT}/lib/page_ammoos_hub.py"
PAGES_BRANCH="${PAGES_BRANCH:-gh-pages}"
OWNER="${GITHUB_PAGES_OWNER:-ZacharyGeurts}"

log() { printf '[hub-pages] %s\n' "$*"; }

[[ -f "$HUB_PY" ]] || { echo "missing page_ammoos_hub.py" >&2; exit 1; }

if [[ -f "${ROOT}/docs/build-ammoos-manual.py" ]]; then
  python3 "${ROOT}/docs/build-ammoos-manual.py"
fi

publish_one() {
  local name="$1" manual_url="$2"
  local remote="https://github.com/${OWNER}/${name}.git"
  local repo_dir="${ROOT}/.pages-hub-${name}"

  log "${name} → ${manual_url}"
  gh repo view "${OWNER}/${name}" >/dev/null 2>&1 || { log "skip ${name} (missing)"; return 0; }

  rm -rf "${STAGE:?}/${name}"
  python3 "$HUB_PY" --out "$STAGE" --version "$VER" --repo "$name" >/dev/null

  rm -rf "$repo_dir"
  if git ls-remote --heads "$remote" "$PAGES_BRANCH" 2>/dev/null | grep -q "$PAGES_BRANCH"; then
    git clone --branch "$PAGES_BRANCH" --single-branch "$remote" "$repo_dir"
  else
    mkdir -p "$repo_dir"
    git -C "$repo_dir" init -b "$PAGES_BRANCH"
    git -C "$repo_dir" remote add origin "$remote"
  fi
  [[ -d "${repo_dir}/.git" ]] || { log "FAIL ${name} — no .git after clone/init"; return 0; }

  rsync -a --delete --exclude='.git' "${STAGE}/${name}/" "${repo_dir}/"
  git -C "$repo_dir" add -A
  if git -C "$repo_dir" diff --cached --quiet; then
    log "${name} up to date"
    return 0
  fi
  git -C "$repo_dir" -c user.email="gzac5314@users.noreply.github.com" -c user.name="ZacharyGeurts" \
    commit -m "pages: ${name} hub → AmmoOS code + manual v${VER}"
  git -C "$repo_dir" push origin "$PAGES_BRANCH" 2>/dev/null || git -C "$repo_dir" push -u origin "$PAGES_BRANCH"
  log "published https://${OWNER,,}.github.io/${name}/"
}

while IFS=$'\t' read -r name manual_url; do
  [[ -n "$name" ]] || continue
  [[ "$name" == "AmmoOS" ]] && continue
  publish_one "$name" "$manual_url"
done < <(python3 "$HUB_PY" --out "$STAGE" --version "$VER" --list)

log "done — canonical code: https://github.com/ZacharyGeurts/AmmoOS"
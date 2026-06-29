#!/usr/bin/env bash
# Publish thin gh-pages stubs for stack repos — all link to canonical AmmoOS manual.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER="${AMMOOS_VERSION:-2.0.0-beta3}"
STAGE="${ROOT}/.pages-hub-staging"
HUB_PY="${ROOT}/lib/page_ammoos_hub.py"
PAGES_BRANCH="${PAGES_BRANCH:-gh-pages}"
OWNER="${GITHUB_PAGES_OWNER:-ZacharyGeurts}"

log() { printf '[hub-pages] %s\n' "$*"; }

[[ -f "$HUB_PY" ]] || { echo "missing page_ammoos_hub.py" >&2; exit 1; }

# Ensure AmmoOS manual is current before publishing redirect targets.
if [[ -f "${ROOT}/docs/build-ammoos-manual.py" ]]; then
  python3 "${ROOT}/docs/build-ammoos-manual.py"
fi

python3 "$HUB_PY" --out "$STAGE" --version "$VER" --list | while IFS=$'\t' read -r name manual_url; do
  [[ -n "$name" ]] || continue
  [[ "$name" == "AmmoOS" ]] && continue
  remote="https://github.com/${OWNER}/${name}.git"
  repo_dir="${ROOT}/.pages-hub-${name}"
  log "${name} → ${manual_url}"

  if ! gh repo view "${OWNER}/${name}" >/dev/null 2>&1; then
    log "skip ${name} (repo missing on GitHub)"
    continue
  fi

  rm -rf "${STAGE:?}/${name}"
  python3 "$HUB_PY" --out "$STAGE" --version "$VER" --repo "$name" >/dev/null

  if [[ ! -d "${repo_dir}/.git" ]]; then
    rm -rf "$repo_dir"
    if git ls-remote --heads "$remote" "$PAGES_BRANCH" 2>/dev/null | grep -q "$PAGES_BRANCH"; then
      git clone --branch "$PAGES_BRANCH" --single-branch "$remote" "$repo_dir"
    else
      mkdir -p "$repo_dir"
      git -C "$repo_dir" init -b "$PAGES_BRANCH"
      git -C "$repo_dir" remote add origin "$remote"
    fi
  fi

  rsync -a --delete "${STAGE}/${name}/" "${repo_dir}/"
  cd "$repo_dir"
  git add -A
  if git diff --cached --quiet; then
    log "${name} up to date"
    continue
  fi
  git -c user.email="gzac5314@users.noreply.github.com" -c user.name="ZacharyGeurts" \
    commit -m "pages: ${name} hub → AmmoOS manual v${VER}"
  git push origin "$PAGES_BRANCH" 2>/dev/null || git push -u origin "$PAGES_BRANCH"
  log "published https://${OWNER,,}.github.io/${name}/"
done

log "done — canonical manual: https://zacharygeurts.github.io/AmmoOS/"
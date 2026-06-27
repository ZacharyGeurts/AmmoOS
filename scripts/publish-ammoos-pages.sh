#!/usr/bin/env bash
# Publish AmmoOS docs/ to GitHub Pages (gh-pages branch).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCS_SRC="${ROOT}/docs"
PAGES_REPO="${PAGES_REPO:-${ROOT}/.pages-ammoos-publish}"
PAGES_REMOTE="${PAGES_REMOTE:-https://github.com/ZacharyGeurts/AmmoOS.git}"
PAGES_BRANCH="${PAGES_BRANCH:-gh-pages}"
VER="${AMMOOS_VERSION:-1.0.1-beta}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VER="$2"; shift 2 ;;
    --remote) PAGES_REMOTE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

[[ -d "$DOCS_SRC" ]] || { echo "Missing docs/" >&2; exit 1; }

if [[ -f "${ROOT}/docs/build-ammoos-manual.py" ]]; then
  python3 "${ROOT}/docs/build-ammoos-manual.py"
fi

if [[ ! -d "${PAGES_REPO}/.git" ]]; then
  rm -rf "$PAGES_REPO"
  if git ls-remote --heads "$PAGES_REMOTE" "$PAGES_BRANCH" 2>/dev/null | grep -q "$PAGES_BRANCH"; then
    git clone --branch "$PAGES_BRANCH" --single-branch "$PAGES_REMOTE" "$PAGES_REPO"
  else
    mkdir -p "$PAGES_REPO"
    git -C "$PAGES_REPO" init -b "$PAGES_BRANCH"
    git -C "$PAGES_REPO" remote add origin "$PAGES_REMOTE"
  fi
fi

rsync -a --delete \
  --exclude='.git' \
  --exclude='build-ammoos-manual.py' \
  --exclude='capture-*.py' \
  "${DOCS_SRC}/" "${PAGES_REPO}/"

cd "$PAGES_REPO"
git add -A
git diff --cached --quiet && { echo "Pages up to date"; exit 0; }
git -c user.email="gzac5314@users.noreply.github.com" -c user.name="ZacharyGeurts" \
  commit -m "pages: AmmoOS manual v${VER}"
git push origin "$PAGES_BRANCH" 2>/dev/null || git push -u origin "$PAGES_BRANCH"
echo "Pages: https://zacharygeurts.github.io/AmmoOS/"
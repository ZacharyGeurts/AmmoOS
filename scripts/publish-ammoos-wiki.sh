#!/usr/bin/env bash
# Publish AmmoOS wiki/*.md → github.com/ZacharyGeurts/AmmoOS.wiki
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WIKI_SRC="${ROOT}/wiki"
WIKI_REPO="${WIKI_REPO:-${ROOT}/.wiki-ammoos-publish}"
WIKI_REMOTE="${WIKI_REMOTE:-https://github.com/ZacharyGeurts/AmmoOS.wiki.git}"
VER="${AMMOOS_VERSION:-2.0.0-beta3}"

[[ -d "$WIKI_SRC" ]] || { echo "Missing ${WIKI_SRC}" >&2; exit 1; }

gh repo edit ZacharyGeurts/AmmoOS --enable-wiki 2>/dev/null || true

if [[ ! -d "${WIKI_REPO}/.git" ]]; then
  rm -rf "$WIKI_REPO"
  if git ls-remote --heads "$WIKI_REMOTE" master 2>/dev/null | grep -q master; then
    git clone "$WIKI_REMOTE" "$WIKI_REPO"
  elif git ls-remote --heads "$WIKI_REMOTE" main 2>/dev/null | grep -q main; then
    git clone -b main "$WIKI_REMOTE" "$WIKI_REPO"
  else
    mkdir -p "$WIKI_REPO"
    git -C "$WIKI_REPO" init -b master
    git -C "$WIKI_REPO" remote add origin "$WIKI_REMOTE"
  fi
fi

rsync -a --delete --exclude='.git' "${WIKI_SRC}/" "${WIKI_REPO}/"

cd "$WIKI_REPO"
git add -A
git diff --cached --quiet && { echo "AmmoOS wiki up to date"; exit 0; }
git -c user.email="gzac5314@users.noreply.github.com" -c user.name="ZacharyGeurts" \
  commit -m "wiki: AmmoOS ${VER} — stack tie-in + MCP lane"
git push origin master 2>/dev/null || git push origin main 2>/dev/null || git push -u origin HEAD
echo "Wiki: https://github.com/ZacharyGeurts/AmmoOS/wiki"
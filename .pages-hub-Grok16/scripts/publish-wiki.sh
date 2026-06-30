#!/usr/bin/env bash
# Publish wiki/*.md to GitHub wiki repo (full replace).
set -euo pipefail

GROK16_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WIKI_SRC="${GROK16_ROOT}/wiki"
WIKI_REPO="${WIKI_REPO:-${GROK16_ROOT}/.wiki-publish}"
WIKI_REMOTE="${WIKI_REMOTE:-https://github.com/ZacharyGeurts/Grok16.wiki.git}"
VER="${1:-$(python3 -c "import json; print(json.load(open('${GROK16_ROOT}/data/grok16-version.json'))['distro_version'])" 2>/dev/null || echo unknown)}"

[[ -d "$WIKI_SRC" ]] || { echo "Missing ${WIKI_SRC}" >&2; exit 1; }

if [[ ! -d "${WIKI_REPO}/.git" ]]; then
  rm -rf "$WIKI_REPO"
  git clone "$WIKI_REMOTE" "$WIKI_REPO"
fi

rsync -a --delete --exclude='.git' "${WIKI_SRC}/" "${WIKI_REPO}/"

cd "$WIKI_REPO"
git add -A
git diff --cached --quiet && { echo "Wiki already up to date."; exit 0; }
git -c user.email="gzac5314@users.noreply.github.com" -c user.name="ZacharyGeurts" \
  commit -m "wiki: Grok16 ${VER}"
git push origin master 2>/dev/null || git push origin main 2>/dev/null || git push
echo "Wiki published: https://github.com/ZacharyGeurts/Grok16/wiki"
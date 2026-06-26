#!/bin/bash
# Publish wiki/*.md to GitHub wiki repo (full replace).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"
WIKI_SRC="${ROOT}/wiki"
WIKI_REPO="${WIKI_REPO:-${ROOT}/.wiki-publish}"
WIKI_REMOTE="${WIKI_REMOTE:-https://github.com/ZacharyGeurts/NEXUS-Shield.wiki.git}"

if [[ ! -d "$WIKI_SRC" ]]; then
  echo "Missing ${WIKI_SRC}" >&2
  exit 1
fi

if [[ ! -d "${WIKI_REPO}/.git" ]]; then
  rm -rf "$WIKI_REPO"
  git clone "$WIKI_REMOTE" "$WIKI_REPO"
fi

# Remove retired pages (v2.x / Ultra-Stealth standalone)
rsync -a --delete \
  --exclude='.git' \
  "${WIKI_SRC}/" "${WIKI_REPO}/"

cd "$WIKI_REPO"
git add -A
if git diff --cached --quiet; then
  echo "Wiki already up to date."
  exit 0
fi
git commit -m "wiki: v${NEXUS_VERSION} — boot hardening, field switch safety, painless conversion"
git push origin master 2>/dev/null || git push origin main 2>/dev/null || git push
echo "Wiki published: https://github.com/ZacharyGeurts/NEXUS-Shield/wiki"
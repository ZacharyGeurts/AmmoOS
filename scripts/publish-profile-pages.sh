#!/usr/bin/env bash
# Publish profile/docs → ZacharyGeurts repo /docs (GitHub Pages from main).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/profile/docs"
CLONE="${ROOT}/.profile-zacharygeurts-publish"
REMOTE="${PROFILE_REMOTE:-https://github.com/ZacharyGeurts/ZacharyGeurts.git}"
VER="${PROFILE_VERSION:-stack}"

[[ -d "$SRC" ]] || { echo "Missing ${SRC}" >&2; exit 1; }

if [[ ! -d "${CLONE}/.git" ]]; then
  rm -rf "$CLONE"
  git clone --depth 1 "$REMOTE" "$CLONE"
fi

git -C "$CLONE" pull --ff-only origin main 2>/dev/null || true
mkdir -p "${CLONE}/docs"
rsync -a --delete "${SRC}/" "${CLONE}/docs/"
cd "$CLONE"
git add docs/
git diff --cached --quiet && { echo "Profile pages up to date"; exit 0; }
git -c user.email="gzac5314@users.noreply.github.com" -c user.name="ZacharyGeurts" \
  commit -m "pages: profile stack v${VER}"
git push origin main
echo "Profile: https://zacharygeurts.github.io/ZacharyGeurts/"
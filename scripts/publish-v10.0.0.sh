#!/usr/bin/env bash
# Publish NEXUS-Shield v10.0.0 to GitHub (Field Tools Edition)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMMIT_MSG='release: v10.0.0 Field Tools Edition — no-sleep waits capped 5s'
TAG='v10.0.0'
RELEASE_TITLE='v10.0.0 Field Tools Edition'
NOTES_FILE='lib/RELEASE-10.0.0.md'
REMOTE='origin'
BRANCH='main'

echo "=== git status ==="
git status -sb
echo "=== remotes ==="
git remote -v

echo "=== stage all ==="
git add -A
if git diff --cached --quiet; then
  echo "No staged changes; using current HEAD for tag/release."
else
  echo "=== commit ==="
  git commit -m "$COMMIT_MSG"
fi

COMMIT_HASH="$(git rev-parse HEAD)"
echo "=== commit hash: $COMMIT_HASH ==="

echo "=== push $BRANCH ==="
git push "$REMOTE" "$BRANCH"

echo "=== annotated tag $TAG ==="
if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Tag $TAG exists locally; recreating at HEAD (-f)."
  git tag -a -f "$TAG" -m "$RELEASE_TITLE"
else
  git tag -a "$TAG" -m "$RELEASE_TITLE"
fi

echo "=== push tag ==="
git push "$REMOTE" "$TAG" --force-with-lease

RELEASE_URL=""
TAG_URL="https://github.com/ZacharyGeurts/NEXUS-Shield/releases/tag/$TAG"

if command -v gh >/dev/null 2>&1; then
  echo "=== gh release create ==="
  if gh release view "$TAG" >/dev/null 2>&1; then
    gh release upload "$TAG" "$NOTES_FILE" --clobber 2>/dev/null || true
    gh release edit "$TAG" --title "$RELEASE_TITLE" --notes-file "$NOTES_FILE"
  else
    gh release create "$TAG" --title "$RELEASE_TITLE" --notes-file "$NOTES_FILE"
  fi
  RELEASE_URL="$(gh release view "$TAG" --json url -q .url 2>/dev/null || echo "$TAG_URL")"
elif [[ -n "${GITHUB_TOKEN:-}" ]]; then
  echo "=== GitHub API release create ==="
  NOTES="$(python3 -c 'import json,sys; print(json.dumps(open(sys.argv[1]).read()))' "$NOTES_FILE")"
  curl -fsSL -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/ZacharyGeurts/NEXUS-Shield/releases" \
    -d "{\"tag_name\":\"$TAG\",\"name\":\"$RELEASE_TITLE\",\"body\":$NOTES,\"draft\":false,\"prerelease\":false}"
  RELEASE_URL="$TAG_URL"
else
  echo "WARN: gh and GITHUB_TOKEN unavailable — tag pushed; create release manually at $TAG_URL"
  RELEASE_URL="$TAG_URL"
fi

echo ""
echo "=== PUBLISH REPORT ==="
echo "commit:  $COMMIT_HASH"
echo "branch:  $REMOTE/$BRANCH pushed"
echo "tag:     $TAG"
echo "tag_url: $TAG_URL"
echo "release: $RELEASE_URL"

#!/usr/bin/env bash
# Sync profile README, favorites manifest, and per-repo releases pages from GitHub API.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHONG:-$(command -v pythong || command -v python3)}"

command -v gh >/dev/null 2>&1 || {
  echo "gh CLI required" >&2
  exit 1
}

echo "=== GitHub profile sync ==="
"$PY" "${ROOT}/lib/github-profile-sync.py"
echo "=== done ==="
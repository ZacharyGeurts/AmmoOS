#!/usr/bin/env bash
# Regenerate docs/releases.html from GitHub API (SHA-256 manifest).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NL="$(cd "$ROOT/.." && pwd)"
PY="${GROK_LAB_PY:-python3}"

export SG_ROOT="$(cd "$NL/.." && pwd)"
export NEXUS_INSTALL_ROOT="$NL"

"$PY" "$NL/lib/github-profile-sync.py" 2>&1 | grep -i KILROY || true
echo "releases page: $ROOT/docs/releases.html"
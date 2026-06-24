#!/usr/bin/env bash
# Build World's Best Dewey Library tree for GitHub — browsable shelves + book manifests.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_REPO_ROOT="${NEXUS_REPO_ROOT:-$ROOT}"
export NEXUS_DEWEY_GITHUB_ROOT="${NEXUS_DEWEY_GITHUB_ROOT:-$ROOT/library}"
export HOSTESS7_ROOT="${HOSTESS7_ROOT:-/home/default/Desktop/SG/Hostess7}"
export HOSTESS7_TEAM_FIELD="${HOSTESS7_TEAM_FIELD:-/media/default/HOSTESS7_TEAM/fieldstorage}"

echo "Building Dewey catalog from field drive…"
python3 "${ROOT}/lib/h7-library-bridge.py" build --force >/dev/null

echo "Generating GitHub library tree at ${NEXUS_DEWEY_GITHUB_ROOT}…"
python3 "${ROOT}/lib/dewey-library-github.py"

echo "OK — library/dewey ready for GitHub"
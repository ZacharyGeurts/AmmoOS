#!/usr/bin/env bash
# Build World's Best Dewey Library tree for GitHub — browsable shelves + book manifests.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_REPO_ROOT="${NEXUS_REPO_ROOT:-$ROOT}"
export NEXUS_DEWEY_GITHUB_ROOT="${NEXUS_DEWEY_GITHUB_ROOT:-$ROOT/library}"
# shellcheck source=/dev/null
source "${ROOT}/lib/sg-paths.sh"
sg_paths_export_defaults

echo "Building Dewey catalog from field drive…"
pythong "${ROOT}/lib/h7-library-bridge.py" build --force >/dev/null

echo "Generating GitHub library tree at ${NEXUS_DEWEY_GITHUB_ROOT}…"
pythong "${ROOT}/lib/dewey-library-github.py"

echo "OK — library/dewey ready for GitHub"
#!/usr/bin/env bash
# Move flat textbooks/*.h7 into textbooks/dewey/{class}/ on Hostess7 TEAM field drive.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
# shellcheck source=/dev/null
source "${ROOT}/lib/sg-paths.sh"
sg_paths_export_defaults

if [[ "${1:-}" == "--dry-run" ]]; then
  pythong "${ROOT}/lib/h7-library-bridge.py" organize --dry-run
else
  pythong "${ROOT}/lib/h7-library-bridge.py" organize
fi
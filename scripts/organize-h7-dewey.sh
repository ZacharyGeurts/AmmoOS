#!/usr/bin/env bash
# Move flat textbooks/*.h7 into textbooks/dewey/{class}/ on Hostess7 TEAM field drive.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export HOSTESS7_ROOT="${HOSTESS7_ROOT:-/home/default/Desktop/SG/Hostess7}"
export HOSTESS7_TEAM_FIELD="${HOSTESS7_TEAM_FIELD:-/media/default/HOSTESS7_TEAM/fieldstorage}"

if [[ "${1:-}" == "--dry-run" ]]; then
  python3 "${ROOT}/lib/h7-library-bridge.py" organize --dry-run
else
  python3 "${ROOT}/lib/h7-library-bridge.py" organize
fi
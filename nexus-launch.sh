#!/usr/bin/env bash
# NEXUS Field launcher — ZNetwork prompt, panel, tray.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_FIELD_STANDALONE=1
export SG_ROOT="${SG_ROOT:-${ROOT}}"
exec "${ROOT}/nexus.sh" "$@"
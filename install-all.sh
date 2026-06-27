#!/usr/bin/env bash
# NEXUS Field — system install via NXF manifest (one admin approval).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export SG_ROOT="${SG_ROOT:-${ROOT}}"
export NEXUS_INSTALL_SRC="${ROOT}"

exec bash "${ROOT}/lib/nxf-install.sh" --mode system "$@"
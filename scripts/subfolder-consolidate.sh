#!/usr/bin/env bash
# Subfolder consolidate — routes through AmmoLang (AML_BUILD=1 default).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$ROOT/.nexus-state}"
export SG_ROOT="${SG_ROOT:-$(dirname "$ROOT")}"
export AML_BUILD="${AML_BUILD:-1}"
exec bash "${ROOT}/lib/ammolang-run.sh" subfolder_migrate "$@"
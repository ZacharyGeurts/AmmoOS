#!/usr/bin/env bash
# AmmoOS beta pipeline — routes through AmmoLang (AML_BUILD=1 default).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export SG_ROOT="${SG_ROOT:-$(cd "${ROOT}/.." && pwd)}"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$ROOT/.nexus-state}"
exec bash "${ROOT}/lib/ammolang-run.sh" beta_pipeline "$@"
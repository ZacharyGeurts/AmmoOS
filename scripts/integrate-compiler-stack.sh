#!/usr/bin/env bash
# Compiler stack — routes through AmmoLang when AML_BUILD=1.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export SG_ROOT="${SG_ROOT:-$(cd "${ROOT}/.." && pwd)}"
exec bash "${ROOT}/lib/ammolang-run.sh" compiler_stack "$@"
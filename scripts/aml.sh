#!/usr/bin/env bash
# AmmoLang-only task entry — minute progress · hang guard · freeze assist.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TASK="${1:-agent}"
shift || true

export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$ROOT/.nexus-state}"
export SG_ROOT="${SG_ROOT:-$(cd "${ROOT}/.." && pwd)}"
export AML_BUILD="${AML_BUILD:-1}"
export AML_PROGRESS="${AML_PROGRESS:-1}"
export AML_PROGRESS_MIN="${AML_PROGRESS_MIN:-60}"
export AML_GITHUB_TRANSPORT="${AML_GITHUB_TRANSPORT:-mcp_secure}"
export HOSTESS_TRUTH_FLOOR="${HOSTESS_TRUTH_FLOOR:-58}"

printf '[aml] task=%s progress_every=%ss panel=%s/ammolang-release-progress.json\n' \
  "$TASK" "$AML_PROGRESS_MIN" "$NEXUS_STATE_DIR"

exec bash "${ROOT}/lib/ammolang-run.sh" "$TASK" "$@"
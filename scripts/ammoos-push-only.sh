#!/usr/bin/env bash
# Push-only lane — skip beta pipeline + pack when dist artifacts already exist.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export SKIP_BETA_PIPELINE=1
export SKIP_PACK=1
export AMMOOS_VERSION="${AMMOOS_VERSION:-2.0.0-beta3}"

exec bash "${ROOT}/scripts/ammoos-release.sh" --version "$AMMOOS_VERSION" --push "$@"
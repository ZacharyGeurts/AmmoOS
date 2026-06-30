#!/usr/bin/env bash
# Resolve KILROY compat substrate path (canonical compat/ pin, legacy linux-kernel/).
# Source: eval "$(./scripts/kilroy-compat-path.sh)"
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -n "${KILROY_COMPAT_SRC:-}" && -f "${KILROY_COMPAT_SRC}/Makefile" ]]; then
    KILROY_COMPAT_RESOLVED="$KILROY_COMPAT_SRC"
elif [[ -f "$ROOT/../compat/linux-7.1.1/Makefile" ]]; then
    KILROY_COMPAT_RESOLVED="$(cd "$ROOT/../compat/linux-7.1.1" && pwd)"
elif [[ -f "$ROOT/../linux-kernel/linux-7.1.1/Makefile" ]]; then
    KILROY_COMPAT_RESOLVED="$(cd "$ROOT/../linux-kernel/linux-7.1.1" && pwd)"
else
    KILROY_COMPAT_RESOLVED="$ROOT/../compat/linux-7.1.1"
fi

export KILROY_COMPAT_SRC="$KILROY_COMPAT_RESOLVED"

if [[ "${1:-}" == "--print" ]]; then
    echo "$KILROY_COMPAT_RESOLVED"
elif [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    :
else
    echo "KILROY_COMPAT_SRC=$KILROY_COMPAT_RESOLVED"
fi
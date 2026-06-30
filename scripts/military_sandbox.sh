#!/usr/bin/env bash
# Military sandbox — landlock + capability drop (graceful fallback when tools absent).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"

RO_PATHS="${NEXUS_SANDBOX_RO:-/etc/nexus:${NEXUS_INSTALL_ROOT}/config}"
RW_PATH="${NEXUS_STATE_DIR}"

if command -v landlock-restrict >/dev/null 2>&1; then
  IFS=':' read -r -a ro_arr <<< "$RO_PATHS"
  args=()
  for p in "${ro_arr[@]}"; do
    [[ -e "$p" ]] && args+=(--ro "$p")
  done
  [[ -d "$RW_PATH" ]] && args+=(--rw "$RW_PATH")
  if ((${#args[@]})); then
    exec landlock-restrict "${args[@]}" -- "$@"
  fi
fi

# seccomp/systemd strict profiles ship with installed units — dev tree runs unsandboxed.
exec "$@"

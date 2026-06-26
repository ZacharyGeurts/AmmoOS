#!/bin/bash
# Resolve KILROY Field OS — top-level sibling preferred; never inside Queen.
set -euo pipefail

nexus_kilroy_resolve() {
  local sg="${1:-${SG_ROOT:-}}"
  local candidate resolved=""

  if [[ -n "${KILROY_ROOT:-}" && -f "${KILROY_ROOT}/scripts/build-kilroy.sh" ]]; then
    resolved="$(cd "${KILROY_ROOT}" && pwd)"
    printf '%s' "$resolved"
    return 0
  fi

  if [[ -n "$sg" ]]; then
    sg="$(cd "$sg" 2>/dev/null && pwd || true)"
  fi
  if [[ -z "$sg" ]]; then
    local here
    here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    sg="$(cd "${here}/.." && pwd)"
  fi

  local -a candidates=()
  candidates+=("${sg}/KILROY")
  candidates+=("$(cd "${sg}/.." 2>/dev/null && pwd)/KILROY")
  candidates+=("${HOME}/Desktop/KILROY")
  candidates+=("${HOME}/KILROY")

  for candidate in "${candidates[@]}"; do
    [[ -n "$candidate" && -f "${candidate}/scripts/build-kilroy.sh" ]] || continue
    resolved="$(cd "$candidate" && pwd)"
    printf '%s' "$resolved"
    return 0
  done
  return 1
}

nexus_kilroy_export() {
  local sg="${1:-${SG_ROOT:-}}"
  local kr
  kr="$(nexus_kilroy_resolve "$sg" 2>/dev/null || true)"
  if [[ -n "$kr" ]]; then
    export KILROY_ROOT="$kr"
    export SG_ROOT="${SG_ROOT:-$(cd "${kr}/.." 2>/dev/null && pwd)}"
    return 0
  fi
  return 1
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  nexus_kilroy_resolve "${1:-}" || exit 1
fi
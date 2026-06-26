#!/bin/bash
# SG portable path resolution — no operator-specific defaults; env + sibling discovery only.

sg_paths_root() {
  if [[ -n "${SG_ROOT:-}" ]]; then
    printf '%s\n' "$(cd "${SG_ROOT}" && pwd)"
    return 0
  fi
  if [[ -n "${NEXUS_INSTALL_ROOT:-}" ]]; then
    local parent
    parent="$(cd "${NEXUS_INSTALL_ROOT}/.." 2>/dev/null && pwd)" || true
    if [[ -n "$parent" && -d "${parent}/Hostess7" ]]; then
      printf '%s\n' "$parent"
      return 0
    fi
    if [[ -n "$parent" ]]; then
      printf '%s\n' "$parent"
      return 0
    fi
  fi
  if [[ -n "${BASH_SOURCE[1]:-}" ]]; then
    local lib
    lib="$(cd "$(dirname "${BASH_SOURCE[1]}")" && pwd)"
    printf '%s\n' "$(cd "${lib}/../.." && pwd)"
    return 0
  fi
  printf '%s\n' "$(pwd)"
}

sg_paths_hostess7_root() {
  if [[ -n "${HOSTESS7_ROOT:-}" ]]; then
    printf '%s\n' "$(cd "${HOSTESS7_ROOT}" && pwd)"
    return 0
  fi
  local sg
  sg="$(sg_paths_root)"
  printf '%s\n' "${sg}/Hostess7"
}

sg_paths_hostess7_team_field() {
  if [[ -n "${HOSTESS7_TEAM_FIELD:-}" ]]; then
    printf '%s\n' "${HOSTESS7_TEAM_FIELD}"
    return 0
  fi
  local h7
  h7="$(sg_paths_hostess7_root)"
  printf '%s\n' "${h7}/cache/fieldstorage"
}

sg_paths_hostess7_team1_field() {
  [[ -n "${HOSTESS7_TEAM1_FIELD:-}" ]] && printf '%s\n' "${HOSTESS7_TEAM1_FIELD}"
}

sg_paths_hostess7_nexus_cache() {
  if [[ -n "${HOSTESS7_NEXUS_CACHE:-}" ]]; then
    printf '%s\n' "${HOSTESS7_NEXUS_CACHE}"
    return 0
  fi
  local state="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"
  printf '%s\n' "${state%/}/hostess7-cache/fieldstorage"
}

sg_paths_znewocr_root() {
  if [[ -n "${ZNEWOCR_ROOT:-}" ]]; then
    printf '%s\n' "$(cd "${ZNEWOCR_ROOT}" 2>/dev/null && pwd || echo "${ZNEWOCR_ROOT}")"
    return 0
  fi
  if [[ -n "${ZOCR_ROOT:-}" ]]; then
    printf '%s\n' "$(cd "${ZOCR_ROOT}" 2>/dev/null && pwd || echo "${ZOCR_ROOT}")"
    return 0
  fi
  local sg
  sg="$(sg_paths_root)"
  for candidate in "${sg}/ZNEWOCR" "${sg}/Final_Eye" "${sg}/ZOCR"; do
    [[ -d "$candidate" ]] || continue
    printf '%s\n' "$candidate"
    return 0
  done
  printf '%s\n' "${sg}/ZNEWOCR"
}

sg_paths_znetwork_root() {
  if [[ -n "${ZNETWORK_ROOT:-}" ]]; then
    printf '%s\n' "$(cd "${ZNETWORK_ROOT}" 2>/dev/null && pwd || echo "${ZNETWORK_ROOT}")"
    return 0
  fi
  local sg
  sg="$(sg_paths_root)"
  for candidate in "${sg}/ZNetwork" "${sg}/znetwork"; do
    [[ -d "$candidate" ]] || continue
    printf '%s\n' "$candidate"
    return 0
  done
  printf '%s\n' "${sg}/ZNetwork"
}

sg_paths_export_defaults() {
  export SG_ROOT="${SG_ROOT:-$(sg_paths_root)}"
  export HOSTESS7_ROOT="${HOSTESS7_ROOT:-$(sg_paths_hostess7_root)}"
  export HOSTESS7_TEAM_FIELD="${HOSTESS7_TEAM_FIELD:-$(sg_paths_hostess7_team_field)}"
  export HOSTESS7_NEXUS_CACHE="${HOSTESS7_NEXUS_CACHE:-$(sg_paths_hostess7_nexus_cache)}"
  export ZNEWOCR_ROOT="${ZNEWOCR_ROOT:-$(sg_paths_znewocr_root)}"
  export ZOCR_ROOT="${ZOCR_ROOT:-${ZNEWOCR_ROOT}}"
  export ZNETWORK_ROOT="${ZNETWORK_ROOT:-$(sg_paths_znetwork_root)}"
  export NEXUS_SHIELD_SOURCE="${NEXUS_SHIELD_SOURCE:-${NEXUS_INSTALL_ROOT:-}}"
  export FINAL_EYE_ROOT="${FINAL_EYE_ROOT:-${SG_ROOT}/Final_Eye}"
}
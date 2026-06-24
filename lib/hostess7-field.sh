#!/bin/bash
# Hostess7 unified fieldstorage — best-of-world: TEAM NVMe primary, desktop cache fallback.

HOSTESS7_ROOT="${HOSTESS7_ROOT:-/home/default/Desktop/SG/Hostess7}"
HOSTESS7_TEAM_FIELD="${HOSTESS7_TEAM_FIELD:-/media/default/HOSTESS7_TEAM/fieldstorage}"

hostess7_field_root() {
  if [[ -d "${HOSTESS7_TEAM_FIELD}/brain" ]]; then
    printf '%s\n' "${HOSTESS7_TEAM_FIELD}"
    return 0
  fi
  if [[ -d "${HOSTESS7_ROOT}/cache/fieldstorage/brain" ]]; then
    printf '%s\n' "${HOSTESS7_ROOT}/cache/fieldstorage"
    return 0
  fi
  printf '%s\n' "${HOSTESS7_TEAM_FIELD}"
}

hostess7_security_paths() {
  local rel="$1"
  local root
  root="$(hostess7_field_root)"
  printf '%s\n' "${root}/${rel}"
  if [[ "${root}" != "${HOSTESS7_ROOT}/cache/fieldstorage" ]] \
    && [[ -d "${HOSTESS7_ROOT}/cache/fieldstorage" ]]; then
    printf '%s\n' "${HOSTESS7_ROOT}/cache/fieldstorage/${rel}"
  fi
}

hostess7_nexus_source() {
  local candidates=(
    "${NEXUS_SHIELD_SOURCE:-}"
    "/home/default/Desktop/SG/Latest/NEXUS-Shield"
    "/home/default/Desktop/SG/NEXUS-Shield"
    "${HOSTESS7_ROOT}/../Latest/NEXUS-Shield"
  )
  local p
  for p in "${candidates[@]}"; do
    [[ -n "$p" && -f "${p}/stealth_install.sh" ]] || continue
    printf '%s\n' "$p"
    return 0
  done
  return 1
}
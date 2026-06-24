#!/bin/bash
# Hostess7 unified fieldstorage — best-of-world: TEAM NVMe primary, desktop cache fallback.

HOSTESS7_ROOT="${HOSTESS7_ROOT:-/home/default/Desktop/SG/Hostess7}"
HOSTESS7_TEAM_FIELD="${HOSTESS7_TEAM_FIELD:-/media/default/HOSTESS7_TEAM/fieldstorage}"

hostess7_field_brain_score() {
  local root="$1"
  local score=0
  [[ -d "${root}/brain" ]] && score=$((score + 5))
  [[ -f "${root}/brain/library/manifest.json" ]] && score=$((score + 80))
  [[ -f "${root}/brain/library/search_index.jsonl" ]] && score=$((score + 40))
  [[ -d "${root}/brain/superintel" ]] && score=$((score + 50))
  [[ -f "${root}/brain/superintel/context.json" ]] && score=$((score + 30))
  printf '%s' "$score"
}

hostess7_field_root() {
  local team="${HOSTESS7_TEAM_FIELD}"
  local cache="${HOSTESS7_ROOT}/cache/fieldstorage"
  local best="" score best_score=0 s
  for candidate in "$team" "$cache"; do
    [[ -d "$candidate" ]] || continue
    s="$(hostess7_field_brain_score "$candidate")"
    if [[ "$s" -gt "$best_score" ]]; then
      best_score="$s"
      best="$candidate"
    fi
  done
  if [[ -n "$best" ]]; then
    printf '%s\n' "$best"
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
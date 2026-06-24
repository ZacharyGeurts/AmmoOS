#!/bin/bash
# Field brain + library — GitHub repo is authoritative; field drive enriches when mounted.

nexus_field_brain_score() {
  local root="$1"
  local score=0
  [[ -d "${root}/brain" ]] && score=$((score + 5))
  [[ -f "${root}/brain/library/manifest.json" ]] && score=$((score + 80))
  [[ -f "${root}/brain/library/search_index.jsonl" ]] && score=$((score + 40))
  [[ -d "${root}/brain/superintel" ]] && score=$((score + 50))
  [[ -f "${root}/brain/superintel/context.json" ]] && score=$((score + 30))
  printf '%s' "$score"
}

nexus_field_brain_best_root() {
  local team="${HOSTESS7_TEAM_FIELD:-/media/default/HOSTESS7_TEAM/fieldstorage}"
  local cache="${HOSTESS7_ROOT:-/home/default/Desktop/SG/Hostess7}/cache/fieldstorage"
  local best="" score best_score=0 s
  for candidate in "$team" "$cache"; do
    [[ -d "$candidate" ]] || continue
    s="$(nexus_field_brain_score "$candidate")"
    if [[ "$s" -gt "$best_score" ]]; then
      best_score="$s"
      best="$candidate"
    fi
  done
  [[ -n "$best" ]] || best="$cache"
  printf '%s' "$best"
}

nexus_field_brain_github_refresh() {
  [[ "${NEXUS_FIELD_BRAIN_GITHUB_FETCH:-1}" == "1" ]] || return 0
  local install="${NEXUS_INSTALL_ROOT}"
  [[ -d "${install}/.git" ]] || return 0
  command -v git >/dev/null 2>&1 || return 0
  (
    cd "$install" || exit 0
    GIT_TERMINAL_PROMPT=0 \
    GIT_SSH_COMMAND="ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15" \
      timeout 30 git fetch origin main 2>/dev/null || true
    git checkout origin/main -- library/ data/field-brain 2>/dev/null \
      || git checkout origin/main -- library/ 2>/dev/null || true
  )
  nexus_log "INFO" "field-brain-sync" "GITHUB_REFRESH library/ data/field-brain from origin/main"
}

nexus_field_brain_sync() {
  [[ "${NEXUS_FIELD_BRAIN_SYNC:-1}" == "1" ]] || return 0
  local h7_root="${HOSTESS7_ROOT:-/home/default/Desktop/SG/Hostess7}"
  local team="${HOSTESS7_TEAM_FIELD:-/media/default/HOSTESS7_TEAM/fieldstorage}"
  local cache="${h7_root}/cache/fieldstorage"
  local install="${NEXUS_INSTALL_ROOT}"
  local data="${install}/data"
  local best
  best="$(nexus_field_brain_best_root)"

  nexus_field_brain_github_refresh

  mkdir -p "${data}/field-brain" 2>/dev/null || true

  # Enrich data/field-brain for GitHub when live field has fuller manifests.
  for src in "${best}/brain/library/manifest.json" "${best}/brain/library/field_fingerprint.json" \
    "${best}/brain/index.json" "${best}/brain/superintel/context.json"; do
    [[ -f "$src" ]] || continue
    base="$(basename "$src")"
    case "$base" in
      context.json) dest="context.json" ;;
      *) dest="$base" ;;
    esac
    install -m 644 "$src" "${data}/field-brain/${dest}" 2>/dev/null \
      || cp -f "$src" "${data}/field-brain/${dest}" 2>/dev/null || true
  done

  local gh_books=0
  if [[ -d "${install}/library/dewey" ]]; then
    gh_books="$(find "${install}/library/dewey" -name book.json 2>/dev/null | wc -l | tr -d ' ')"
  fi

  if [[ -f "${install}/lib/field-brain-panel.py" ]]; then
    NEXUS_INSTALL_ROOT="${install}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
      HOSTESS7_ROOT="${h7_root}" HOSTESS7_TEAM_FIELD="${team}" \
      python3 "${install}/lib/field-brain-panel.py" panel >/dev/null 2>&1 || true
  fi

  if [[ -f "${install}/lib/h7-library-bridge.py" ]]; then
    NEXUS_INSTALL_ROOT="${install}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
      HOSTESS7_ROOT="${h7_root}" HOSTESS7_TEAM_FIELD="${team}" \
      python3 "${install}/lib/h7-library-bridge.py" build >/dev/null 2>&1 || true
  fi

  nexus_log "INFO" "field-brain-sync" "BRAIN_SYNC github_books=${gh_books} field_root=${best}"
}

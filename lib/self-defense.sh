#!/bin/bash
# Self-defense — verify signed script manifest before loading modules.

NEXUS_MANIFEST="${NEXUS_MANIFEST:-${NEXUS_INSTALL_ROOT}/MANIFEST.sha256}"

nexus_manifest_paths() {
  find "${NEXUS_INSTALL_ROOT}/lib" -maxdepth 1 \( -name '*.sh' -o -name '*.py' \) -type f 2>/dev/null | sort
  find "${NEXUS_INSTALL_ROOT}/bin" -maxdepth 1 -type f 2>/dev/null | sort
  find "${NEXUS_INSTALL_ROOT}/panel" -type f 2>/dev/null | sort
  [[ -f "${NEXUS_INSTALL_ROOT}/config/nexus.conf" ]] && echo "${NEXUS_INSTALL_ROOT}/config/nexus.conf"
  [[ -f "${NEXUS_INSTALL_ROOT}/config/device-whitelist.conf" ]] && echo "${NEXUS_INSTALL_ROOT}/config/device-whitelist.conf"
}

nexus_manifest_unlock() {
  command -v chattr >/dev/null 2>&1 || return 0
  chattr -i "$NEXUS_MANIFEST" 2>/dev/null || true
}

nexus_manifest_lock() {
  command -v chattr >/dev/null 2>&1 || return 0
  [[ -f "$NEXUS_MANIFEST" ]] && chattr +i "$NEXUS_MANIFEST" 2>/dev/null || true
}

nexus_sign_manifest() {
  local out="${1:-$NEXUS_MANIFEST}"
  [[ "$out" == "$NEXUS_MANIFEST" ]] && nexus_manifest_unlock
  : >"$out"
  chmod 640 "$out" 2>/dev/null || true
  local path hash
  while IFS= read -r path; do
    [[ -f "$path" ]] || continue
    hash="$(sha256sum "$path" | awk '{print $1}')"
    printf '%s  %s\n' "$hash" "$path" >>"$out"
  done < <(nexus_manifest_paths)
  [[ "$out" == "$NEXUS_MANIFEST" ]] && nexus_manifest_lock
}

nexus_manifest_resolve_path() {
  local path="$1"
  [[ -f "$path" ]] && { printf '%s' "$path"; return 0; }
  local base="${path##*/}"
  [[ -n "$base" && -f "${NEXUS_INSTALL_ROOT}/lib/${base}" ]] && {
    printf '%s' "${NEXUS_INSTALL_ROOT}/lib/${base}"
    return 0
  }
  [[ -n "$base" && -f "${NEXUS_INSTALL_ROOT}/bin/${base}" ]] && {
    printf '%s' "${NEXUS_INSTALL_ROOT}/bin/${base}"
    return 0
  }
  local rel="${path#*${NEXUS_INSTALL_ROOT}/}"
  if [[ "$rel" != "$path" && -f "${NEXUS_INSTALL_ROOT}/${rel}" ]]; then
    printf '%s' "${NEXUS_INSTALL_ROOT}/${rel}"
    return 0
  fi
  rel="${path#*/panel/}"
  if [[ "$rel" != "$path" && -f "${NEXUS_INSTALL_ROOT}/panel/${rel}" ]]; then
    printf '%s' "${NEXUS_INSTALL_ROOT}/panel/${rel}"
    return 0
  fi
  printf '%s' "$path"
  return 1
}

nexus_verify_integrity() {
  [[ "${NEXUS_SELF_DEFENSE:-1}" == "1" ]] || return 0
  [[ -f "$NEXUS_MANIFEST" ]] || {
    nexus_log "ALERT" "self-defense" "MANIFEST_MISSING"
    return 1
  }
  local fail=0 hash path resolved current
  while read -r hash path; do
    [[ -n "$hash" && -n "$path" ]] || continue
    resolved="$(nexus_manifest_resolve_path "$path" || true)"
    [[ -f "$resolved" ]] || {
      nexus_log "ALERT" "self-defense" "INTEGRITY_MISSING path=${path}"
      fail=1
      continue
    }
    current="$(sha256sum "$resolved" | awk '{print $1}')"
    if [[ "$current" != "$hash" ]]; then
      nexus_log "ALERT" "self-defense" "INTEGRITY_FAIL path=${resolved}"
      fail=1
    fi
  done <"$NEXUS_MANIFEST"
  [[ "$fail" -eq 0 ]]
}

nexus_safe_source() {
  local script="$1"
  nexus_verify_integrity || {
    nexus_log "ALERT" "self-defense" "REFUSING_LOAD tampered=${script}"
    return 1
  }
  # shellcheck source=/dev/null
  source "$script"
}
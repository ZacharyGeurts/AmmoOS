#!/bin/bash
# NEXUS boot implementation — reload field tech on every startup/reboot.
# First install: full wire + migrate + meld + paths. Later boots: lighter refresh, then normal daemon.

nexus_boot_impl_default_timeout() {
  printf '%s' "${NEXUS_BOOT_SCRIPT_TIMEOUT:-30}"
}

nexus_boot_impl_validate_install_root() {
  local root="${NEXUS_INSTALL_ROOT:-}"
  [[ -n "$root" && "$root" == /* ]] || {
    nexus_log "ALERT" "boot-impl" "UNSAFE_INSTALL_ROOT empty_or_relative"
    return 1
  }
  [[ "$root" != *".."* ]] || {
    nexus_log "ALERT" "boot-impl" "UNSAFE_INSTALL_ROOT traversal"
    return 1
  }
  local resolved="$root"
  if command -v realpath >/dev/null 2>&1; then
    resolved="$(realpath -m "$root" 2>/dev/null || echo "$root")"
  fi
  [[ "$resolved" == /* ]] || return 1
  [[ -d "$resolved" ]] || {
    nexus_log "ALERT" "boot-impl" "INSTALL_ROOT_MISSING path=${resolved}"
    return 1
  }
  if [[ "$resolved" != "$root" ]]; then
    NEXUS_INSTALL_ROOT="$resolved"
    export NEXUS_INSTALL_ROOT
  fi
  return 0
}

nexus_boot_impl_script_trusted() {
  local script="$1"
  [[ -f "$script" && -r "$script" ]] || return 1
  case "$script" in
    "${NEXUS_INSTALL_ROOT}"/*) ;;
    *) return 1 ;;
  esac
  if command -v realpath >/dev/null 2>&1; then
    local real_script real_root
    real_script="$(realpath "$script" 2>/dev/null || return 1)"
    real_root="$(realpath "${NEXUS_INSTALL_ROOT}" 2>/dev/null || echo "${NEXUS_INSTALL_ROOT}")"
    [[ "$real_script" == "${real_root}/"* ]] || return 1
  fi
  return 0
}

nexus_boot_impl_rotate_log() {
  local log max_bytes size
  log="$(nexus_boot_impl_log_path)"
  [[ -f "$log" ]] || return 0
  max_bytes=$((5 * 1024 * 1024))
  size="$(stat -c%s "$log" 2>/dev/null || echo 0)"
  if [[ "$size" -gt "$max_bytes" ]]; then
    : >"$log"
  fi
}

nexus_boot_impl_run_script() {
  local script="$1"
  local timeout_sec="${2:-$(nexus_boot_impl_default_timeout)}"
  nexus_boot_impl_script_trusted "$script" || {
    nexus_log "ALERT" "boot-impl" "UNTRUSTED_SCRIPT path=${script}"
    return 1
  }
  if command -v timeout >/dev/null 2>&1; then
    timeout "${timeout_sec}s" bash "$script" >>"$(nexus_boot_impl_log_path)" 2>&1
  else
    bash "$script" >>"$(nexus_boot_impl_log_path)" 2>&1
  fi
}

nexus_boot_impl_resolve_python() {
  local py=""
  py="$(nexus_resolve_pythong 2>/dev/null || true)"
  [[ -n "$py" && -x "$py" ]] || py="$(command -v python3 2>/dev/null || true)"
  [[ -n "$py" && -x "$py" ]] || return 1
  printf '%s' "$py"
}

nexus_boot_impl_enabled() {
  [[ "${NEXUS_BOOT_IMPL:-1}" == "1" ]]
}

nexus_boot_impl_first_marker() {
  printf '%s' "${NEXUS_STATE_DIR}/first-boot.complete"
}

nexus_boot_impl_last_marker() {
  printf '%s' "${NEXUS_STATE_DIR}/boot-impl.last"
}

nexus_boot_impl_log_path() {
  printf '%s' "${NEXUS_STATE_DIR}/boot-impl.log"
}

nexus_boot_impl_is_first() {
  [[ "${NEXUS_BOOT_FORCE_FIRST:-}" == "1" ]] && return 0
  [[ ! -f "$(nexus_boot_impl_first_marker)" ]]
}

nexus_boot_impl_record() {
  local mode="$1" wired="$2" meld="$3"
  local ts ver
  ts="$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date)"
  ver="$(nexus_read_version 2>/dev/null || echo unknown)"
  cat >"$(nexus_boot_impl_last_marker)" <<EOF
mode=${mode}
version=${ver}
wired=${wired}
meld=${meld}
install_root=${NEXUS_INSTALL_ROOT}
sg_root=${SG_ROOT:-}
ts=${ts}
EOF
  chmod 640 "$(nexus_boot_impl_last_marker)" 2>/dev/null || true
}

nexus_boot_impl_wire_stack() {
  local wire="" parent wired=0
  for wire in \
    "${NEXUS_INSTALL_ROOT}/scripts/wire-stack.sh" \
    "${SG_ROOT:-}/scripts/wire-stack.sh"; do
    [[ -x "$wire" ]] && break
    wire=""
  done
  [[ -n "$wire" ]] || { printf '0'; return 0; }

  parent="$(cd "$(dirname "$wire")/.." && pwd)"
  if nexus_is_dev_install \
    || [[ -d "${parent}/../Grok16" ]] \
    || [[ -d "${parent}/../KILROY" ]] \
    || [[ -d "${parent}/Grok16" ]]; then
    if nexus_boot_impl_run_script "$wire"; then
      wired=1
    fi
  fi
  printf '%s' "$wired"
}

nexus_boot_impl_migrate_state() {
  local migrate="${NEXUS_INSTALL_ROOT}/scripts/migrate-nexus-state.sh"
  [[ -x "$migrate" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    nexus_boot_impl_run_script "$migrate" 120 || true
}

nexus_boot_impl_export_paths() {
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/nexus-os-assist.sh" ]]; then
    nexus_boot_impl_script_trusted "${NEXUS_INSTALL_ROOT}/lib/nexus-os-assist.sh" || return 1
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/nexus-os-assist.sh"
    nexus_os_assist_export_paths 2>/dev/null || true
    return 0
  fi
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/sg-paths.sh" ]]; then
    nexus_boot_impl_script_trusted "${NEXUS_INSTALL_ROOT}/lib/sg-paths.sh" || return 1
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/sg-paths.sh"
    sg_paths_export_defaults 2>/dev/null || true
  fi
}

nexus_boot_impl_front_hook() {
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/front-hook.sh" ]] || return 0
  nexus_boot_impl_script_trusted "${NEXUS_INSTALL_ROOT}/lib/front-hook.sh" || return 1
  # shellcheck source=/dev/null
  source "${NEXUS_INSTALL_ROOT}/lib/front-hook.sh"
  nexus_front_hook_board 2>/dev/null || true
}

nexus_boot_impl_sense_meld() {
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/field-sense-package.sh" ]] || return 1
  local py meld_py
  py="$(nexus_boot_impl_resolve_python)" || {
    nexus_log "WARN" "boot-impl" "PYTHON_MISSING sense_meld_skipped"
    return 1
  }
  meld_py="${NEXUS_INSTALL_ROOT}/lib/field-sense-package-meld.py"
  nexus_boot_impl_script_trusted "${NEXUS_INSTALL_ROOT}/lib/field-sense-package.sh" || return 1
  local state_saved="${NEXUS_STATE_DIR}"
  # shellcheck source=/dev/null
  source "${NEXUS_INSTALL_ROOT}/lib/field-sense-package.sh"
  NEXUS_STATE_DIR="${state_saved}"
  if command -v timeout >/dev/null 2>&1; then
    timeout 60s env \
      NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
      SG_ROOT="${SG_ROOT:-}" \
      FINAL_EYE_ROOT="${FINAL_EYE_ROOT:-}" \
      FINAL_EAR_ROOT="${FINAL_EAR_ROOT:-}" \
      ZOCR_ROOT="${ZOCR_ROOT:-}" \
      ZNEWOCR_ROOT="${ZNEWOCR_ROOT:-}" \
      WORLD_REDATA_ROOT="${WORLD_REDATA_ROOT:-}" \
      HOSTESS7_ROOT="${HOSTESS7_ROOT:-}" \
      "$py" "$meld_py" meld >/dev/null 2>&1 && return 0
  else
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
      SG_ROOT="${SG_ROOT:-}" \
      FINAL_EYE_ROOT="${FINAL_EYE_ROOT:-}" \
      FINAL_EAR_ROOT="${FINAL_EAR_ROOT:-}" \
      ZOCR_ROOT="${ZOCR_ROOT:-}" \
      ZNEWOCR_ROOT="${ZNEWOCR_ROOT:-}" \
      WORLD_REDATA_ROOT="${WORLD_REDATA_ROOT:-}" \
      HOSTESS7_ROOT="${HOSTESS7_ROOT:-}" \
      "$py" "$meld_py" meld >/dev/null 2>&1 && return 0
  fi
  return 1
}

nexus_boot_impl_training_viewer() {
  [[ "${NEXUS_TRAINING_VIEWER_BOOT:-0}" == "1" ]] || return 0
  local launch="${NEXUS_INSTALL_ROOT}/hostess7-training-viewer/launch.sh"
  [[ -x "$launch" ]] || return 0
  H7_TRAINING_VIEWER_PORT="${H7_TRAINING_VIEWER_PORT:-9488}" \
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    SG_ROOT="${SG_ROOT:-}" nexus_boot_impl_run_script "$launch" 15 || true
}

nexus_boot_impl_verify_integrity() {
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/self-defense.sh" ]] || return 0
  nexus_boot_impl_script_trusted "${NEXUS_INSTALL_ROOT}/lib/self-defense.sh" || {
    nexus_log "ALERT" "boot-impl" "UNTRUSTED_SELF_DEFENSE"
    return 1
  }
  # shellcheck source=/dev/null
  source "${NEXUS_INSTALL_ROOT}/lib/self-defense.sh"
  if nexus_verify_integrity; then
    return 0
  fi
  nexus_log "WARN" "boot-impl" "INTEGRITY_VERIFY_FAILED"
  return 1
}

nexus_boot_impl_sign_manifest() {
  [[ "$(id -u)" -ne 0 ]] && return 0
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/self-defense.sh" ]] || return 0
  nexus_boot_impl_script_trusted "${NEXUS_INSTALL_ROOT}/lib/self-defense.sh" || return 1
  # shellcheck source=/dev/null
  source "${NEXUS_INSTALL_ROOT}/lib/self-defense.sh"
  nexus_sign_manifest "${NEXUS_INSTALL_ROOT}/MANIFEST.sha256" 2>/dev/null || {
    nexus_log "WARN" "boot-impl" "MANIFEST_SIGN_FAILED"
    return 1
  }
}

nexus_boot_impl_thermal_guard_init() {
  [[ "${NEXUS_FIELD_THERMAL_GUARD:-1}" == "1" ]] || return 0
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/field-thermal-guard.py" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    pythong "${NEXUS_INSTALL_ROOT}/lib/field-thermal-guard.py" evaluate >/dev/null 2>&1 || true
}

nexus_boot_impl_bounded_redata() {
  [[ "${NEXUS_FIELD_THERMAL_GUARD:-1}" == "1" ]] || return 0
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/field-global-redata.py" ]] || return 0
  local py
  py="$(nexus_boot_impl_resolve_python)" || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    "$py" "${NEXUS_INSTALL_ROOT}/lib/field-global-redata.py" boot-test >/dev/null 2>&1 || {
    nexus_log "WARN" "boot-impl" "bounded_redata_deferred"
    return 1
  }
  nexus_log "INFO" "boot-impl" "bounded_redata_ok"
}

nexus_boot_impl_ensure_dirs() {
  mkdir -p "${NEXUS_STATE_DIR}" "${NEXUS_STATE_DIR}/hostess7-cache" 2>/dev/null || true
  touch "$(nexus_boot_impl_log_path)" 2>/dev/null || true
  nexus_boot_impl_rotate_log
  nexus_boot_impl_thermal_guard_init
}

nexus_boot_impl_first() {
  local wired=0 meld=0
  nexus_boot_impl_ensure_dirs
  nexus_boot_impl_log_path >/dev/null
  nexus_log "INFO" "boot-impl" "FIRST_INSTALL begin root=${NEXUS_INSTALL_ROOT}"

  wired="$(nexus_boot_impl_wire_stack)"
  nexus_boot_impl_migrate_state
  nexus_boot_impl_export_paths
  nexus_boot_impl_front_hook
  nexus_apply_permissions 2>/dev/null || true
  nexus_boot_impl_sign_manifest || nexus_log "WARN" "boot-impl" "sign_skipped"
  if ! nexus_boot_impl_verify_integrity; then
    nexus_log "WARN" "boot-impl" "first_boot_integrity_fail"
  fi
  nexus_boot_impl_bounded_redata || true
  nexus_boot_impl_sense_meld && meld=1
  nexus_boot_impl_training_viewer

  printf 'completed=1\nmode=first\nts=%s\nversion=%s\n' \
    "$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date)" \
    "$(nexus_read_version 2>/dev/null || echo unknown)" \
    >"$(nexus_boot_impl_first_marker)"
  chmod 640 "$(nexus_boot_impl_first_marker)" 2>/dev/null || true
  nexus_boot_impl_record first "$wired" "$meld"
  nexus_log "INFO" "boot-impl" "FIRST_INSTALL done wired=${wired} meld=${meld}"
}

nexus_boot_impl_refresh() {
  local wired=0 meld=0
  nexus_boot_impl_ensure_dirs
  nexus_log "INFO" "boot-impl" "BOOT_REFRESH begin root=${NEXUS_INSTALL_ROOT}"

  wired="$(nexus_boot_impl_wire_stack)"
  nexus_boot_impl_export_paths
  nexus_boot_impl_front_hook
  if ! nexus_boot_impl_verify_integrity; then
    nexus_log "WARN" "boot-impl" "refresh_integrity_fail"
  fi
  nexus_boot_impl_bounded_redata || true
  nexus_boot_impl_sense_meld && meld=1

  nexus_boot_impl_record refresh "$wired" "$meld"
  nexus_log "INFO" "boot-impl" "BOOT_REFRESH done wired=${wired} meld=${meld}"
}

nexus_boot_impl_run() {
  nexus_boot_impl_enabled || return 0
  nexus_boot_impl_validate_install_root || return 1
  if nexus_boot_impl_is_first; then
    nexus_boot_impl_first
  else
    nexus_boot_impl_refresh
  fi
}
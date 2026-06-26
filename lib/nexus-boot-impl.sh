#!/bin/bash
# NEXUS boot implementation — reload field tech on every startup/reboot.
# First install: full wire + migrate + meld + paths. Later boots: lighter refresh, then normal daemon.

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
  [[ -n "$wire" ]] || return 1

  parent="$(cd "$(dirname "$wire")/.." && pwd)"
  if nexus_is_dev_install \
    || [[ -d "${parent}/../Grok16" ]] \
    || [[ -d "${parent}/../KILROY" ]] \
    || [[ -d "${parent}/Grok16" ]]; then
    bash "$wire" >>"$(nexus_boot_impl_log_path)" 2>&1 || true
    wired=1
  fi
  printf '%s' "$wired"
}

nexus_boot_impl_migrate_state() {
  local migrate="${NEXUS_INSTALL_ROOT}/scripts/migrate-nexus-state.sh"
  [[ -x "$migrate" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    bash "$migrate" >>"$(nexus_boot_impl_log_path)" 2>&1 || true
}

nexus_boot_impl_export_paths() {
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/nexus-os-assist.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/nexus-os-assist.sh"
    nexus_os_assist_export_paths 2>/dev/null || true
    return 0
  fi
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/sg-paths.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/sg-paths.sh"
    sg_paths_export_defaults 2>/dev/null || true
  fi
}

nexus_boot_impl_front_hook() {
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/front-hook.sh" ]] || return 0
  # shellcheck source=/dev/null
  source "${NEXUS_INSTALL_ROOT}/lib/front-hook.sh"
  nexus_front_hook_board 2>/dev/null || true
}

nexus_boot_impl_sense_meld() {
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/field-sense-package.sh" ]] || return 1
  local state_saved="${NEXUS_STATE_DIR}"
  # shellcheck source=/dev/null
  source "${NEXUS_INSTALL_ROOT}/lib/field-sense-package.sh"
  NEXUS_STATE_DIR="${state_saved}"
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    SG_ROOT="${SG_ROOT:-}" \
    FINAL_EYE_ROOT="${FINAL_EYE_ROOT:-}" \
    FINAL_EAR_ROOT="${FINAL_EAR_ROOT:-}" \
    ZOCR_ROOT="${ZOCR_ROOT:-}" \
    ZNEWOCR_ROOT="${ZNEWOCR_ROOT:-}" \
    WORLD_REDATA_ROOT="${WORLD_REDATA_ROOT:-}" \
    HOSTESS7_ROOT="${HOSTESS7_ROOT:-}" \
    pythong "${NEXUS_INSTALL_ROOT}/lib/field-sense-package-meld.py" meld >/dev/null 2>&1 && return 0
  return 1
}

nexus_boot_impl_training_viewer() {
  [[ "${NEXUS_TRAINING_VIEWER_BOOT:-0}" == "1" ]] || return 0
  local launch="${NEXUS_INSTALL_ROOT}/hostess7-training-viewer/launch.sh"
  [[ -x "$launch" ]] || return 0
  H7_TRAINING_VIEWER_PORT="${H7_TRAINING_VIEWER_PORT:-9488}" \
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    SG_ROOT="${SG_ROOT:-}" bash "$launch" start >>"$(nexus_boot_impl_log_path)" 2>&1 || true
}

nexus_boot_impl_verify_integrity() {
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/self-defense.sh" ]] || return 0
  # shellcheck source=/dev/null
  source "${NEXUS_INSTALL_ROOT}/lib/self-defense.sh"
  nexus_verify_integrity 2>/dev/null || true
}

nexus_boot_impl_sign_manifest() {
  [[ "$(id -u)" -ne 0 ]] && return 0
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/self-defense.sh" ]] || return 0
  # shellcheck source=/dev/null
  source "${NEXUS_INSTALL_ROOT}/lib/self-defense.sh"
  nexus_sign_manifest "${NEXUS_INSTALL_ROOT}/MANIFEST.sha256" 2>/dev/null || true
}

nexus_boot_impl_ensure_dirs() {
  mkdir -p "${NEXUS_STATE_DIR}" "${NEXUS_STATE_DIR}/hostess7-cache" 2>/dev/null || true
  touch "$(nexus_boot_impl_log_path)" 2>/dev/null || true
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
  nexus_boot_impl_sign_manifest
  nexus_boot_impl_verify_integrity
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
  nexus_boot_impl_verify_integrity
  nexus_boot_impl_sense_meld && meld=1
  nexus_boot_impl_training_viewer

  nexus_boot_impl_record refresh "$wired" "$meld"
  nexus_log "INFO" "boot-impl" "BOOT_REFRESH done wired=${wired} meld=${meld}"
}

nexus_boot_impl_run() {
  nexus_boot_impl_enabled || return 0
  if nexus_boot_impl_is_first; then
    nexus_boot_impl_first
  else
    nexus_boot_impl_refresh
  fi
}
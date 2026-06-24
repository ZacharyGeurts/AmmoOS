#!/bin/bash
# Field Drive System — whole NEXUS on TEAM fieldstorage; minimal browser talk path.

HOSTESS7_TEAM_FIELD="${HOSTESS7_TEAM_FIELD:-/media/default/HOSTESS7_TEAM/fieldstorage}"
HOSTESS7_ROOT="${HOSTESS7_ROOT:-/home/default/Desktop/SG/Hostess7}"

nexus_field_drive_root() {
  local local_mirror="${NEXUS_INSTALL_ROOT:-.}/.nexus-field-drive"
  if [[ -d "${local_mirror}/nexus-field/state" ]]; then
    printf '%s\n' "${local_mirror}"
    return 0
  fi
  if [[ -d "${HOSTESS7_TEAM_FIELD}/nexus-field" ]]; then
    printf '%s\n' "${HOSTESS7_TEAM_FIELD}"
    return 0
  fi
  if [[ -d "${HOSTESS7_TEAM_FIELD}/brain" ]]; then
    printf '%s\n' "${HOSTESS7_TEAM_FIELD}"
    return 0
  fi
  if [[ -d "${HOSTESS7_ROOT}/cache/fieldstorage/nexus-field" ]]; then
    printf '%s\n' "${HOSTESS7_ROOT}/cache/fieldstorage"
    return 0
  fi
  if [[ -d "${HOSTESS7_ROOT}/cache/fieldstorage/brain" ]]; then
    printf '%s\n' "${HOSTESS7_ROOT}/cache/fieldstorage"
    return 0
  fi
  printf '%s\n' "${HOSTESS7_TEAM_FIELD}"
}

nexus_field_drive_apply_paths() {
  [[ "${NEXUS_FIELD_DRIVE:-1}" == "1" ]] || return 0
  local root field_base state_on_drive
  root="$(nexus_field_drive_root 2>/dev/null)" || return 0
  field_base="${root}/nexus-field"
  state_on_drive="${field_base}/state"
  [[ -d "$state_on_drive" ]] || return 0
  [[ -f "${field_base}/active.json" || -f "${field_base}/manifest.json" ]] || return 0

  export NEXUS_HOST_STATE_DIR="${NEXUS_HOST_STATE_DIR:-/var/lib/nexus-shield}"
  export NEXUS_FIELD_DRIVE_ACTIVE=1
  export NEXUS_FIELD_DRIVE_ROOT="$field_base"
  export NEXUS_FIELD_DRIVE_STATE="$state_on_drive"
  export NEXUS_STATE_DIR="$state_on_drive"
  export NEXUS_SHADOW_DIR="${NEXUS_STATE_DIR}/shadow"
  export NEXUS_BEHAVIOR_DIR="${NEXUS_STATE_DIR}/behavior"
  export NEXUS_VIGIL_STATE="${NEXUS_STATE_DIR}/vigil.state"

  mkdir -p "$NEXUS_STATE_DIR" "$NEXUS_SHADOW_DIR" "$NEXUS_BEHAVIOR_DIR" \
    "${field_base}/talk/inbox" "${field_base}/talk/outbox" "${field_base}/run" 2>/dev/null || true
  return 0
}

nexus_field_drive_publish() {
  [[ "${NEXUS_FIELD_DRIVE:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-drive-system.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}" \
    NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    HOSTESS7_TEAM_FIELD="$HOSTESS7_TEAM_FIELD" \
    HOSTESS7_ROOT="$HOSTESS7_ROOT" \
    python3 "$py" sync >/dev/null 2>&1 || true
}

nexus_field_drive_publish_full() {
  [[ "${NEXUS_FIELD_DRIVE:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-drive-system.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}" \
    NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    HOSTESS7_TEAM_FIELD="$HOSTESS7_TEAM_FIELD" \
    HOSTESS7_ROOT="$HOSTESS7_ROOT" \
    python3 "$py" publish >/dev/null 2>&1 || true
}

nexus_field_drive_json() {
  if declare -f nexus_field_drive_publish >/dev/null 2>&1; then
    nexus_field_drive_publish
  fi
  local py="${NEXUS_INSTALL_ROOT}/lib/field-drive-system.py"
  if [[ -f "$py" ]]; then
    NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}" \
      NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
      HOSTESS7_TEAM_FIELD="$HOSTESS7_TEAM_FIELD" \
      HOSTESS7_ROOT="$HOSTESS7_ROOT" \
      python3 "$py" json 2>/dev/null && return 0
  fi
  printf '{"schema":"field-drive-system/v1","drive_mounted":false,"whole_system_on_drive":false,"drives":[],"gui_on_drive":false,"panel_url":"/field"}'
}

nexus_field_drive_inbox_loop() {
  [[ "${NEXUS_FIELD_DRIVE:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-drive-system.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}" \
    NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    HOSTESS7_TEAM_FIELD="$HOSTESS7_TEAM_FIELD" \
    python3 "$py" inbox >/dev/null 2>&1 || true
}
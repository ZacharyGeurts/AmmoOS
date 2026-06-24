#!/bin/bash
# Field Outside ASM — build minimal egress probe binary (field-fast, no shell deps).

[[ -f "${NEXUS_INSTALL_ROOT}/lib/nexus-common.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/nexus-common.sh"

NEXUS_FIELD_OUTSIDE_ASM="${NEXUS_FIELD_OUTSIDE_ASM:-${NEXUS_INSTALL_ROOT}/lib/bin/field-outside-asm}"
NEXUS_FIELD_OUTSIDE_ASM_SRC="${NEXUS_INSTALL_ROOT}/lib/field-outside-asm.c"

nexus_field_outside_asm_build() {
  [[ "${NEXUS_FIELD_OUTSIDE_TALK:-1}" == "1" ]] || return 0
  command -v gcc >/dev/null 2>&1 || {
    if declare -f nexus_log >/dev/null 2>&1; then
      nexus_log "WARN" "field-outside-asm" "gcc missing — ASM probe unavailable; socket fallback only"
    fi
    return 1
  }
  local src="${NEXUS_FIELD_OUTSIDE_ASM_SRC}"
  [[ -f "$src" ]] || src="${NEXUS_INSTALL_ROOT}/lib/field-outside-asm.c"
  [[ -f "$src" ]] || return 1
  local out_dir
  out_dir="$(dirname "$NEXUS_FIELD_OUTSIDE_ASM")"
  mkdir -p "$out_dir" 2>/dev/null || true
  local err
  err="$(gcc -O2 -pipe -fstack-protector-strong -D_FORTIFY_SOURCE=2 -fPIE -pie \
    -o "$NEXUS_FIELD_OUTSIDE_ASM" "$src" 2>&1)" || {
    if declare -f nexus_log >/dev/null 2>&1; then
      nexus_log "WARN" "field-outside-asm" "build failed: ${err}"
    fi
    return 1
  }
  chmod 755 "$NEXUS_FIELD_OUTSIDE_ASM" 2>/dev/null || true
  if declare -f nexus_log >/dev/null 2>&1; then
    nexus_log "INFO" "field-outside-asm" "ASM probe built path=${NEXUS_FIELD_OUTSIDE_ASM}"
  fi
  return 0
}

nexus_field_outside_asm_path() {
  if [[ -x "$NEXUS_FIELD_OUTSIDE_ASM" ]]; then
    printf '%s' "$NEXUS_FIELD_OUTSIDE_ASM"
    return 0
  fi
  if declare -f nexus_field_outside_asm_build >/dev/null 2>&1; then
    nexus_field_outside_asm_build >/dev/null 2>&1 || true
  fi
  [[ -x "$NEXUS_FIELD_OUTSIDE_ASM" ]] && printf '%s' "$NEXUS_FIELD_OUTSIDE_ASM"
}
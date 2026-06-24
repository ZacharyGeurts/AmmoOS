#!/bin/bash
# Field Wave ASM — build field-fast RTL-SDR USB probe (no lsusb).

[[ -f "${NEXUS_INSTALL_ROOT}/lib/nexus-common.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/nexus-common.sh"

NEXUS_FIELD_WAVE_ASM="${NEXUS_FIELD_WAVE_ASM:-${NEXUS_INSTALL_ROOT}/lib/bin/field-wave-asm}"
NEXUS_FIELD_WAVE_ASM_SRC="${NEXUS_INSTALL_ROOT}/lib/field-wave-asm.c"

nexus_field_wave_asm_build() {
  [[ "${NEXUS_FIELD_WAVE:-1}" == "1" ]] || return 0
  command -v gcc >/dev/null 2>&1 || {
    if declare -f nexus_log >/dev/null 2>&1; then
      nexus_log "WARN" "field-wave-asm" "gcc missing — sysfs Python fallback only"
    fi
    return 1
  }
  local src="${NEXUS_FIELD_WAVE_ASM_SRC}"
  [[ -f "$src" ]] || src="${NEXUS_INSTALL_ROOT}/lib/field-wave-asm.c"
  [[ -f "$src" ]] || return 1
  local out_dir
  out_dir="$(dirname "$NEXUS_FIELD_WAVE_ASM")"
  mkdir -p "$out_dir" 2>/dev/null || true
  local err
  err="$(gcc -O2 -pipe -fstack-protector-strong -D_FORTIFY_SOURCE=2 -fPIE -pie \
    -o "$NEXUS_FIELD_WAVE_ASM" "$src" 2>&1)" || {
    if declare -f nexus_log >/dev/null 2>&1; then
      nexus_log "WARN" "field-wave-asm" "build failed: ${err}"
    fi
    return 1
  }
  chmod 755 "$NEXUS_FIELD_WAVE_ASM" 2>/dev/null || true
  if declare -f nexus_log >/dev/null 2>&1; then
    nexus_log "INFO" "field-wave-asm" "ASM probe built path=${NEXUS_FIELD_WAVE_ASM}"
  fi
  return 0
}

nexus_field_wave_asm_path() {
  if [[ -x "$NEXUS_FIELD_WAVE_ASM" ]]; then
    printf '%s' "$NEXUS_FIELD_WAVE_ASM"
    return 0
  fi
  if declare -f nexus_field_wave_asm_build >/dev/null 2>&1; then
    nexus_field_wave_asm_build >/dev/null 2>&1 || true
  fi
  [[ -x "$NEXUS_FIELD_WAVE_ASM" ]] && printf '%s' "$NEXUS_FIELD_WAVE_ASM"
}
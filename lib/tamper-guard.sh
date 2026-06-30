#!/bin/bash
# Tamper Guard — verify manifest, auto-restore from seal, refuse tampered loads.

nexus_tamper_guard_cycle() {
  [[ "${NEXUS_TAMPER_GUARD:-1}" == "1" ]] || return 0
  nexus_verify_integrity && return 0
  nexus_alert "tamper-guard" "TAMPER_GUARD_ALERT integrity_fail"
  [[ "${NEXUS_TAMPER_AUTO_RESTORE:-1}" == "1" ]] || return 1
  nexus_tamper_restore_from_seal
  nexus_sign_manifest
  nexus_verify_integrity
}

nexus_tamper_restore_from_seal() {
  [[ -f "${NEXUS_SEAL_MANIFEST:-${NEXUS_STATE_DIR}/sealed/MANIFEST.sealed}" ]] || return 1
  nexus_seal_unseal
  local fail=0 hash path rel install_path current
  while read -r hash path; do
    [[ -n "$hash" && -n "$path" ]] || continue
    rel="${path#./}"
    install_path="${NEXUS_INSTALL_ROOT}/${rel}"
    [[ -f "$install_path" ]] || { nexus_seal_restore_path "$install_path" || fail=1; continue; }
    current="$(sha256sum "$install_path" | awk '{print $1}')"
    [[ "$current" == "$hash" ]] && continue
    nexus_seal_restore_path "$install_path" || fail=1
  done <"${NEXUS_SEAL_MANIFEST}"
  nexus_manifest_unlock
  command -v chattr >/dev/null 2>&1 && chattr -R +i "${NEXUS_SEAL_DIR}" 2>/dev/null || true
  [[ "$fail" -eq 0 ]]
}
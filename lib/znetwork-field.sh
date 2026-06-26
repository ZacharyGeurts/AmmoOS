#!/bin/bash
# ZNetwork — field secure network manager (REVIEW_ONLY integration, zero mutation).

ZNETWORK_ROOT="${ZNETWORK_ROOT:-${SG_ROOT:-}/ZNetwork}"
ZNETWORK_BIN="${ZNETWORK_BIN:-}"
ZNETWORK_MODE="${ZNETWORK_MODE:-REVIEW_ONLY}"
ZNETWORK_OPERATOR_JSON="${NEXUS_STATE_DIR}/znetwork-operator.json"
ZNETWORK_SKIP_MARKER="${NEXUS_STATE_DIR}/znetwork-skip.marker"
ZNETWORK_SOCK="${NEXUS_STATE_DIR}/znetwork-field.sock"

nexus_znetwork_bin() {
  local candidate
  for candidate in \
    "${ZNETWORK_BIN}" \
    "${NEXUS_INSTALL_ROOT}/bin/znetwork" \
    "${NEXUS_INSTALL_ROOT}/bin/znetwork.exe" \
    "${ZNETWORK_ROOT}/build/znetwork" \
    "${ZNETWORK_ROOT}/build/znetwork.exe" \
    "${SG_ROOT}/ZNetwork/build/znetwork" \
    "${SG_ROOT}/ZNetwork/build/znetwork.exe"; do
    [[ -n "$candidate" && -x "$candidate" ]] || continue
    printf '%s' "$candidate"
    return 0
  done
  return 1
}

nexus_znetwork_write_operator() {
  local choice="$1"
  local running="${2:-0}"
  mkdir -p "${NEXUS_STATE_DIR}" 2>/dev/null || true
  printf '{"choice":"%s","running":%s,"mode":"%s","updated":"%s"}\n' \
    "$choice" "$running" "${ZNETWORK_MODE}" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    >"${ZNETWORK_OPERATOR_JSON}" 2>/dev/null || true
}

nexus_znetwork_is_running() {
  [[ -S "${ZNETWORK_SOCK}" ]] && return 0
  if [[ -f "${ZNETWORK_OPERATOR_JSON}" ]]; then
    grep -q '"running"[[:space:]]*:[[:space:]]*true' "${ZNETWORK_OPERATOR_JSON}" 2>/dev/null \
      && grep -q '"choice"[[:space:]]*:[[:space:]]*"yes"' "${ZNETWORK_OPERATOR_JSON}" 2>/dev/null \
      && return 0
  fi
  pgrep -f '[z]network.*policy' >/dev/null 2>&1 && return 0
  return 1
}

nexus_znetwork_mark_running() {
  nexus_znetwork_write_operator "yes" "true"
  mkdir -p "${NEXUS_STATE_DIR}" 2>/dev/null || true
  rm -f "${ZNETWORK_SKIP_MARKER}" 2>/dev/null || true
  : >"${ZNETWORK_SOCK}" 2>/dev/null || true
  chmod 600 "${ZNETWORK_SOCK}" 2>/dev/null || true
}

nexus_znetwork_activate_log() {
  local step="$1" status="$2" detail="${3:-}"
  local log="${NEXUS_STATE_DIR}/znetwork-activate.jsonl"
  mkdir -p "${NEXUS_STATE_DIR}" 2>/dev/null || true
  printf '{"ts":"%s","step":"%s","status":"%s","detail":"%s"}\n' \
    "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$step" "$status" "$detail" >>"$log" 2>/dev/null || true
  nexus_log "INFO" "znetwork" "ACTIVATE_${status} step=${step} ${detail}"
}

# User-space swap — no sudo, no password prompt. Native NM stays up; field bridges attach in software.
nexus_znetwork_user_attach() {
  local bin iface shadow="${NEXUS_STATE_DIR}/znetwork-shadow.json"
  bin="$(nexus_znetwork_bin)" || return 1
  iface="$("${bin}" probe --json 2>/dev/null | sed -n 's/.*"iface"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
  [[ -n "$iface" ]] || iface="$(ip -4 route show default 2>/dev/null | awk '{print $5; exit}')"

  if [[ -f "${NEXUS_STATE_DIR}/znetwork-status.json" ]]; then
    cp -f "${NEXUS_STATE_DIR}/znetwork-status.json" "$shadow" 2>/dev/null || true
    nexus_znetwork_activate_log "shadow_mirror" "OK" "file=${shadow}"
  fi

  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/field-dns.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/field-dns.sh"
    declare -f nexus_field_dns_publish >/dev/null 2>&1 && nexus_field_dns_publish 2>/dev/null || true
    nexus_znetwork_activate_log "truth_dns_panel" "OK" "loopback_publish_no_resolv_override"
  fi

  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/gatekeeper-enforce.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/gatekeeper-enforce.sh"
    declare -f nexus_gatekeeper_enforce_strict >/dev/null 2>&1 \
      && nexus_gatekeeper_enforce_strict 2>/dev/null || true
    nexus_znetwork_activate_log "gatekeeper_iff" "OK" "user_space_scoring"
  fi

  nexus_znetwork_activate_log "native_manager" "UNCHANGED" "iface=${iface:-unknown} swap=software_only"
  return 0
}

nexus_znetwork_activate_on_yes() {
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/front-hook.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/front-hook.sh"
    nexus_front_hook_board 2>/dev/null || true
  fi
  nexus_znetwork_activate_log "operator_accept" "OK" "choice=yes mode=${ZNETWORK_MODE} front_hook=1 pass_through=0"
  nexus_znetwork_triple_check || {
    nexus_znetwork_activate_log "complete" "FAIL" "triple_check"
    return 1
  }
  nexus_znetwork_activate_log "triple_check" "OK" "mode=${ZNETWORK_MODE}"

  nexus_znetwork_user_attach || true
  nexus_znetwork_mark_running
  nexus_znetwork_activate_log "complete" "OK" "running=true swap=user_space"
  return 0
}

nexus_znetwork_startup_prompt() {
  [[ "${NEXUS_ZNETWORK:-1}" == "1" ]] || return 0
  [[ "${NEXUS_ZNETWORK_PROMPT:-1}" == "1" ]] || return 0
  nexus_znetwork_is_running && return 0
  [[ -f "${ZNETWORK_SKIP_MARKER}" ]] && return 0

  local bin rc=0 choice
  bin="$(nexus_znetwork_bin)" || {
    nexus_log "WARN" "znetwork" "STARTUP_SKIP reason=binary_missing"
    return 0
  }

  export SG_ROOT="${SG_ROOT:-$(cd "${NEXUS_INSTALL_ROOT}/.." 2>/dev/null && pwd)}"
  export ZNETWORK_MODE="${ZNETWORK_MODE}"
  export DISPLAY="${DISPLAY:-:0}"

  local out
  out="$("${bin}" startup 2>&1)" || rc=$?
  choice="$(printf '%s\n' "$out" | sed -n 's/^CHOICE=//p' | tail -1)"
  if [[ -z "$choice" ]]; then
    case "$rc" in
      0) choice="yes" ;;
      1) choice="no" ;;
      2) choice="skip" ;;
      *) choice="unavailable" ;;
    esac
  fi

  case "$choice" in
    yes)
      nexus_log "INFO" "znetwork" "STARTUP_YES operator=accepted"
      nexus_znetwork_activate_on_yes || true
      ;;
    no)
      nexus_znetwork_write_operator "no" "false"
      nexus_log "INFO" "znetwork" "STARTUP_NO operator=declined"
      ;;
    skip)
      nexus_znetwork_write_operator "skip" "false"
      : >"${ZNETWORK_SKIP_MARKER}"
      nexus_log "WARN" "znetwork" "STARTUP_SKIP operator=skipped_not_recommended"
      ;;
    *)
      nexus_log "WARN" "znetwork" "STARTUP_DIALOG_UNAVAILABLE install=zenity|yad|kdialog"
      ;;
  esac
}

nexus_znetwork_triple_check() {
  local bin probe_ok=0 status_ok=0 gate_ok=0 out="${NEXUS_STATE_DIR}/znetwork-status.json"
  bin="$(nexus_znetwork_bin)" || {
    nexus_log "WARN" "znetwork" "BINARY_MISSING path=${ZNETWORK_BIN}"
    return 1
  }
  export SG_ROOT="${SG_ROOT:-$(cd "${NEXUS_INSTALL_ROOT}/.." 2>/dev/null && pwd)}"
  export ZNETWORK_MODE="${ZNETWORK_MODE}"
  mkdir -p "${NEXUS_STATE_DIR}" 2>/dev/null || true

  if "${bin}" probe --json >/dev/null 2>&1; then
    probe_ok=1
  fi
  if "${bin}" status --json >"${out}.tmp" 2>/dev/null; then
    status_ok=1
    mv -f "${out}.tmp" "${out}" 2>/dev/null || cp "${out}.tmp" "${out}" 2>/dev/null || true
    rm -f "${out}.tmp" 2>/dev/null || true
  else
    rm -f "${out}.tmp" 2>/dev/null || true
  fi
  if [[ -x "${ZNETWORK_ROOT}/scripts/znetwork-review-gate.sh" ]]; then
    ZNETWORK_BIN="${bin}" SG_ROOT="${SG_ROOT}" ZNETWORK_MODE="${ZNETWORK_MODE}" \
      "${ZNETWORK_ROOT}/scripts/znetwork-review-gate.sh" >/dev/null 2>&1 && gate_ok=1
  fi

  if [[ "$probe_ok" -eq 1 && "$status_ok" -eq 1 && "$gate_ok" -eq 1 ]]; then
    nexus_log "INFO" "znetwork" "TRIPLE_CHECK_OK mode=${ZNETWORK_MODE} ready=REVIEW"
    return 0
  fi
  nexus_log "WARN" "znetwork" "TRIPLE_CHECK_FAIL probe=${probe_ok} status=${status_ok} gate=${gate_ok}"
  return 1
}

nexus_znetwork_publish() {
  [[ "${NEXUS_ZNETWORK:-1}" == "1" ]] || return 0
  nexus_znetwork_triple_check || return 1
}

nexus_znetwork_build() {
  [[ -d "${ZNETWORK_ROOT}" ]] || return 1
  command -v cmake >/dev/null 2>&1 || return 1
  (
    cd "${ZNETWORK_ROOT}"
    cmake -B build -DCMAKE_BUILD_TYPE=Release >/dev/null 2>&1
    cmake --build build >/dev/null 2>&1
  ) && nexus_znetwork_bin >/dev/null 2>&1
}

nexus_znetwork_status_line() {
  local out="${NEXUS_STATE_DIR}/znetwork-status.json"
  if nexus_znetwork_is_running; then
    printf 'znetwork=running'
    [[ -f "$out" ]] && printf ' status=%s' "$out"
    printf '\n'
  elif [[ -f "$out" ]]; then
    printf 'znetwork=ready file=%s\n' "$out"
  elif nexus_znetwork_bin >/dev/null 2>&1; then
    printf 'znetwork=binary_ok status=pending\n'
  else
    printf 'znetwork=missing\n'
  fi
}
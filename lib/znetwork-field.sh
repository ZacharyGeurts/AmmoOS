#!/bin/bash
# ZNetwork v2 — NewLatest integrated field secure network manager.
# Truth-gated orchestrator + taskbar swap after pol elevation.

if [[ -f "${NEXUS_INSTALL_ROOT:-}/lib/nexus-polkit.sh" ]]; then
  # shellcheck source=/dev/null
  source "${NEXUS_INSTALL_ROOT}/lib/nexus-polkit.sh"
elif [[ -f "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/nexus-polkit.sh" ]]; then
  # shellcheck source=/dev/null
  source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/nexus-polkit.sh"
fi

if [[ -f "${NEXUS_INSTALL_ROOT:-}/lib/sg-paths.sh" ]]; then
  # shellcheck source=/dev/null
  source "${NEXUS_INSTALL_ROOT}/lib/sg-paths.sh"
  sg_paths_export_defaults 2>/dev/null || true
fi

# Prefer integrated NewLatest/znetwork over legacy SG/ZNetwork tree.
ZNETWORK_ROOT="${ZNETWORK_ROOT:-${NEXUS_INSTALL_ROOT}/znetwork}"
[[ -d "${ZNETWORK_ROOT}" ]] || ZNETWORK_ROOT="${SG_ROOT:-}/ZNetwork"
ZNETWORK_BIN="${ZNETWORK_BIN:-}"
ZNETWORK_MODE="${ZNETWORK_MODE:-REVIEW_ONLY}"
ZNETWORK_OPERATOR_JSON="${NEXUS_STATE_DIR}/znetwork-operator.json"
ZNETWORK_SKIP_MARKER="${NEXUS_STATE_DIR}/znetwork-skip.marker"
ZNETWORK_RUNNING_MARKER="${NEXUS_STATE_DIR}/znetwork-running.marker"
ZNETWORK_SOCK="${NEXUS_STATE_DIR}/znetwork-field.sock"
ZNETWORK_ORCHESTRATOR="${NEXUS_INSTALL_ROOT}/lib/znetwork-orchestrator.py"
ZNETWORK_HOSTILE_PY="${NEXUS_INSTALL_ROOT}/lib/znetwork-hostile-threat.py"

nexus_znetwork_bin() {
  local candidate
  for candidate in \
    "${ZNETWORK_BIN}" \
    "${NEXUS_INSTALL_ROOT}/bin/znetwork" \
    "${NEXUS_INSTALL_ROOT}/bin/znetwork.exe" \
    "${ZNETWORK_ROOT}/build/znetwork" \
    "${SG_ROOT}/ZNetwork/build/znetwork" \
    "${SG_ROOT}/ZNetwork/build/znetwork.exe"; do
    [[ -n "$candidate" && -x "$candidate" ]] || continue
    printf '%s' "$candidate"
    return 0
  done
  return 1
}

nexus_znetwork_review_gate_script() {
  local candidate
  for candidate in \
    "${NEXUS_INSTALL_ROOT}/znetwork/scripts/znetwork-review-gate.sh" \
    "${ZNETWORK_ROOT}/scripts/znetwork-review-gate.sh" \
    "${SG_ROOT}/ZNetwork/scripts/znetwork-review-gate.sh"; do
    [[ -x "$candidate" ]] || continue
    printf '%s' "$candidate"
    return 0
  done
  return 1
}

nexus_znetwork_hostile_py() {
  local runner="${NEXUS_PYTHONG:-pythong}"
  command -v "$runner" >/dev/null 2>&1 || runner="python3"
  [[ -f "${ZNETWORK_HOSTILE_PY}" ]] || return 1
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    "$runner" "${ZNETWORK_HOSTILE_PY}" "$@"
}

nexus_znetwork_hostile_scan() {
  if nexus_znetwork_hostile_py scan >/dev/null 2>&1; then
    nexus_znetwork_activate_log "hostile_scan" "OK" "immediate_iff"
    return 0
  fi
  if nexus_znetwork_orchestrator_py hostile-scan >/dev/null 2>&1; then
    nexus_znetwork_activate_log "hostile_scan" "OK" "via=orchestrator"
    return 0
  fi
  nexus_znetwork_activate_log "hostile_scan" "SKIP" "hostile_module_unavailable"
  return 0
}

nexus_znetwork_hostile_respond() {
  if nexus_znetwork_hostile_py countermeasure >/dev/null 2>&1; then
    nexus_znetwork_activate_log "hostile_respond" "OK" "zero_hesitation"
    return 0
  fi
  if nexus_znetwork_orchestrator_py hostile-respond >/dev/null 2>&1; then
    nexus_znetwork_activate_log "hostile_respond" "OK" "via=orchestrator"
    return 0
  fi
  nexus_znetwork_activate_log "hostile_respond" "SKIP" "hostile_module_unavailable"
  return 0
}

nexus_znetwork_orchestrator_py() {
  local runner="${NEXUS_PYTHONG:-pythong}"
  command -v "$runner" >/dev/null 2>&1 || runner="python3"
  [[ -f "${ZNETWORK_ORCHESTRATOR}" ]] || return 1
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
  ZNETWORK_BIN="$(nexus_znetwork_bin 2>/dev/null || true)" \
  ZNETWORK_MODE="${ZNETWORK_MODE}" \
    "$runner" "${ZNETWORK_ORCHESTRATOR}" "$@"
}

nexus_znetwork_write_operator() {
  local choice="$1"
  local running="${2:-0}"
  mkdir -p "${NEXUS_STATE_DIR}" 2>/dev/null || true
  printf '{"choice":"%s","running":%s,"mode":"%s","updated":"%s","orchestrator":"znetwork-orchestrator/v2"}\n' \
    "$choice" "$running" "${ZNETWORK_MODE}" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    >"${ZNETWORK_OPERATOR_JSON}" 2>/dev/null || true
  if [[ "$choice" == "yes" && "$running" == "true" ]]; then
    : >"${ZNETWORK_RUNNING_MARKER}" 2>/dev/null || true
    chmod 600 "${ZNETWORK_RUNNING_MARKER}" 2>/dev/null || true
  else
    rm -f "${ZNETWORK_RUNNING_MARKER}" 2>/dev/null || true
  fi
}

nexus_znetwork_is_running() {
  [[ -f "${ZNETWORK_RUNNING_MARKER}" ]] && return 0
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
  if declare -f nexus_znetwork_orchestrator_py >/dev/null 2>&1 \
    && nexus_znetwork_orchestrator_py mark-running >/dev/null 2>&1; then
    return 0
  fi
  nexus_znetwork_write_operator "yes" "true"
  mkdir -p "${NEXUS_STATE_DIR}" 2>/dev/null || true
  rm -f "${ZNETWORK_SKIP_MARKER}" 2>/dev/null || true
  : >"${ZNETWORK_RUNNING_MARKER}" 2>/dev/null || true
  chmod 600 "${ZNETWORK_RUNNING_MARKER}" 2>/dev/null || true
}

nexus_znetwork_activate_log() {
  local step="$1" status="$2" detail="${3:-}"
  local log="${NEXUS_STATE_DIR}/znetwork-activate.jsonl"
  mkdir -p "${NEXUS_STATE_DIR}" 2>/dev/null || true
  printf '{"ts":"%s","step":"%s","status":"%s","detail":"%s"}\n' \
    "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$step" "$status" "$detail" >>"$log" 2>/dev/null || true
  nexus_log "INFO" "znetwork" "ACTIVATE_${status} step=${step} ${detail}"
}

nexus_znetwork_tray_swap() {
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/panel-tray.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/panel-tray.sh"
    export NEXUS_TRAY_MODE=znetwork
    export NEXUS_TRAY_ICON_REFRESH=1
    nexus_panel_tray_znetwork_swap 2>/dev/null && {
      nexus_znetwork_activate_log "tray_swap" "OK" "mode=znetwork"
      return 0
    }
  fi
  if nexus_znetwork_orchestrator_py tray-swap >/dev/null 2>&1; then
    nexus_znetwork_activate_log "tray_swap" "OK" "orchestrator"
    return 0
  fi
  nexus_znetwork_activate_log "tray_swap" "FAIL" "no_tray_or_display"
  return 1
}

nexus_znetwork_handler_retire_py() {
  local runner="${NEXUS_PYTHONG:-pythong}"
  command -v "$runner" >/dev/null 2>&1 || runner="python3"
  local py="${NEXUS_INSTALL_ROOT}/lib/znetwork-handler-retire.py"
  [[ -f "$py" ]] || return 1
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
  ZNETWORK_BIN="$(nexus_znetwork_bin 2>/dev/null || true)" \
    "$runner" "$py" "$@"
}

nexus_znetwork_never_harm_os() {
  [[ "${ZNETWORK_NEVER_HARM_OS:-${NEXUS_NEVER_HARM_OS:-1}}" != "0" ]]
}

nexus_znetwork_retire_legacy_handlers() {
  nexus_znetwork_handler_retire_py retire >/dev/null 2>&1 && {
    if nexus_znetwork_never_harm_os; then
      nexus_znetwork_activate_log "handler_retire" "OK" "coexist_os_bypass_only"
    else
      nexus_znetwork_activate_log "handler_retire" "OK" "graceful_no_sudo"
    fi
    return 0
  }
  nexus_znetwork_activate_log "handler_retire" "SKIP" "handler_retire_unavailable"
  return 0
}

nexus_znetwork_replace_connection() {
  nexus_znetwork_handler_retire_py replace >/dev/null 2>&1 && {
    nexus_znetwork_activate_log "replace_connection" "OK" "policy_owner=znetwork"
    return 0
  }
  nexus_znetwork_activate_log "replace_connection" "SKIP" "replace_unavailable"
  return 0
}

# Pol root gate — optional; skipped when NEXUS_ZNETWORK_NO_SUDO=1 (default).
nexus_znetwork_pol_root_gate() {
  [[ "${NEXUS_ZNETWORK_NO_SUDO:-1}" == "1" ]] && {
    nexus_znetwork_activate_log "pol_root" "SKIP" "no_sudo_user_space"
    return 0
  }
  local pol_json root_ok=0
  if ! declare -f nexus_pol_ensure_root >/dev/null 2>&1; then
    nexus_znetwork_activate_log "pol_root" "SKIP" "nexus-polkit.sh missing"
    return 0
  fi
  pol_json="$(nexus_pol_root_json znetwork 2>/dev/null || true)"
  if [[ -n "$pol_json" ]]; then
    nexus_znetwork_activate_log "pol_root" "OK" "$pol_json"
    grep -q '"is_root"[[:space:]]*:[[:space:]]*true' <<<"$pol_json" 2>/dev/null && root_ok=1
    grep -q '"has_cached_sudo"[[:space:]]*:[[:space:]]*true' <<<"$pol_json" 2>/dev/null && root_ok=1
  fi
  if [[ "$root_ok" -eq 1 ]] || nexus_pol_is_root znetwork 2>/dev/null; then
    export NEXUS_ELEVATED_ROOT=1
    nexus_znetwork_activate_log "pol_elevated" "OK" "already_root_or_cached_sudo"
    return 0
  fi
  if nexus_pol_ensure_root znetwork; then
    export NEXUS_ELEVATED_ROOT=1
    nexus_znetwork_activate_log "pol_elevated" "OK" "secure_elevation"
    return 0
  fi
  nexus_znetwork_activate_log "pol_elevated" "FAIL" "operator_declined_or_no_gui"
  return 1
}

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

  nexus_znetwork_replace_connection || true
  nexus_znetwork_activate_log "native_manager" "BYPASSED_ALONGSIDE" "iface=${iface:-unknown} coexist_os=1"
  return 0
}

nexus_znetwork_ensure_tray() {
  [[ "${NEXUS_PANEL_TRAY:-1}" == "1" ]] || return 0
  nexus_znetwork_is_running || return 0
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/panel-tray.sh" ]] || return 0
  # shellcheck source=/dev/null
  source "${NEXUS_INSTALL_ROOT}/lib/panel-tray.sh"
  local mode
  mode="$(nexus_panel_tray_mode)"
  if [[ "$mode" != "znetwork" ]] || ! nexus_panel_tray_is_running; then
    export NEXUS_TRAY_MODE=znetwork
    export NEXUS_TRAY_ICON_REFRESH=1
    nexus_panel_tray_znetwork_swap 2>/dev/null || true
    nexus_znetwork_activate_log "ensure_tray" "OK" "mode=znetwork running=$(nexus_panel_tray_is_running && echo 1 || echo 0)"
  fi
  nexus_znetwork_hostile_scan || true
  nexus_znetwork_hostile_respond || true
}

nexus_znetwork_activate_on_yes() {
  nexus_znetwork_pol_root_gate || return 1
  nexus_znetwork_retire_legacy_handlers || true
  nexus_znetwork_replace_connection || true
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/front-hook.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/front-hook.sh"
    nexus_front_hook_board 2>/dev/null || true
  fi
  nexus_znetwork_activate_log "operator_accept" "OK" "choice=yes mode=${ZNETWORK_MODE} front_hook=1"

  # Prefer v2 orchestrator (truth gate + sovereign time + tray swap).
  if nexus_znetwork_orchestrator_py activate --elevated >/dev/null 2>&1; then
    nexus_znetwork_activate_log "orchestrator" "OK" "v2_activate"
    nexus_znetwork_ensure_tray || true
    nexus_znetwork_activate_log "complete" "OK" "running=true swap=tray_and_bridges"
    return 0
  fi

  nexus_znetwork_triple_check || {
    nexus_znetwork_activate_log "complete" "FAIL" "triple_check"
    return 1
  }
  nexus_znetwork_activate_log "triple_check" "OK" "mode=${ZNETWORK_MODE}"

  nexus_znetwork_user_attach || true
  nexus_znetwork_mark_running
  nexus_znetwork_tray_swap || true
  nexus_znetwork_activate_log "complete" "OK" "running=true swap=tray_legacy_path"
  return 0
}

# ZNetwork with us — auto-activate and replace legacy networking (no dialog unless prompted).
nexus_znetwork_startup_with_us() {
  [[ "${NEXUS_ZNETWORK:-1}" == "1" ]] || return 0
  if nexus_znetwork_is_running; then
    nexus_znetwork_ensure_tray || true
    nexus_znetwork_publish 2>/dev/null || true
    return 0
  fi
  [[ -f "${ZNETWORK_SKIP_MARKER}" ]] && return 0
  if [[ "${NEXUS_ZNETWORK_PROMPT:-0}" == "1" ]]; then
    nexus_znetwork_startup_prompt
    return $?
  fi
  nexus_znetwork_bin >/dev/null 2>&1 || {
    nexus_log "WARN" "znetwork" "STARTUP_WITH_US_SKIP reason=binary_missing"
    return 0
  }
  nexus_log "INFO" "znetwork" "STARTUP_WITH_US auto_activate replace_legacy=1"
  nexus_znetwork_activate_on_yes || {
    nexus_znetwork_write_operator "no" "false"
    return 1
  }
  nexus_znetwork_ensure_tray || true
  return 0
}

nexus_znetwork_startup_prompt() {
  [[ "${NEXUS_ZNETWORK:-1}" == "1" ]] || return 0
  [[ "${NEXUS_ZNETWORK_PROMPT:-0}" == "1" ]] || return 0
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
      nexus_znetwork_activate_on_yes || {
        nexus_znetwork_write_operator "no" "false"
        return 1
      }
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
  if nexus_znetwork_orchestrator_py triple-check >/dev/null 2>&1; then
    nexus_log "INFO" "znetwork" "TRIPLE_CHECK_OK mode=${ZNETWORK_MODE} via=orchestrator"
    return 0
  fi

  local bin probe_ok=0 status_ok=0 gate_ok=0 gate_script out="${NEXUS_STATE_DIR}/znetwork-status.json"
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
  gate_script="$(nexus_znetwork_review_gate_script 2>/dev/null || true)"
  if [[ -n "$gate_script" ]]; then
    ZNETWORK_BIN="${bin}" SG_ROOT="${SG_ROOT}" ZNETWORK_MODE="${ZNETWORK_MODE}" \
      NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
      "$gate_script" >/dev/null 2>&1 && gate_ok=1
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
  if nexus_znetwork_is_running; then
    nexus_znetwork_hostile_scan || true
    nexus_znetwork_hostile_respond || true
  fi
  nexus_znetwork_ensure_tray 2>/dev/null || true
}

nexus_znetwork_build() {
  [[ -d "${SG_ROOT}/ZNetwork" ]] || return 1
  command -v cmake >/dev/null 2>&1 || return 1
  (
    cd "${SG_ROOT}/ZNetwork"
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
#!/bin/bash
# NEXUS GitHub update apply — holds github-update.lock, git pull, install, restart.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"

GIT_DIR="${NEXUS_UPDATE_GIT_DIR:-$ROOT}"
INSTALL_SH="${NEXUS_UPDATE_INSTALL_SH:-${GIT_DIR}/stealth_install.sh}"
TOKEN="${NEXUS_UPDATE_LOCK_TOKEN:-}"
TARGET="${NEXUS_UPDATE_TARGET:-}"
PREVIOUS="${NEXUS_UPDATE_PREVIOUS:-}"
LOG="${NEXUS_STATE_DIR}/update-apply.log"
NEEDS_SUDO_JSON="${NEXUS_STATE_DIR}/update-needs-sudo.json"

# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/nexus-common.sh" 2>/dev/null || true
nexus_init_runtime_paths 2>/dev/null || true
# shellcheck source=/dev/null
[[ -f "${NEXUS_INSTALL_ROOT}/lib/nexus-update-lock.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/nexus-update-lock.sh"
# shellcheck source=/dev/null
[[ -f "${NEXUS_INSTALL_ROOT}/lib/panel-browser.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/panel-browser.sh"

_log() {
  printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*" | tee -a "$LOG"
}

_heartbeat_loop() {
  [[ -n "$TOKEN" ]] || return 0
  while true; do
    if ! nexus_update_lock_heartbeat "$TOKEN" 2>/dev/null | grep -q '"ok": true'; then
      break
    fi
    sleep 25
  done
}

_cleanup() {
  local rc=$?
  kill "${HB_PID:-}" 2>/dev/null || true
  if [[ $rc -eq 0 ]]; then
    rm -f "$NEEDS_SUDO_JSON" 2>/dev/null || true
  elif [[ -n "$TOKEN" ]]; then
    nexus_update_lock_phase failed "--token=${TOKEN}" 2>/dev/null || true
  fi
  if [[ -n "$TOKEN" ]]; then
    nexus_update_lock_release "$TOKEN" 2>/dev/null || nexus_update_lock_release 2>/dev/null || true
  fi
  exit "$rc"
}

_run_with_sudo() {
  local inner="$1"
  if [[ "$(id -u)" -eq 0 ]]; then
    bash -c "$inner"
    return $?
  fi
  if sudo -n true 2>/dev/null; then
    _log "sudo: cached credentials"
    sudo -E bash -c "$inner"
    return $?
  fi
  if command -v pkexec >/dev/null 2>&1 && [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
    _log "sudo: pkexec prompt"
    pkexec env \
      NEXUS_UPDATE_LOCK_TOKEN="${TOKEN}" \
      NEXUS_UPDATE_PREVIOUS_VERSION="${PREVIOUS}" \
      NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
      NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
      bash -c "$inner"
    return $?
  fi
  if command -v zenity >/dev/null 2>&1 && [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
    local pw
    pw="$(zenity --password --title="NEXUS-Shield Update" \
      --text="Administrator password required to install ${PREVIOUS} → ${TARGET} and restart NEXUS." 2>/dev/null || true)"
    if [[ -n "$pw" ]]; then
      _log "sudo: zenity password"
      printf '%s\n' "$pw" | sudo -S -E bash -c "$inner"
      return $?
    fi
    _log "sudo: zenity cancelled"
    return 3
  fi
  if command -v kdialog >/dev/null 2>&1 && [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
    local pw
    pw="$(kdialog --password "NEXUS-Shield needs sudo to install ${PREVIOUS} → ${TARGET}" 2>/dev/null || true)"
    if [[ -n "$pw" ]]; then
      _log "sudo: kdialog password"
      printf '%s\n' "$pw" | sudo -S -E bash -c "$inner"
      return $?
    fi
    return 3
  fi
  if [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
    for term in x-terminal-emulator gnome-terminal konsole xfce4-terminal xterm; do
      if command -v "$term" >/dev/null 2>&1; then
        _log "sudo: terminal prompt via ${term}"
        "$term" -e bash -c "sudo -E bash -c $(printf '%q' "$inner"); echo; read -p 'Press Enter to close…'"
        return $?
      fi
    done
  fi
  _log "sudo: no prompt method — needs manual sudo"
  mkdir -p "$(dirname "$NEEDS_SUDO_JSON")"
  printf '{"needs_sudo":true,"message":"Administrator password required","command":"cd %s && sudo bash %s","target":"%s","previous":"%s"}\n' \
    "$GIT_DIR" "$INSTALL_SH" "$TARGET" "$PREVIOUS" >"$NEEDS_SUDO_JSON"
  return 3
}

_systemd_nexus_active() {
  command -v systemctl >/dev/null 2>&1 \
    && systemctl is-enabled nexus-genius.service >/dev/null 2>&1
}

_tree_standalone() {
  [[ "${NEXUS_FIELD_STANDALONE:-}" == "1" ]] \
    || [[ "$NEXUS_INSTALL_ROOT" == "$GIT_DIR" ]] \
    || [[ ! -x /usr/local/lib/nexus-shield/lib/nexus-daemon.sh ]]
}

_restart_standalone_panel() {
  declare -f nexus_panel_stop >/dev/null 2>&1 || return 1
  nexus_update_lock_phase restarting "--token=${TOKEN}" 2>/dev/null || true
  nexus_panel_stop 2>/dev/null || true
  sleep 1
  if [[ -f "${GIT_DIR}/nexus.sh" ]]; then
    (cd "$GIT_DIR" && nohup env NEXUS_INSTALL_ROOT="$GIT_DIR" NEXUS_FIELD_STANDALONE=1 \
      NEXUS_STATE_DIR="$NEXUS_STATE_DIR" bash ./nexus.sh --no-browser --no-tray \
      >>"${NEXUS_STATE_DIR}/update-restart.log" 2>&1 &) || true
    sleep 2
  fi
}

main() {
  mkdir -p "$NEXUS_STATE_DIR"
  : >>"$LOG"
  _log "update apply start target=${TARGET} previous=${PREVIOUS} git=${GIT_DIR}"

  trap _cleanup EXIT
  [[ -n "$TOKEN" ]] || { _log "missing NEXUS_UPDATE_LOCK_TOKEN"; exit 1; }

  nexus_update_lock_adopt "$TOKEN" "nexus-update-apply" "git_fetch" | grep -q '"ok": true' \
    || { _log "lock adopt failed"; exit 1; }

  _heartbeat_loop &
  HB_PID=$!

  if [[ -d "${GIT_DIR}/.git" ]]; then
    nexus_update_lock_phase git_fetch "--token=${TOKEN}" 2>/dev/null || true
    _log "git fetch"
    git -C "$GIT_DIR" fetch --tags origin 2>&1 | tee -a "$LOG" || true
    nexus_update_lock_phase git_pull "--token=${TOKEN}" 2>/dev/null || true
    _log "git pull"
    git -C "$GIT_DIR" pull --ff-only origin main 2>&1 | tee -a "$LOG" || {
      _log "git pull failed"
      exit 1
    }
  fi

  if _tree_standalone && ! _systemd_nexus_active; then
    _log "standalone tree update — restart panel (no system install)"
    nexus_update_lock_phase restarting "--token=${TOKEN}" 2>/dev/null || true
    _restart_standalone_panel || true
    _log "standalone update complete"
    exit 0
  fi

  [[ -f "$INSTALL_SH" ]] || { _log "stealth_install missing: $INSTALL_SH"; exit 1; }

  nexus_update_lock_phase stealth_install "--token=${TOKEN}" 2>/dev/null || true
  local inner
  inner="export NEXUS_UPDATE_LOCK_TOKEN='${TOKEN}'; export NEXUS_UPDATE_PREVIOUS_VERSION='${PREVIOUS}'; cd '${GIT_DIR}' && bash '${INSTALL_SH}'"
  _log "running stealth_install"
  if ! _run_with_sudo "$inner"; then
    rc=$?
    if [[ $rc -eq 3 ]]; then
      _log "awaiting sudo — wrote ${NEEDS_SUDO_JSON}"
      nexus_update_lock_phase awaiting_sudo "--token=${TOKEN}" 2>/dev/null || true
      exit 3
    fi
    _log "stealth_install failed rc=${rc}"
    exit 1
  fi

  nexus_update_lock_phase starting_service "--token=${TOKEN}" 2>/dev/null || true
  if _systemd_nexus_active; then
    _log "systemd restart nexus-genius"
    if [[ "$(id -u)" -eq 0 ]]; then
      systemctl restart nexus-genius.service 2>&1 | tee -a "$LOG" || true
    elif sudo -n systemctl restart nexus-genius.service 2>&1 | tee -a "$LOG"; then
      :
    else
      _run_with_sudo "systemctl restart nexus-genius.service" || true
    fi
  else
    _restart_standalone_panel || true
  fi

  _log "update apply complete ${PREVIOUS} → ${TARGET}"
  exit 0
}

main "$@"
#!/usr/bin/env bash
# ZNetwork release login boot — prime sudo once, unmask NetworkManager, board relayer.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG_ROOT="${SG_ROOT:-$(cd "$ROOT/.." && pwd)}"
NEXUS_ROOT="${NEXUS_INSTALL_ROOT:-$SG_ROOT/NewLatest}"

export SG_ROOT
export NEXUS_INSTALL_ROOT="$NEXUS_ROOT"
export ZNETWORK_ROOT="$ROOT"
export ZNETWORK_BIN="${ZNETWORK_BIN:-$ROOT/build/znetwork}"
export ZNETWORK_MODE=ACTIVE
export ZNETWORK_RELAYER=1
export ZNETWORK_UNDERHOOK=0
export ZNETWORK_FAST=1
export ZNETWORK_NO_REVIEW=1
export ZNETWORK_REVIEW_APPROVED=1
export ZNETWORK_LAB_GATE_OK=1
export ZNETWORK_OUTSIDE_LAB=1
export ZNETWORK_SMART_INSIDE=1
export ZNETWORK_TAKEOVER=0
export ZNETWORK_NEVER_HARM_OS=1
export NEXUS_NEVER_HARM_OS=1
export NEXUS_ZNETWORK=1
export NEXUS_ZNETWORK_NO_SUDO=0
export ZNETWORK_RETIRE_NM_SYSTEMD=0
export ZNETWORK_STARTUP_RETIRE="${ZNETWORK_STARTUP_RETIRE:-1}"
export ZNETWORK_AUTOSTART=1

LOG="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}/znetwork-boot.log"
mkdir -p "${NEXUS_STATE_DIR:-/var/lib/nexus-shield}" 2>/dev/null || true
{
  echo "=== znetwork-boot $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
  echo "sg_root=${SG_ROOT} znetwork_root=${ROOT} nexus=${NEXUS_ROOT}"
} >>"$LOG" 2>/dev/null || true

# shellcheck source=/dev/null
[[ -f "$NEXUS_ROOT/lib/nexus-common.sh" ]] && source "$NEXUS_ROOT/lib/nexus-common.sh"
declare -f nexus_init_runtime_paths >/dev/null 2>&1 && nexus_init_runtime_paths 2>/dev/null || true
declare -f nexus_load_config >/dev/null 2>&1 && nexus_load_config 2>/dev/null || true

# shellcheck source=/dev/null
[[ -f "$NEXUS_ROOT/lib/nexus-polkit.sh" ]] && source "$NEXUS_ROOT/lib/nexus-polkit.sh"
# shellcheck source=/dev/null
[[ -f "$NEXUS_ROOT/lib/znetwork-field.sh" ]] && source "$NEXUS_ROOT/lib/znetwork-field.sh"

# Prime sudo once — zenity/pkexec via nexus-polkit; never hardcoded passwords.
if [[ "$(id -u)" -ne 0 ]]; then
  if declare -f nexus_pol_has_cached_sudo >/dev/null 2>&1 && nexus_pol_has_cached_sudo; then
    declare -f nexus_pol_start_sudo_keepalive >/dev/null 2>&1 && nexus_pol_start_sudo_keepalive 2>/dev/null || true
    echo "sudo_prime=cached" >>"$LOG" 2>/dev/null || true
  elif declare -f nexus_pol_ensure_root >/dev/null 2>&1; then
    if nexus_pol_ensure_root znetwork >>"$LOG" 2>&1; then
      echo "sudo_prime=pol_ensure_root" >>"$LOG" 2>/dev/null || true
    else
      echo "sudo_prime=skipped_no_auth" >>"$LOG" 2>/dev/null || true
    fi
  elif declare -f nexus_znetwork_prime_sudo_once >/dev/null 2>&1; then
    nexus_znetwork_prime_sudo_once >>"$LOG" 2>&1 || true
  fi
fi

# Unmask + enable + start NetworkManager (may be masked after prior retire).
if declare -f nexus_znetwork_ensure_host_network >/dev/null 2>&1; then
  nexus_znetwork_ensure_host_network >>"$LOG" 2>&1 || true
elif command -v systemctl >/dev/null 2>&1; then
  nm_enabled="$(systemctl is-enabled NetworkManager 2>/dev/null || echo unknown)"
  if [[ "$nm_enabled" == "masked" ]]; then
    sudo systemctl unmask NetworkManager 2>/dev/null \
      || pkexec systemctl unmask NetworkManager 2>/dev/null || true
  fi
  sudo systemctl enable NetworkManager 2>/dev/null || true
  sudo systemctl start NetworkManager 2>/dev/null || true
fi

# Board relayer — sole internet in/out after host network is restored.
if declare -f nexus_znetwork_startup_with_us >/dev/null 2>&1; then
  nexus_znetwork_startup_with_us >>"$LOG" 2>&1 || true
elif declare -f nexus_znetwork_relayer_board >/dev/null 2>&1; then
  nexus_znetwork_relayer_board >>"$LOG" 2>&1 || true
fi

echo "znetwork-boot complete" >>"$LOG" 2>/dev/null || true
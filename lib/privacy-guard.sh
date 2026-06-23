#!/bin/bash
# Privacy Guard — detect unauthorized viewing of sensitive paths.

NEXUS_PRIVACY_SENSITIVE=(
  /etc/shadow
  /etc/gshadow
  /etc/sudoers
)

nexus_privacy_add_user_paths() {
  local home
  for home in /home/* /root; do
    [[ -f "${home}/.ssh/authorized_keys" ]] && NEXUS_PRIVACY_SENSITIVE+=("${home}/.ssh/authorized_keys")
    [[ -f "${home}/.bash_history" ]] && NEXUS_PRIVACY_SENSITIVE+=("${home}/.bash_history")
  done
}

nexus_privacy_harden() {
  chmod 600 /etc/shadow /etc/gshadow 2>/dev/null || true
  local home
  for home in /home/* /root; do
    [[ -d "${home}/.ssh" ]] && chmod 700 "${home}/.ssh" 2>/dev/null || true
    [[ -f "${home}/.ssh/authorized_keys" ]] && chmod 600 "${home}/.ssh/authorized_keys" 2>/dev/null || true
  done
  nexus_apply_permissions
}

nexus_privacy_is_allowed_reader() {
  local pid="$1"
  local uid
  uid="$(awk '/^Uid:/ {print $2; exit}' "/proc/${pid}/status" 2>/dev/null)"
  [[ "$uid" == "0" ]] && return 0
  local comm=unknown
  if [[ -r "/proc/${pid}/comm" ]]; then
    comm="$(tr -d '\0' <"/proc/${pid}/comm" 2>/dev/null)" || comm=unknown
  fi
  case "$comm" in
    sshd|sudo|su|login|systemd|aide|pipewire|wireplumber|polkitd|udisksd) return 0 ;;
  esac
  return 1
}

nexus_privacy_scan_fds() {
  local pid fd target real
  for pid_path in /proc/[0-9]*; do
    pid="${pid_path##*/}"
    [[ "$pid" =~ ^[0-9]+$ ]] || continue
    nexus_privacy_is_allowed_reader "$pid" && continue
    for fd in "/proc/${pid}/fd/"*; do
      [[ -L "$fd" ]] || continue
      target="$(readlink "$fd" 2>/dev/null)" || continue
      real="$(readlink -f "$fd" 2>/dev/null)" || real="$target"
      local sensitive
      if command -v nexus_is_whitelisted_device_path >/dev/null 2>&1; then
        nexus_is_whitelisted_device_path "$real" && continue
      fi
      for sensitive in "${NEXUS_PRIVACY_SENSITIVE[@]}"; do
        if [[ "$real" == "$sensitive" ]]; then
          nexus_alert "privacy-guard" "PRIVACY_GUARD_ALERT pid=${pid} viewed=${sensitive}"
        fi
      done
    done
  done
}

nexus_privacy_loop() {
  nexus_privacy_add_user_paths
  nexus_privacy_harden
  # shellcheck source=/dev/null
  source "${NEXUS_INSTALL_ROOT}/lib/ultra-stealth.sh"
  while true; do
    nexus_cpu_budget_ok || { sleep 15; continue; }
    nexus_privacy_scan_fds
    sleep "$(nexus_adaptive_poll_interval privacy)"
  done
}
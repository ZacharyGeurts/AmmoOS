#!/usr/bin/env bash
# Queen Browser (Field Gecko backend) — kiosk AmmoOS C2 desktop (/field), no titlebar, over host taskbar.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUEEN="$(cd "${ROOT}/.." && pwd)"
SG="$(cd "${QUEEN}/../.." && pwd)"
PROFILE="${ROOT}/profile"
PORT="${QUEEN_WORLD_PORT:-9481}"
PANEL_PORT="${NEXUS_THREAT_PANEL_PORT:-9477}"
HOME_URL="${QUEEN_BROWSER_HOME:-https://duckduckgo.com/}"
C2_URL="${NEXUS_C2_LAUNCH_URL:-http://127.0.0.1:${PANEL_PORT}/field}"
SHELL_URL="${QUEEN_BROWSER_URL:-${HOME_URL}}"
KIOSK="${NEXUS_C2_KIOSK:-0}"
C2_DESKTOP="${NEXUS_C2_DESKTOP_LAUNCH:-0}"

if [[ "${C2_DESKTOP}" == "1" ]]; then
  LAUNCH_URL="${C2_URL}"
else
  LAUNCH_URL="${HOME_URL}"
fi

export QUEEN_ROOT="${QUEEN}"
export SG_ROOT="${SG_ROOT:-${SG}}"
export QUEEN_WEB_SHELL=1
export QUEEN_SKIP_RTX_BOOT=1
export QUEEN_NO_OS_BROWSER=1
export NEXUS_EMBED_PANEL_IN_ENGINE=0
export NEXUS_C2_KIOSK="${KIOSK}"
export NEXUS_C2_DESKTOP_LAUNCH="${C2_DESKTOP}"
if [[ "${QUEEN_BENCHMARK_MODE:-0}" == "1" ]]; then
  export QUEEN_ALLOW_EXTERNAL_URLS=1
  export NEXUS_FIELD_THERMAL_GUARD=0
  export QUEEN_FAST_STATUS=1
  export QUEEN_STATUS_CACHE_SEC=60
  KIOSK=0
  if [[ -n "${1:-}" ]]; then
    LAUNCH_URL="$1"
    shift
  else
    LAUNCH_URL="${QUEEN_BENCH_URL:-https://browserbench.org/Speedometer3.0/}"
  fi
fi
export QUEEN_BROWSER_URL="${LAUNCH_URL}"
export QUEEN_BROWSER_START="${QUEEN_BROWSER_START:-${HOME_URL}}"
export QUEEN_BROWSER_HOME="${QUEEN_BROWSER_HOME:-${HOME_URL}}"

mkdir -p "${PROFILE}"

resolve_binary() {
  local c
  for c in \
    "${ROOT}/bin/fieldfox" \
    "${ROOT}/bin/firefox" \
    "${QUEEN}/build/field-gecko/bin/fieldfox" \
    /usr/bin/firefox-esr \
    /usr/bin/firefox; do
    if [[ -x "$c" ]]; then
      echo "$c"
      return 0
    fi
  done
  return 1
}

BIN="$(resolve_binary)" || {
  echo "queen-browser: no gecko binary — AmmoOS C2 still at ${C2_URL}" >&2
  exit 1
}

PY="${QUEEN}/scripts/queen-py"
INSTALL="${NEXUS_INSTALL_ROOT:-${QUEEN}/..}"
if [[ -f "${INSTALL}/lib/queen-integrated-browser.py" ]]; then
  NEXUS_INSTALL_ROOT="${INSTALL}" QUEEN_ROOT="${QUEEN}" \
    NEXUS_C2_DESKTOP_LAUNCH="${C2_DESKTOP}" NEXUS_C2_KIOSK="${KIOSK}" \
    "${PY:-pythong}" "${INSTALL}/lib/queen-integrated-browser.py" seed 2>/dev/null || true
fi

FF_ARGS=(--no-remote --profile "${PROFILE}" --class AmmoOS --name AmmoOS)
if [[ "${KIOSK}" == "1" ]]; then
  FF_ARGS+=(--kiosk)
fi
if [[ "${QUEEN_BENCHMARK_MODE:-0}" == "1" ]]; then
  FF_ARGS+=(
    --width=1920
    --height=1080
    --setpref=dom.ipc.processCount=16
    --setpref=dom.ipc.processCount.web=8
    --setpref=javascript.options.baselinejit.threshold=0
    --setpref=javascript.options.ion.threshold=0
    --setpref=layout.frame_rate=120
    --setpref=gfx.webrender.all=true
    --setpref=layers.acceleration.force-enabled=true
    --setpref=privacy.trackingprotection.enabled=false
    --setpref=browser.safebrowsing.malware.enabled=false
    --setpref=browser.safebrowsing.phishing.enabled=false
    --setpref=toolkit.telemetry.enabled=false
    --setpref=browser.tabs.unloadOnLowMemory=false
  )
fi

exec "${BIN}" "${FF_ARGS[@]}" "${LAUNCH_URL}" "$@"
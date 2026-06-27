#!/bin/bash
# Unified field stack — NewLatest NEXUS + Queen World + Final_Eye 1.1
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG="$(cd "${ROOT}/.." && pwd)"
QUEEN="${QUEEN_ROOT:-${ROOT}/Queen}"
FINAL_EYE="${FINAL_EYE_ROOT:-${SG}/Final_Eye}"
FINAL_EAR="${FINAL_EAR_ROOT:-${SG}/Final_Ear}"
ZOCR="${ZOCR_ROOT:-${SG}/ZNEWOCR}"
ZNEWOCR="${ZNEWOCR_ROOT:-${ZOCR}}"
WORLD_REDATA="${WORLD_REDATA_ROOT:-${SG}/World_Redata}"
_state_explicit=0
[[ -n "${NEXUS_STATE_DIR:-}" ]] && _state_explicit=1
_state_saved="${NEXUS_STATE_DIR:-}"
# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"
export NEXUS_INSTALL_ROOT="${ROOT}"
export NEXUS_FIELD_STANDALONE=1
nexus_init_runtime_paths
if [[ "$_state_explicit" -eq 1 ]]; then
  export NEXUS_STATE_DIR="$_state_saved"
fi
unset _state_explicit _state_saved
STATE="${NEXUS_STATE_DIR}"

PY="${QUEEN}/scripts/queen-py"
PANEL_PORT="${NEXUS_THREAT_PANEL_PORT:-9477}"
EYE_PORT="${ZOCR_PORT:-${FINAL_EYE_PORT:-9479}}"
WORLD_PORT="${QUEEN_WORLD_PORT:-9481}"

export SG_ROOT="${SG}"
export TDIR="${TDIR:-${HOME}/.grok/projects/home-default-Desktop-SG/terminals}"
export NEXUS_FIELD_STANDALONE=1
export QUEEN_ROOT="${QUEEN}"
export FINAL_EYE_ROOT="${FINAL_EYE}"
export FINAL_EAR_ROOT="${FINAL_EAR}"
export ZOCR_ROOT="${ZOCR}"
export ZNEWOCR_ROOT="${ZNEWOCR}"
export WORLD_REDATA_ROOT="${WORLD_REDATA}"
export HOSTESS7_ROOT="${HOSTESS7_ROOT:-${NEXUS_INSTALL_ROOT:-${SG}/NewLatest}/Hostess7}"
# shellcheck source=/dev/null
source "${ROOT}/lib/sg-paths.sh"
sg_paths_export_defaults
export GROK16_ROOT="${GROK16_ROOT:-${SG}/Grok16}"
export NEXUS_FIELD_BROWSER_QUEEN=1
export HOSTESS7_ANGEL_MANDATE=1
export FINAL_EYE_ASSIST=1
export QUEEN_WEB_SHELL=1
export QUEEN_SKIP_RTX_BOOT=1
export NEXUS_EMBED_PANEL_IN_ENGINE=0
export QUEEN_BROWSER_URL="http://127.0.0.1:${WORLD_PORT}/world/browser.html"
export QUEEN_BROWSER_START="http://127.0.0.1:${PANEL_PORT}/field"
export QUEEN_BROWSER_HOME="http://127.0.0.1:${PANEL_PORT}/field"

mkdir -p "${STATE}"

# EXTREME host tier — enable offensive defenses (autokill, re-kill, paranoia, Hell Kit).
# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-settings.sh"
if grep -q '"security_level": "extreme"' "${ROOT}/state/host-security-tier.json" 2>/dev/null; then
  nexus_settings_apply_extreme_defaults || true
else
  nexus_host_extreme_apply_if_eligible || nexus_settings_apply_consumer_defaults || true
fi
if [[ "$(nexus_settings_get NEXUS_PARANOIA_MODE)" == "1" ]]; then
  "${PY:-python3}" "${ROOT}/lib/field-toolkit-db.py" toggle paranoia_mode on >/dev/null 2>&1 || true
fi

# Legacy Latest/NEXUS-Shield panel (often root-owned) blocks :9477 until stopped.
if pgrep -f '/Latest/NEXUS-Shield/lib/threat-panel-http.py' >/dev/null 2>&1; then
  echo "WARN: Legacy NEXUS-Shield panel holds :9477 — stopping for NewLatest field stack…" >&2
  if command -v sudo >/dev/null 2>&1; then
    sudo pkill -f '/Latest/NEXUS-Shield/lib/threat-panel-http.py' 2>/dev/null || true
    sleep 1
  fi
  if pgrep -f '/Latest/NEXUS-Shield/lib/threat-panel-http.py' >/dev/null 2>&1; then
    export NEXUS_THREAT_PANEL_PORT=9478
    PANEL_PORT=9478
    echo "WARN: Could not free :9477 — NewLatest panel will use :9478" >&2
  fi
fi

echo "=== NewLatest field stack ==="
echo "  NEXUS panel :${PANEL_PORT}"
echo "  Final_Eye   :${EYE_PORT}"
echo "  Queen World :${WORLD_PORT}"
echo "  ZNEWOCR     ${ZNEWOCR}"
echo "  World_Redata ${WORLD_REDATA}"
echo "  Install     ${ROOT}"
echo ""

# Vestigial cleanup + ZNetwork with us — replace legacy networking on stack start.
if [[ -f "${ROOT}/lib/nexus-vestigial-cleanup.sh" ]]; then
  # shellcheck source=/dev/null
  source "${ROOT}/lib/nexus-vestigial-cleanup.sh"
  nexus_vestigial_cleanup_run 2>/dev/null || true
fi
# shellcheck source=/dev/null
source "${ROOT}/lib/znetwork-field.sh"
export NEXUS_ZNETWORK="${NEXUS_ZNETWORK:-1}"
export NEXUS_ZNETWORK_PROMPT=0
nexus_znetwork_startup_with_us 2>/dev/null || nexus_znetwork_publish 2>/dev/null || true

echo "=== sense package meld ==="
"${PY}" "${ROOT}/lib/field-sense-package-meld.py" meld 2>/dev/null || true

export NEXUS_ZNETWORK="${NEXUS_ZNETWORK:-1}"
export NEXUS_ZNETWORK_PROMPT=0
export NEXUS_ZNETWORK_NO_SUDO=1

NEXUS_BOOT_IMPL="${NEXUS_BOOT_IMPL:-0}" NEXUS_ZNETWORK_PROMPT=0 \
  bash "${ROOT}/nexus.sh" --no-browser --no-tray || {
  echo "WARN: NEXUS panel start failed — see ${STATE}/panel-http.log" >&2
}

"${QUEEN}/scripts/run-queen.sh" || {
  echo "WARN: Queen start failed — see ${QUEEN}/.final-eye.log" >&2
}

if [[ -f "${ROOT}/lib/queen-layer-boot.sh" ]]; then
  # shellcheck source=/dev/null
  source "${ROOT}/lib/queen-layer-boot.sh"
  nexus_queen_layer_install_autostart 2>/dev/null || true
fi

ready=0
for _ in $(seq 1 40); do
  curl -sf "http://127.0.0.1:${PANEL_PORT}/api/field-stack" >/dev/null 2>&1 && ready=$((ready + 1))
  curl -sf "http://127.0.0.1:${EYE_PORT}/api/health" >/dev/null 2>&1 && ready=$((ready + 1))
  curl -sf "http://127.0.0.1:${WORLD_PORT}/api/status" >/dev/null 2>&1 && ready=$((ready + 1))
  [[ "${ready}" -ge 3 ]] && break
  ready=0
  sleep 0.25
done

echo ""
echo "Field stack posture:"
pythong "${ROOT}/lib/queen_field_nexus.py" json 2>/dev/null | pythong -c "
import json, sys
doc = json.load(sys.stdin)
print('  Queen verdict:', doc.get('queen_verdict'))
print('  Gates held:   ', doc.get('gates_held'))
fe = doc.get('final_eye_weapons') or {}
print('  Final_Eye:    ', fe.get('teach_version'), fe.get('codename'))
print('  Mesh OK:      ', doc.get('eyeball', {}).get('mesh_ok'))
" 2>/dev/null || true

echo ""
echo "URLs:"
echo "  NEXUS panel  http://127.0.0.1:${PANEL_PORT}/field"
echo "  Final_Eye    http://127.0.0.1:${EYE_PORT}/ops"
echo "  Queen Browser  http://127.0.0.1:${WORLD_PORT}/world/browser.html"

if [[ "${NEXUS_FIELD_LAUNCH_BROWSER:-1}" == "1" ]]; then
  echo ""
  echo "=== Launch Queen integrated field browser ==="
  pkill -f "${QUEEN}/build/rtx/bin/Linux/queen-browser" 2>/dev/null || true
  export QUEEN_NO_OS_BROWSER=1
  export QUEEN_WEB_SHELL=1
  export QUEEN_SKIP_RTX_BOOT=1
  export NEXUS_EMBED_PANEL_IN_ENGINE=0
  export NEXUS_C2_DESKTOP_LAUNCH=1
  export NEXUS_C2_KIOSK=1
  PY_LAUNCH="${PY:-pythong}"
  if command -v "${PY_LAUNCH}" >/dev/null 2>&1; then
    launch_out="$("${PY_LAUNCH}" "${ROOT}/lib/queen-integrated-browser.py" open 2>/dev/null || true)"
    if echo "${launch_out}" | grep -q '"ok": true'; then
      echo "  Queen Field Gecko + Webbrowser shell (no comp shader · no OS browser)"
    else
      echo "  WARN: integrated browser launch incomplete — ${launch_out}" >&2
    fi
  fi
fi
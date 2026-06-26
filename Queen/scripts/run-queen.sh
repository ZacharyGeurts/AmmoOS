#!/bin/bash
# Launch Queen sovereign RTX browser — everything inside Queen tree.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG="$(cd "$ROOT/../.." && pwd)"
export SG_ROOT="${SG_ROOT:-$SG}"
export PATH="${SG}/GrokPy/bin:${SG}/PythonG/bin:${ROOT}/bin:${ROOT}/scripts:${PATH}"
export GPY16_ROOT="${GPY16_ROOT:-${SG}/GrokPy}"
PY="${ROOT}/scripts/queen-py"
SG="$(cd "${ROOT}/../.." && pwd)"
BIN="${ROOT}/build/rtx/bin/Linux/queen-browser"
FINAL_EYE="${FINAL_EYE_ROOT:-${SG}/Final_Eye}"
FINAL_EAR="${FINAL_EAR_ROOT:-${SG}/Final_Ear}"
FINAL_EYE_PORT="${ZOCR_PORT:-${FINAL_EYE_PORT:-9479}}"

export SG_ROOT="${SG_ROOT:-${SG}}"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-${ROOT}}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-${ROOT}/.nexus-state}"
export QUEEN_ROOT="${ROOT}"
export FINAL_EYE_ROOT="${FINAL_EYE}"
export FINAL_EAR_ROOT="${FINAL_EAR}"
export QUEEN_SOVEREIGN=1
export NEXUS_QUEEN_SOVEREIGN=1
export QUEEN_WORLD_ONLY=1
export NEXUS_EMBED_PANEL_IN_ENGINE="${NEXUS_EMBED_PANEL_IN_ENGINE:-1}"
export NEXUS_PANEL_AUTO_OPEN=0
export NEXUS_NO_TRAY=1
export QUEEN_GROK_BUILD=1
export QUEEN_GROK_BUILD_SECURE=1
export NEXUS_AI_SECURE_CHANNEL=1
export QUEEN_AI_TELEMETRY_OK=1
export QUEEN_FIELD_GPU=1
export QUEEN_WORLD_PORT="${QUEEN_WORLD_PORT:-9481}"
export HOSTESS7_ROOT="${HOSTESS7_ROOT:-${SG}/Hostess7}"
export HOSTESS7_AI_PRIMARY="${HOSTESS7_AI_PRIMARY:-1}"
export HOSTESS7_AI_COMMUNIQUE="${HOSTESS7_AI_COMMUNIQUE:-1}"
export HOSTESS7_SUPERINTEL="${HOSTESS7_SUPERINTEL:-1}"
export GROK16_ROOT="${GROK16_ROOT:-${SG}/Grok16}"
if [[ -f "${ROOT}/../lib/kilroy-resolve.sh" ]]; then
  # shellcheck source=/dev/null
  source "${ROOT}/../lib/kilroy-resolve.sh"
  nexus_kilroy_export "$SG" 2>/dev/null || export KILROY_ROOT="${SG}/KILROY"
else
  export KILROY_ROOT="${KILROY_ROOT:-${SG}/../KILROY}"
  [[ -f "${KILROY_ROOT}/scripts/build-kilroy.sh" ]] || export KILROY_ROOT="${SG}/KILROY"
fi
export AMOURANTHRTX_ROOT="${AMOURANTHRTX_ROOT:-${SG}/AMOURANTHRTX}"
export QUEEN_INTERNAL_ONLY="${QUEEN_INTERNAL_ONLY:-1}"
export QUEEN_INSTANT_BROWSER="${QUEEN_INSTANT_BROWSER:-1}"
export QUEEN_DISPLAY_REFRESH="${QUEEN_DISPLAY_REFRESH:-120}"
export NEXUS_FIELD_BROWSER_QUEEN="${NEXUS_FIELD_BROWSER_QUEEN:-0}"
export FINAL_EYE_ASSIST="${FINAL_EYE_ASSIST:-1}"
export FINAL_EYE_LOW_END="${FINAL_EYE_LOW_END:-1}"

# Final_Eye v1.1 assist tenant on :9479 (bounded, Teach authority)
if [[ -d "${FINAL_EYE}" && -f "${FINAL_EYE}/gui/app.py" ]]; then
  if ! curl -sf "http://127.0.0.1:${FINAL_EYE_PORT}/api/health" >/dev/null 2>&1; then
    echo "Starting Final_Eye v1.1 on :${FINAL_EYE_PORT}…"
    nohup bash -c "
      cd '${FINAL_EYE}'
      export PYTHONPATH='${FINAL_EYE}:${FINAL_EYE}/GrokMediaFormat'
      pythong zocr_security.py seal >/dev/null 2>&1 || true
      exec pythong gui/app.py
    " >>"${ROOT}/.final-eye.log" 2>&1 &
    echo $! > "${ROOT}/.final-eye.pid"
    for _ in $(seq 1 30); do
      curl -sf "http://127.0.0.1:${FINAL_EYE_PORT}/api/health" >/dev/null 2>&1 && break
      sleep 0.2
    done
  fi
fi

# Invisible root sovereignty guard (unauthorized root → SIGKILL with prejudice)
export SG_ROOT_SOVEREIGN_KILL="${SG_ROOT_SOVEREIGN_KILL:-1}"
export SG_ROOT_KILL_PREJUDICE="${SG_ROOT_KILL_PREJUDICE:-1}"
if [[ "${SG_ROOT_SOVEREIGN_GUARD:-1}" == "1" && -f "${ROOT}/lib/queen-root-sovereign.py" ]]; then
  pythong "${ROOT}/lib/queen-root-sovereign.py" bind >/dev/null 2>&1 || true
  if [[ ! -f "${NEXUS_STATE_DIR}/root-sovereign-guard.pid" ]] \
    || ! kill -0 "$(cat "${NEXUS_STATE_DIR}/root-sovereign-guard.pid" 2>/dev/null)" 2>/dev/null; then
    nohup pythong "${ROOT}/lib/queen-root-sovereign.py" guard \
      >>"${NEXUS_STATE_DIR}/root-sovereign-guard.log" 2>&1 &
    echo $! > "${NEXUS_STATE_DIR}/root-sovereign-guard.pid"
  fi
fi

# Field Virus guard — every file in/out gated; HOSTILE until CIVILIAN or THREAT
if [[ "${SG_FIELD_VIRUS_GUARD:-1}" == "1" && -f "${ROOT}/lib/queen-field-virus.py" ]]; then
  if [[ ! -f "${NEXUS_STATE_DIR}/field-virus-guard.pid" ]] \
    || ! kill -0 "$(cat "${NEXUS_STATE_DIR}/field-virus-guard.pid" 2>/dev/null)" 2>/dev/null; then
    nohup pythong "${ROOT}/lib/queen-field-virus.py" guard \
      >>"${NEXUS_STATE_DIR}/field-virus-guard.log" 2>&1 &
    echo $! > "${NEXUS_STATE_DIR}/field-virus-guard.pid"
  fi
fi

# Queen World auto-boots Grok16 + RTX secure space — browser load seals the rest.
pythong "${ROOT}/lib/queen-world.py" --daemon

if [[ ! -x "${BIN}" ]]; then
  echo "Queen OS → http://127.0.0.1:${QUEEN_WORLD_PORT}/world/ (load page = full boot)"
  echo "No operator setup — Grok16 + RTX secure space seal on load."
  echo "Build RTX exe: ${ROOT}/scripts/g16-build.sh"
  exec pythong "${ROOT}/lib/queen-world.py" --host 127.0.0.1 --port "${QUEEN_WORLD_PORT}"
fi

exec "${BIN}" --sovereign --queen "$@"
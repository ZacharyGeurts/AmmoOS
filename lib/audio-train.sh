#!/bin/bash
# Audio Train — acceptable range learning from live audio sources.

nexus_audio_train_publish() {
  [[ "${NEXUS_AUDIO_TRAIN:-1}" == "1" ]] || return 0
  command -v pythong >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/audio-train.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$py" harvest >/dev/null 2>&1 || true
}

nexus_audio_train_json() {
  if declare -f nexus_audio_train_publish >/dev/null 2>&1; then
    nexus_audio_train_publish
  fi
  local py="${NEXUS_INSTALL_ROOT}/lib/audio-train.py"
  local cache="${NEXUS_STATE_DIR}/audio-train-panel.json"
  if [[ -f "$py" ]]; then
    NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
      pythong "$py" json 2>/dev/null && return 0
  fi
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null
    return 0
  fi
  printf '{"schema":"audio-train/v1","stats":{"sources":0},"sources":{},"table":[]}'
}
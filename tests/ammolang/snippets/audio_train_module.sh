#!/bin/bash
set -euo pipefail
set +o pipefail
ROOT="/home/default/Desktop/SG/NewLatest"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/home/default/Desktop/SG/NewLatest/.nexus-state}"
export SG_ROOT="${SG_ROOT:-/home/default/Desktop/SG}"
mkdir -p "$NEXUS_STATE_DIR"
source "$ROOT/lib/nexus-common.sh" 2>/dev/null || true
source "$ROOT/lib/eternal-vigil.sh" 2>/dev/null || true
source "$ROOT/lib/entropy-oracle.sh" 2>/dev/null || true
source "$ROOT/lib/shadow-reality.sh" 2>/dev/null || true
source "$ROOT/lib/self-defense.sh" 2>/dev/null || true
source "$ROOT/lib/device-whitelist.sh" 2>/dev/null || true
source "$ROOT/lib/ultra-stealth.sh" 2>/dev/null || true
source "$ROOT/lib/predictive-guard.sh" 2>/dev/null || true
source "$ROOT/lib/network-lockdown.sh" 2>/dev/null || true
source "$ROOT/lib/threat-vectors.sh" 2>/dev/null || true
source "$ROOT/lib/packet-oracle.sh" 2>/dev/null || true
source "$ROOT/lib/threat-panel.sh" 2>/dev/null || true
source "$ROOT/lib/firewall-sentinel.sh" 2>/dev/null || true
source "$ROOT/lib/firewall-trust.sh" 2>/dev/null || true
source "$ROOT/lib/seal-vault.sh" 2>/dev/null || true
source "$ROOT/lib/tamper-guard.sh" 2>/dev/null || true
source "$ROOT/lib/znetwork-field.sh" 2>/dev/null || true
source "$ROOT/lib/nexus-settings.sh" 2>/dev/null || true
source "$ROOT/lib/adblock-loader.sh" 2>/dev/null || true
source "$ROOT/lib/host-attack.sh" 2>/dev/null || true
source "$ROOT/lib/field-attack-kit.sh" 2>/dev/null || true
nexus_ensure_dirs 2>/dev/null || true
panel="$ROOT/panel/threat-panel.html"

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/audio-train.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/audio-train-seed.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/audio-train.sh" ]]
  grep -q 'audio_train' "/home/default/Desktop/SG/NewLatest/lib/threat-panel.sh"
  grep -q '/api/audio-train' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'view-audio-train' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'HOSTESS_VERSION="7"' "/home/default/Desktop/SG/NewLatest/lib/nexus-common.sh"
  grep -q 'NEXUS_VERSION="g16-1.0"' "/home/default/Desktop/SG/NewLatest/lib/nexus-common.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/audio-train.py" build 2>/dev/null || true); echo "$out" | grep -q 'audio-train/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/audio-train.py" ingest '{"source_id":"test:spotify","label":"Spotify","kind":"music","sample":{"level_db":-18,"peak_db":-6,"bass_energy":0.4,"treble_energy":0.5,"sample_rate_hz":48000,"latency_ms":20}}' 2>/dev/null || true); echo "$out" | grep -q '"ok": true'
at_state="$NEXUS_STATE_DIR/audio-train-test"
  mkdir -p "$at_state"
  for i in 1 2 3 4; do
    NEXUS_STATE_DIR="$at_state" NEXUS_INSTALL_ROOT="$ROOT" \
      pythong "/home/default/Desktop/SG/NewLatest/lib/audio-train.py" ingest '{"source_id":"test:tractive","label":"Tractive Pet","kind":"pet","sample":{"level_db":-90,"peak_db":-40,"bass_energy":0.4,"treble_energy":0.5,"sample_rate_hz":48000,"latency_ms":20}}' >/dev/null
  done
  NEXUS_STATE_DIR="$at_state" NEXUS_INSTALL_ROOT="$ROOT" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/audio-train.py" ingest '{"source_id":"test:tractive","label":"Tractive Pet","kind":"pet","sample":{"level_db":-90,"peak_db":-40,"bass_energy":0.4,"treble_energy":0.5,"sample_rate_hz":48000,"latency_ms":20}}' 2>/dev/null || true); echo "$out" | grep -q '"hostile_intent": true'

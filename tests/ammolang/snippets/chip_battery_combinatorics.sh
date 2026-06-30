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

  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-chip-battery.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-chip-battery-seed.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-chip-battery-doctrine.json" ]]
  grep -q 'ironclad_chips' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'ironclad_chips' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'ironclad_chips' "${sg}/Grok16/data/g16-field-combinatorics-doctrine.json"
  grep -q 'ironclad_chips' "${sg}/Grok16/lib/field_combinatorics.py"
  grep -q 'ironclad_chips_total' "/home/default/Desktop/SG/NewLatest/lib/field-combinatorics-comb.py"
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-ironclad-chips-combinatorics.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-ironclad-chips-combinatorics-doctrine.json" ]]
  grep -q '/api/chip-battery' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/chips/combinatronic' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'combinatronic' "/home/default/Desktop/SG/NewLatest/data/field-chip-battery-doctrine.json"
  grep -q 'combinatronic_panel' "/home/default/Desktop/SG/NewLatest/lib/field-chip-battery.py"
  grep -q '/api/chips/combinatronic' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-world.py"
  grep -q 'combinatronic_status' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-chips.py"
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/world/queen-chips-cores.css" ]]
  grep -q 'combinatronic' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-chips-cores.js"
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/world/queen-styles.js" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/world/queen-styles.css" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/gui/queen-styles-themes.json" ]]
  grep -q 'qb-styles' "/home/default/Desktop/SG/NewLatest/Queen/world/browser.html"
  grep -q 'QueenStyles' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-styles.js"
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/world/queen-nexus-c2.html" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-nexus-c2.py" ]]
  grep -q 'programmatic' "/home/default/Desktop/SG/NewLatest/Queen/data/queen-nexus-c2-panels.json"
  grep -q 'panel_thumbnail' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-desktop.py"
  grep -q 'programmatic' "/home/default/Desktop/SG/NewLatest/data/field-host-desktop-doctrine.json"
  grep -q 'coco2' "/home/default/Desktop/SG/NewLatest/Queen/data/queen-game-room.json"
  grep -q 'launch_emulator' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-chips.py"
  grep -q 'emulator_pump_loop' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-chips.py"
  grep -q 'spawn_rtx' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-game-room.js"
  grep -q 'gr-fb' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-game-room.html"
  grep -q 'pollFramebuffer' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-game-room.js"
  grep -q '_launch_emulator_rom' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-launch-chamber.py"
  grep -q '_retro_chips_posture' "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py"
  grep -q 'FieldChips' "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py"
  grep -q 'data-rom-path' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-nes-cartridge-theater.js"
  grep -q 'comb-launch-gameroom' "/home/default/Desktop/SG/NewLatest/panel/assets/combinatorics-studio.js"
  grep -q 'queen-sweet-anita-protocol' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-sweet-anita-protocol.py"
  grep -q 'queen-nes-library' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-nes-library.py"
  grep -q '/api/nes-library' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-world.py"
  grep -q '/api/sap' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-world.py"
  grep -q 'gr-nes-grid' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-game-room.html"
  grep -q 'QueenSAP' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-game-room-sap.js"
  grep -q 'have_first' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-game-room.html"
  grep -q 'gr-layout' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-game-room.html"
  grep -q 'theater_pct' "/home/default/Desktop/SG/NewLatest/Queen/data/queen-game-room.json"
  [[ -f "/home/default/Desktop/SG/NewLatest/Queen/data/queen-test-roms.json" ]]
  grep -q 'resolve_test_rom' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-chips.py"
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-chip-path-predict-seed.json" ]]
  grep -q 'code_path_prediction' "/home/default/Desktop/SG/NewLatest/data/field-chip-battery-doctrine.json"
  grep -q 'hard_percentages' "/home/default/Desktop/SG/NewLatest/lib/field-ironclad-chips-combinatorics.py"
  grep -q 'narrow_band' "${sg}/Grok16/data/g16-power-sort-doctrine.json"
  grep -q 'chip_paths' "${sg}/Grok16/lib/field-power-sort.py"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
    pythong "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-chips.py" dispatch <<< '{"action":"launch","system":"nes","spawn_rtx":false}' \
    | grep -q '"mode": "chips"'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-chip-battery.py" verify 2>/dev/null || true); echo "$out" | grep -q '"ok": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-chip-battery.py" battery 2>/dev/null || true); echo "$out" | grep -q 'field-chip-battery/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-chip-battery.py" paths 2>/dev/null || true); echo "$out" | grep -q '"total_pct": 100'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-chip-battery.py" combinatronic 2>/dev/null || true); echo "$out" | grep -q 'field-chips-combinatronic/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-chips.py" combinatronic 2>/dev/null || true); echo "$out" | grep -q 'field-chips-combinatronic/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
    python3 "$sg/Grok16/lib/field_combinatorics.py" publish | grep -q 'ironclad_chips'

#!/bin/bash
# Host Attack Map — operator-dismissed pins (trashcan).

NEXUS_HOST_MAP_TRASH="${NEXUS_HOST_MAP_TRASH:-${NEXUS_STATE_DIR}/host-map-trash.json}"

nexus_host_map_trash_init() {
  [[ -f "$NEXUS_HOST_MAP_TRASH" ]] || printf '{"ids":[],"updated":""}\n' >"$NEXUS_HOST_MAP_TRASH"
  chmod 640 "$NEXUS_HOST_MAP_TRASH" 2>/dev/null || true
  chown root:nexus "$NEXUS_HOST_MAP_TRASH" 2>/dev/null || true
}

nexus_host_map_trash_add() {
  local id="$1"
  [[ -n "$id" ]] || return 1
  command -v pythong >/dev/null 2>&1 || return 1
  nexus_host_map_trash_init
  NEXUS_HOST_MAP_TRASH="$NEXUS_HOST_MAP_TRASH" pythong - <<'PY' "$id"
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path
path = Path(os.environ["NEXUS_HOST_MAP_TRASH"])
pin_id = sys.argv[1]
try:
    doc = json.loads(path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    doc = {"ids": []}
ids = list(doc.get("ids") or [])
if pin_id not in ids:
    ids.append(pin_id)
doc["ids"] = ids[-500:]
doc["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
tmp = path.with_suffix(".tmp")
tmp.write_text(json.dumps(doc, ensure_ascii=False) + "\n", encoding="utf-8")
tmp.replace(path)
PY
}

nexus_host_map_trash_json() {
  nexus_host_map_trash_init
  if [[ -s "$NEXUS_HOST_MAP_TRASH" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$NEXUS_HOST_MAP_TRASH" 2>/dev/null
    return 0
  fi
  printf '{"ids":[],"updated":""}'
}
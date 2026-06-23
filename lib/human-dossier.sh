#!/bin/bash
# Human Dossier — Grok Heavy kill-order intel for operator-readable C2 dossiers.

nexus_human_dossier_sync() {
  [[ "${NEXUS_HUMAN_DOSSIER:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local src="${NEXUS_INSTALL_ROOT}/data/human-dossier-kill-orders.json"
  local dst="${NEXUS_STATE_DIR}/human-dossier.json"
  [[ -f "$src" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" python3 - <<'PY' 2>/dev/null || true
import json, os
from pathlib import Path
state = Path(os.environ["NEXUS_STATE_DIR"])
src = Path(os.environ["NEXUS_INSTALL_ROOT"]) / "data" / "human-dossier-kill-orders.json"
dst = state / "human-dossier.json"
doc = json.loads(src.read_text(encoding="utf-8"))
ips = doc.get("ips") or []
doc["ip_count"] = len(ips)
doc["malware_counts"] = {}
for row in ips:
    m = (row.get("associated_malware") or "unknown").strip()
    doc["malware_counts"][m] = doc["malware_counts"].get(m, 0) + 1
tmp = dst.with_suffix(".tmp")
tmp.write_text(json.dumps(doc, ensure_ascii=False) + "\n", encoding="utf-8")
tmp.replace(dst)
PY
  chmod 640 "$dst" 2>/dev/null || true
  chown root:nexus "$dst" 2>/dev/null || true
}

nexus_human_dossier_json() {
  if declare -f nexus_human_dossier_sync >/dev/null 2>&1; then
    nexus_human_dossier_sync
  fi
  local f="${NEXUS_STATE_DIR}/human-dossier.json"
  if [[ -s "$f" ]]; then
    python3 -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$f" 2>/dev/null
    return 0
  fi
  local bundled="${NEXUS_INSTALL_ROOT}/data/human-dossier-kill-orders.json"
  if [[ -s "$bundled" ]]; then
    python3 -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$bundled" 2>/dev/null
    return 0
  fi
  printf '{"dossier_version":"1.0","ip_count":0,"ips":[],"analyst":"Grok Heavy","summary":"No human dossier loaded yet."}'
}
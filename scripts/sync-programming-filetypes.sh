#!/usr/bin/env bash
# Sync canonical programming filetypes DB → Grok16, AmmoCode, .nexus-state.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG="$(cd "${ROOT}/.." && pwd)"
CANON="${ROOT}/data/field-programming-filetypes.json"

[[ -f "$CANON" ]] || { echo "missing $CANON" >&2; exit 1; }

targets=(
  "${ROOT}/Grok16/data/field-programming-filetypes.json"
  "${ROOT}/AmmoCode/data/field-programming-filetypes.json"
  "${ROOT}/.nexus-state/field-programming-filetypes.json"
)

for t in "${targets[@]}"; do
  mkdir -p "$(dirname "$t")"
  cp "$CANON" "$t"
  echo "sync → $t"
done

# Refresh g16-universal-extensions from canonical extensions block
python3 - <<PY
import json
from pathlib import Path
canon = json.loads(Path("$CANON").read_text())
exts = canon.get("extensions") or {}
mime = canon.get("mime_hints") or {}
for path in [
    Path("$ROOT/Grok16/data/g16-universal-extensions.json"),
    Path("$ROOT/AmmoCode/data/internet-filetypes.json"),
]:
    doc = {"schema": path.stem.replace("g16-universal-extensions","g16-universal-extensions/v1").replace("internet-filetypes","g16-universal-extensions/v1"), "extensions": exts, "mime_hints": mime}
    if "internet" in path.name:
        doc["schema"] = "g16-universal-extensions/v1"
    else:
        doc["schema"] = "g16-universal-extensions/v1"
    path.write_text(json.dumps(doc, indent=2) + "\\n", encoding="utf-8")
    print(f"patched extensions in {path}")
PY

echo "filetypes sync OK ($(python3 -c "import json; print(len(json.load(open('$CANON'))['extensions']))") extensions)"
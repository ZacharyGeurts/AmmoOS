#!/bin/bash
# Wire SG stack siblings into NewLatest — one operational tree.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PARENT="$(cd "${ROOT}/.." && pwd)"

STACK=(
  AMOURANTHRTX
  Grok16
  GrokPy
  PythonG
  KILROY
  Final_Eye
  Final_Ear
  ZNEWOCR
  ZOCR
  ZNetwork
  World_Redata
  World_Repack
  Field_Primer
  Spiderweb
)

wired=0
skipped=0
missing=0

for name in "${STACK[@]}"; do
  target="${PARENT}/${name}"
  link="${ROOT}/${name}"
  if [[ -L "$link" ]]; then
    echo "skip  ${name} (symlink exists -> $(readlink "$link"))"
    skipped=$((skipped + 1))
    continue
  fi
  if [[ -e "$link" && ! -L "$link" ]]; then
    echo "skip  ${name} (real directory in NewLatest — not replacing)"
    skipped=$((skipped + 1))
    continue
  fi
  if [[ ! -e "$target" ]]; then
    echo "miss  ${name} (no ${target})"
    missing=$((missing + 1))
    continue
  fi
  ln -sfn "$target" "$link"
  echo "link  ${name} -> ${target}"
  wired=$((wired + 1))
done

# Training viewer lives inside NewLatest
if [[ ! -d "${ROOT}/hostess7-training-viewer" && -d "${PARENT}/hostess7-training-viewer" ]]; then
  mv "${PARENT}/hostess7-training-viewer" "${ROOT}/"
  echo "move  hostess7-training-viewer -> NewLatest/"
  wired=$((wired + 1))
fi
if [[ -d "${ROOT}/hostess7-training-viewer" && ! -e "${PARENT}/hostess7-training-viewer" ]]; then
  ln -sfn "${ROOT}/hostess7-training-viewer" "${PARENT}/hostess7-training-viewer"
  echo "link  ../hostess7-training-viewer (compat)"
fi

# Legacy SG/Hostess7 -> NewLatest/Hostess7
if [[ ! -e "${PARENT}/Hostess7" ]]; then
  ln -sfn "${ROOT}/Hostess7" "${PARENT}/Hostess7"
  echo "link  ../Hostess7 -> NewLatest/Hostess7"
fi

echo "--- wired=${wired} skipped=${skipped} missing=${missing} root=${ROOT}"
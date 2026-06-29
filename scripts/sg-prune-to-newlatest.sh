#!/bin/bash
# Prune SG/ — keep only NewLatest after wiring useful siblings into the canonical tree.
set -euo pipefail

SG="$(cd "$(dirname "$0")/../.." && pwd)"
NL="${SG}/NewLatest"

if [[ ! -d "$NL" ]]; then
  echo "error: ${NL} missing" >&2
  exit 1
fi

echo "== absorb external symlinks into NewLatest =="
for link in "${NL}"/*; do
  [[ -L "$link" ]] || continue
  target="$(readlink -f "$link" 2>/dev/null || true)"
  [[ -n "$target" ]] || continue
  case "$target" in
    "${NL}"/*) continue ;;
    "${SG}"/*)
      name="$(basename "$link")"
      echo "absorb ${name} <- ${target}"
      rm -f "$link"
      if [[ -d "$target" ]]; then
        mv "$target" "$link"
      else
        cp -a "$target" "$link"
        rm -f "$target"
      fi
      ;;
  esac
done

echo "== wire stack into NewLatest =="
if [[ -x "${NL}/scripts/wire-stack.sh" ]]; then
  bash "${NL}/scripts/wire-stack.sh" || true
fi

KEEP=(
  NewLatest
  .nexus-state
)

echo "== SG prune audit =="
for entry in "$SG"/* "$SG"/.[!.]*; do
  [[ -e "$entry" ]] || continue
  base="$(basename "$entry")"
  keep=0
  for k in "${KEEP[@]}"; do
    if [[ "$base" == "$k" ]]; then
      keep=1
      break
    fi
  done
  if [[ $keep -eq 1 ]]; then
    echo "keep  ${base}"
    continue
  fi
  echo "remove ${base}"
  rm -rf "$entry"
done

echo "== done — SG contents =="
ls -la "$SG"
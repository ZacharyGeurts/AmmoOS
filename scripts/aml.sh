#!/usr/bin/env bash
# AmmoLang task entry — kit Grok16 · hang guard · minute progress.
exec "$(cd "$(dirname "$0")/.." && pwd)/lib/ammolang-route.sh" "${1:-tasks}" "${@:2}"
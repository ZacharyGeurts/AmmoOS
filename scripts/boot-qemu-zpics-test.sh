#!/usr/bin/env bash
exec "$(cd "$(dirname "$0")/.." && pwd)/lib/ammolang-route.sh" boot_qemu_test "$@"
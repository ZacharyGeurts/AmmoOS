"""GrokPy native interpreter — lexer, parser, compiler, VM."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from vm import GrokVM, VMError


def run_source(source: str, *, globals: dict[str, Any] | None = None) -> Any:
    vm = GrokVM()
    if globals:
        vm.globals.update(globals)
    return vm.run_source(source)


def run_file(path: str | Path, *, globals: dict[str, Any] | None = None) -> Any:
    p = Path(path)
    return run_source(p.read_text(encoding="utf-8"), globals=globals)


__all__ = ["GrokVM", "VMError", "run_file", "run_source"]
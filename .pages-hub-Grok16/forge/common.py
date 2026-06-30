"""Shared Grok16 forge helpers."""
from __future__ import annotations

from engine import ForgeEngine, ForgeResult


def ok_result(engine: ForgeEngine, tool: str, msg: str = "") -> ForgeResult:
    return ForgeResult(ok=True, tool=tool, message=msg, tail=engine.tail_buffer())


def fail_result(engine: ForgeEngine, tool: str, msg: str, rc: int = 1) -> ForgeResult:
    return ForgeResult(ok=False, tool=tool, message=msg, returncode=rc, tail=engine.tail_buffer())
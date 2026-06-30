"""GrokPy object model."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class GrokFunction:
    name: str
    argnames: list[str]
    code: Any
    defaults: list[Any] = field(default_factory=list)
    closure: dict[str, Any] | None = None


@dataclass
class Code:
    consts: list[Any]
    names: list[str]
    varnames: list[str]
    instrs: list[tuple[int, Any]]
    argcount: int = 0
    name: str = "<module>"


class GrokObject:
    """Tagged runtime values."""

    __slots__ = ("value", "type_name")

    def __init__(self, value: Any, type_name: str) -> None:
        self.value = value
        self.type_name = type_name

    def __repr__(self) -> str:
        return repr(self.value)


def grok_repr(v: Any) -> str:
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "True" if v else "False"
    return repr(v)
"""GrokPy AST nodes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Module:
    body: list[Any]


@dataclass
class Assign:
    targets: list[str]
    value: Any


@dataclass
class ExprStmt:
    value: Any


@dataclass
class If:
    test: Any
    body: list[Any]
    orelse: list[Any] = field(default_factory=list)


@dataclass
class While:
    test: Any
    body: list[Any]


@dataclass
class For:
    target: str
    iter: Any
    body: list[Any]


@dataclass
class FunctionDef:
    name: str
    args: list[str]
    body: list[Any]
    defaults: list[Any] = field(default_factory=list)


@dataclass
class Return:
    value: Any | None = None


@dataclass
class Pass:
    pass


@dataclass
class Break:
    pass


@dataclass
class BinOp:
    left: Any
    op: str
    right: Any


@dataclass
class UnaryOp:
    op: str
    operand: Any


@dataclass
class Compare:
    left: Any
    ops: list[str]
    comparators: list[Any]


@dataclass
class Call:
    func: Any
    args: list[Any]


@dataclass
class Name:
    id: str


@dataclass
class Constant:
    value: Any


@dataclass
class ListLit:
    elts: list[Any]


@dataclass
class Attribute:
    value: Any
    attr: str
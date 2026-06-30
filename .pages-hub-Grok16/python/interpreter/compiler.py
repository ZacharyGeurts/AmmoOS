"""GrokPy compiler — AST to GROKPY12 bytecode."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ast_nodes import (
    Assign,
    BinOp,
    Break,
    Call,
    Compare,
    Constant,
    ExprStmt,
    For,
    FunctionDef,
    If,
    ListLit,
    Module,
    Name,
    Pass,
    Return,
    UnaryOp,
    While,
)
from objects import Code
from grok_opcode import (
    COMPARE_EQ,
    COMPARE_GE,
    COMPARE_GT,
    COMPARE_LE,
    COMPARE_LT,
    COMPARE_NE,
    Op,
)


class CompileError(Exception):
    pass


_CMP_MAP = {
    "==": COMPARE_EQ,
    "!=": COMPARE_NE,
    "<": COMPARE_LT,
    "<=": COMPARE_LE,
    ">": COMPARE_GT,
    ">=": COMPARE_GE,
}

_BIN_MAP = {
    "+": Op.BINARY_ADD,
    "-": Op.BINARY_SUB,
    "*": Op.BINARY_MUL,
    "/": Op.BINARY_TRUE_DIV,
    "//": Op.BINARY_FLOOR_DIV,
    "%": Op.BINARY_MOD,
    "**": Op.BINARY_POW,
}


@dataclass
class _LoopCtx:
    break_patches: list[int] = field(default_factory=list)
    head: int = 0


class Compiler:
    def __init__(self, *, name: str = "<module>", argnames: list[str] | None = None) -> None:
        self.code = Code(
            consts=[],
            names=[],
            varnames=list(argnames or []),
            instrs=[],
            argcount=len(argnames or []),
            name=name,
        )
        self._const_index: dict[Any, int] = {}
        self._name_index: dict[str, int] = {}
        self._loop_stack: list[_LoopCtx] = []
        self._assigned_locals: set[str] = set(argnames or [])

    def _const(self, value: Any) -> int:
        key = (type(value), value if isinstance(value, (int, float, str, bool, type(None))) else id(value))
        if key not in self._const_index:
            self._const_index[key] = len(self.code.consts)
            self.code.consts.append(value)
        return self._const_index[key]

    def _name(self, ident: str) -> int:
        if ident not in self._name_index:
            self._name_index[ident] = len(self.code.names)
            self.code.names.append(ident)
        return self._name_index[ident]

    def _emit(self, op: Op, arg: Any = None) -> int:
        self.code.instrs.append((int(op), arg))
        return len(self.code.instrs) - 1

    def _patch(self, idx: int, arg: Any) -> None:
        op, _ = self.code.instrs[idx]
        self.code.instrs[idx] = (op, arg)

    def compile(self, mod: Module) -> Code:
        for stmt in mod.body:
            self._stmt(stmt)
        self._emit(Op.LOAD_CONST, self._const(None))
        self._emit(Op.RETURN)
        return self.code

    def _stmt(self, node: Any) -> None:
        if isinstance(node, Assign):
            self._expr(node.value)
            for target in node.targets:
                self._store(target)
            return
        if isinstance(node, ExprStmt):
            self._expr(node.value)
            self._emit(Op.POP_TOP)
            return
        if isinstance(node, Pass):
            return
        if isinstance(node, Return):
            if node.value is not None:
                self._expr(node.value)
            else:
                self._emit(Op.LOAD_CONST, self._const(None))
            self._emit(Op.RETURN)
            return
        if isinstance(node, Break):
            if not self._loop_stack:
                raise CompileError("break outside loop")
            patch = self._emit(Op.JUMP_FORWARD, None)
            self._loop_stack[-1].break_patches.append(patch)
            return
        if isinstance(node, If):
            self._if_stmt(node)
            return
        if isinstance(node, While):
            self._while_stmt(node)
            return
        if isinstance(node, For):
            self._for_stmt(node)
            return
        if isinstance(node, FunctionDef):
            self._function_def(node)
            return
        raise CompileError(f"unsupported stmt {type(node).__name__}")

    def _if_stmt(self, node: If) -> None:
        self._expr(node.test)
        jump_false = self._emit(Op.JUMP_IF_FALSE, None)
        for stmt in node.body:
            self._stmt(stmt)
        jump_end = self._emit(Op.JUMP_FORWARD, None)
        self._patch(jump_false, len(self.code.instrs))
        for stmt in node.orelse:
            self._stmt(stmt)
        self._patch(jump_end, len(self.code.instrs))

    def _while_stmt(self, node: While) -> None:
        loop = _LoopCtx(head=len(self.code.instrs))
        self._loop_stack.append(loop)
        self._expr(node.test)
        jump_end = self._emit(Op.JUMP_IF_FALSE, None)
        for stmt in node.body:
            self._stmt(stmt)
        self._emit(Op.JUMP_FORWARD, loop.head)
        end = len(self.code.instrs)
        self._patch(jump_end, end)
        for patch in loop.break_patches:
            self._patch(patch, end)
        self._loop_stack.pop()

    def _for_stmt(self, node: For) -> None:
        self._expr(node.iter)
        self._emit(Op.GET_ITER)
        loop = _LoopCtx(head=len(self.code.instrs))
        self._loop_stack.append(loop)
        jump_end = self._emit(Op.FOR_ITER, None)
        self._store(node.target)
        for stmt in node.body:
            self._stmt(stmt)
        self._emit(Op.JUMP_FORWARD, loop.head)
        end = len(self.code.instrs)
        self._patch(jump_end, end)
        for patch in loop.break_patches:
            self._patch(patch, end)
        self._loop_stack.pop()

    def _function_def(self, node: FunctionDef) -> None:
        child = Compiler(name=node.name, argnames=node.args)
        for stmt in node.body:
            child._stmt(stmt)
        child._emit(Op.LOAD_CONST, child._const(None))
        child._emit(Op.RETURN)
        fn_code = child.code
        self._emit(Op.LOAD_CONST, self._const(fn_code))
        for default in node.defaults:
            self._expr(default)
        self._emit(Op.MAKE_FUNCTION, len(node.defaults))
        if self.code.name == "<module>":
            self._emit(Op.STORE_GLOBAL, self._name(node.name))
        else:
            self._emit(Op.STORE_NAME, self._var(node.name))

    def _store(self, name: str) -> None:
        if self.code.name == "<module>":
            self._emit(Op.STORE_GLOBAL, self._name(name))
        else:
            self._assigned_locals.add(name)
            self._emit(Op.STORE_NAME, self._var(name))

    def _var(self, name: str) -> int:
        if name not in self.code.varnames:
            self.code.varnames.append(name)
        return self.code.varnames.index(name)

    def _expr(self, node: Any) -> None:
        if isinstance(node, Constant):
            self._emit(Op.LOAD_CONST, self._const(node.value))
            return
        if isinstance(node, Name):
            if self.code.name == "<module>" or (
                node.id not in self._assigned_locals and node.id not in self.code.varnames[: self.code.argcount]
            ):
                self._emit(Op.LOAD_GLOBAL, self._name(node.id))
            else:
                self._emit(Op.LOAD_NAME, self._var(node.id))
            return
        if isinstance(node, BinOp):
            self._expr(node.left)
            self._expr(node.right)
            op = _BIN_MAP.get(node.op)
            if op is None:
                raise CompileError(f"unknown binop {node.op}")
            self._emit(op)
            return
        if isinstance(node, UnaryOp):
            self._expr(node.operand)
            if node.op == "-":
                self._emit(Op.UNARY_NEG)
            elif node.op == "not":
                self._emit(Op.UNARY_NOT)
            elif node.op == "+":
                pass
            else:
                raise CompileError(f"unknown unary {node.op}")
            return
        if isinstance(node, Compare):
            self._compare(node)
            return
        if isinstance(node, Call):
            self._expr(node.func)
            for arg in node.args:
                self._expr(arg)
            self._emit(Op.CALL, len(node.args))
            return
        if isinstance(node, ListLit):
            for elt in node.elts:
                self._expr(elt)
            self._emit(Op.BUILD_LIST, len(node.elts))
            return
        raise CompileError(f"unsupported expr {type(node).__name__}")

    def _compare(self, node: Compare) -> None:
        if len(node.ops) == 1:
            self._expr(node.left)
            self._expr(node.comparators[0])
            self._emit(Op.COMPARE_OP, _CMP_MAP[node.ops[0]])
            return
        raise CompileError("chained comparisons not yet supported")


def compile_module(mod: Module) -> Code:
    return Compiler().compile(mod)


def compile_source(source: str) -> Code:
    from parser import parse_source

    return compile_module(parse_source(source))


_COMPILE_CACHE: dict[str, Code] = {}
_COMPILE_CACHE_MAX = 128


def compile_source_cached(source: str) -> Code:
    """Fast path — in-memory compile cache keyed by source hash."""
    import hashlib
    import os

    if os.environ.get("GPY16_NO_CACHE", "").strip().lower() in ("1", "true", "yes"):
        return compile_source(source)
    key = hashlib.sha256(source.encode("utf-8")).hexdigest()[:24]
    hit = _COMPILE_CACHE.get(key)
    if hit is not None:
        return hit
    code = compile_source(source)
    if len(_COMPILE_CACHE) >= _COMPILE_CACHE_MAX:
        _COMPILE_CACHE.clear()
    _COMPILE_CACHE[key] = code
    return code
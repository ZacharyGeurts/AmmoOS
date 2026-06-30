"""GrokPy VM — GROKPY12 stack machine, field AI globals on boot."""
from __future__ import annotations

import os
from typing import Any

from grok_builtins import grok_ai_status, grok_truth_floor, make_builtins
from objects import Code, GrokFunction
from grok_opcode import (
    COMPARE_EQ,
    COMPARE_GE,
    COMPARE_GT,
    COMPARE_LE,
    COMPARE_LT,
    COMPARE_NE,
    Op,
)


class VMError(Exception):
    pass


class _ReturnSignal(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value


class Frame:
    __slots__ = ("code", "globals", "locals")

    def __init__(self, code: Code, globals: dict[str, Any], locals: dict[str, Any] | None = None) -> None:
        self.code = code
        self.globals = globals
        self.locals = locals if locals is not None else {}

    def load_name(self, idx: int) -> Any:
        name = self.code.varnames[idx]
        if name in self.locals:
            return self.locals[name]
        if name in self.globals:
            return self.globals[name]
        raise VMError(f"name not defined: {name}")

    def store_name(self, idx: int, value: Any) -> None:
        self.locals[self.code.varnames[idx]] = value

    def store_global(self, idx: int, value: Any) -> None:
        self.globals[self.code.names[idx]] = value


_VM_SINGLETON: "GrokVM | None" = None


def _fast_mode() -> bool:
    return os.environ.get("GPY16_FAST", "").strip().lower() in ("1", "true", "yes", "on")


def _skip_ai_boot() -> bool:
    return _fast_mode() or os.environ.get("GPY16_SKIP_AI_BOOT", "").strip().lower() in ("1", "true", "yes")


class GrokVM:
    def __init__(self) -> None:
        self.globals: dict[str, Any] = dict(make_builtins())
        if not _skip_ai_boot() and (
            os.environ.get("GROKPY_FIELD") == "1" or os.environ.get("PYTHONG_FIELD") == "1"
        ):
            self.globals["__truth_floor__"] = grok_truth_floor()
            self.globals["__grokpy_ai__"] = grok_ai_status()

    def run_source(self, source: str, *, path: str | None = None) -> Any:
        from pathlib import Path

        from compiler import compile_source_cached
        from grok_core.cache import load_bytecode, store_bytecode

        src_path = Path(path) if path else None
        cached = load_bytecode(source=source, path=src_path)
        if cached is not None:
            return self.run_code(cached)
        code = compile_source_cached(source)
        store_bytecode(code, source=source, path=src_path)
        return self.run_code(code)

    def run_file(self, path: str) -> Any:
        from pathlib import Path

        p = Path(path)
        return self.run_source(p.read_text(encoding="utf-8"), path=str(p.resolve()))

    def run_code(self, code: Code) -> Any:
        frame = Frame(code, self.globals)
        return self._run_frame(frame)

    def _run_frame(self, frame: Frame) -> Any:
        stack: list[Any] = []
        code = frame.code
        instrs = code.instrs
        consts = code.consts
        names = code.names
        load_name = frame.load_name
        store_name = frame.store_name
        store_global = frame.store_global
        globals_ref = frame.globals
        ip = 0
        cmp_ops = (
            lambda x, y: x == y,
            lambda x, y: x != y,
            lambda x, y: x < y,
            lambda x, y: x <= y,
            lambda x, y: x > y,
            lambda x, y: x >= y,
        )
        call_fn = self._call_function
        try:
            while ip < len(instrs):
                op_raw, arg = instrs[ip]
                ip += 1
                if op_raw == Op.LOAD_CONST:
                    stack.append(consts[arg])
                elif op_raw == Op.LOAD_NAME:
                    stack.append(load_name(arg))
                elif op_raw == Op.LOAD_GLOBAL:
                    name = names[arg]
                    if name not in globals_ref:
                        raise VMError(f"global not defined: {name}")
                    stack.append(globals_ref[name])
                elif op_raw == Op.STORE_NAME:
                    store_name(arg, stack.pop())
                elif op_raw == Op.STORE_GLOBAL:
                    store_global(arg, stack.pop())
                elif op_raw == Op.POP_TOP:
                    stack.pop()
                elif op_raw == Op.DUP_TOP:
                    stack.append(stack[-1])
                elif op_raw == Op.BINARY_ADD:
                    b, a = stack.pop(), stack.pop()
                    stack.append(a + b)
                elif op_raw == Op.BINARY_SUB:
                    b, a = stack.pop(), stack.pop()
                    stack.append(a - b)
                elif op_raw == Op.BINARY_MUL:
                    b, a = stack.pop(), stack.pop()
                    stack.append(a * b)
                elif op_raw == Op.BINARY_TRUE_DIV:
                    b, a = stack.pop(), stack.pop()
                    stack.append(a / b)
                elif op_raw == Op.BINARY_FLOOR_DIV:
                    b, a = stack.pop(), stack.pop()
                    stack.append(a // b)
                elif op_raw == Op.BINARY_MOD:
                    b, a = stack.pop(), stack.pop()
                    stack.append(a % b)
                elif op_raw == Op.BINARY_POW:
                    b, a = stack.pop(), stack.pop()
                    stack.append(a ** b)
                elif op_raw == Op.UNARY_NEG:
                    stack.append(-stack.pop())
                elif op_raw == Op.UNARY_NOT:
                    stack.append(not stack.pop())
                elif op_raw == Op.COMPARE_OP:
                    b, a = stack.pop(), stack.pop()
                    stack.append(cmp_ops[arg](a, b))
                elif op_raw == Op.JUMP_FORWARD:
                    ip = arg
                elif op_raw == Op.JUMP_IF_FALSE:
                    if not stack.pop():
                        ip = arg
                elif op_raw == Op.JUMP_IF_TRUE:
                    if stack.pop():
                        ip = arg
                elif op_raw == Op.GET_ITER:
                    stack.append(iter(stack.pop()))
                elif op_raw == Op.FOR_ITER:
                    it = stack[-1]
                    try:
                        stack.append(next(it))
                    except StopIteration:
                        stack.pop()
                        ip = arg
                elif op_raw == Op.BUILD_LIST:
                    stack.append([stack.pop() for _ in range(arg)][::-1])
                elif op_raw == Op.BUILD_TUPLE:
                    stack.append(tuple([stack.pop() for _ in range(arg)][::-1]))
                elif op_raw == Op.CALL:
                    argc = arg
                    args = [stack.pop() for _ in range(argc)][::-1]
                    fn = stack.pop()
                    if isinstance(fn, GrokFunction):
                        ret = call_fn(fn, args)
                        if ret is not None:
                            stack.append(ret)
                    elif callable(fn):
                        stack.append(fn(*args))
                    else:
                        raise VMError("call on non-callable")
                elif op_raw == Op.RETURN:
                    raise _ReturnSignal(stack.pop() if stack else None)
                elif op_raw == Op.MAKE_FUNCTION:
                    ndef = arg
                    defaults = [stack.pop() for _ in range(ndef)][::-1] if ndef else []
                    fn_code = stack.pop()
                    stack.append(
                        GrokFunction(
                            name=fn_code.name,
                            argnames=list(fn_code.varnames[: fn_code.argcount]),
                            code=fn_code,
                            defaults=defaults,
                        )
                    )
                else:
                    raise VMError(f"unhandled op: {Op(op_raw)}")
        except _ReturnSignal as sig:
            return sig.value
        return None

    def _call_function(self, fn: GrokFunction, args: list[Any]) -> Any:
        local: dict[str, Any] = {}
        nargs = len(fn.argnames)
        ndef = len(fn.defaults)
        pos_required = nargs - ndef
        for i, name in enumerate(fn.argnames):
            if i < len(args):
                local[name] = args[i]
            elif i >= pos_required:
                local[name] = fn.defaults[i - pos_required]
            else:
                raise VMError(f"missing arg: {name}")
        child_globals = dict(fn.globals) if hasattr(fn, "globals") else dict(self.globals)
        if fn.closure:
            child_globals.update(fn.closure)
        frame = Frame(fn.code, child_globals, local)
        return self._run_frame(frame)


def get_vm(*, reset: bool = False) -> GrokVM:
    """Singleton GrokVM — reuse across hot invocations when GPY16_FAST=1."""
    global _VM_SINGLETON
    if reset or _VM_SINGLETON is None:
        _VM_SINGLETON = GrokVM()
    return _VM_SINGLETON
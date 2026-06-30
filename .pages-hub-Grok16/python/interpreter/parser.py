"""GrokPy parser — Python syntax to AST."""
from __future__ import annotations

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
from lexer import LexError, TokKind, Token


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def _cur(self) -> Token:
        return self.tokens[self.pos]

    def _eat(self, kind: TokKind | None = None, value: str | None = None) -> Token:
        t = self._cur()
        if kind and t.kind != kind:
            raise ParseError(f"expected {kind}, got {t.kind} {t.value!r}")
        if value and t.value != value:
            raise ParseError(f"expected {value!r}, got {t.value!r}")
        self.pos += 1
        return t

    def _match(self, kind: TokKind, value: str | None = None) -> bool:
        t = self._cur()
        if t.kind != kind:
            return False
        if value and t.value != value:
            return False
        self.pos += 1
        return True

    def parse(self) -> Module:
        body = self._suite(expect_indent=False)
        self._eat(TokKind.EOF)
        return Module(body=body)

    def _suite(self, *, expect_indent: bool) -> list[Any]:
        stmts: list[Any] = []
        if expect_indent:
            if not self._match(TokKind.INDENT):
                return [Pass()]
        while self._cur().kind not in (TokKind.DEDENT, TokKind.EOF):
            if self._cur().kind == TokKind.NEWLINE:
                self._eat()
                continue
            stmts.append(self._stmt())
            if self._cur().kind == TokKind.NEWLINE:
                self._eat()
        if expect_indent and self._cur().kind == TokKind.DEDENT:
            self._eat()
        return stmts

    def _stmt(self) -> Any:
        t = self._cur()
        if t.kind == TokKind.KEYWORD:
            if t.value == "if":
                return self._if_stmt()
            if t.value == "while":
                return self._while_stmt()
            if t.value == "for":
                return self._for_stmt()
            if t.value == "def":
                return self._def_stmt()
            if t.value == "return":
                self._eat()
                val = None if self._cur().kind == TokKind.NEWLINE else self._expr()
                return Return(val)
            if t.value == "pass":
                self._eat()
                return Pass()
            if t.value == "break":
                self._eat()
                return Break()
        if t.kind == TokKind.IDENT and self.tokens[self.pos + 1].kind == TokKind.OP and self.tokens[self.pos + 1].value == "=":
            targets = [self._eat(TokKind.IDENT).value]
            while self._match(TokKind.OP, ","):
                targets.append(self._eat(TokKind.IDENT).value)
            self._eat(TokKind.OP, "=")
            return Assign(targets=targets, value=self._expr())
        return ExprStmt(self._expr())

    def _if_stmt(self) -> If:
        self._eat(TokKind.KEYWORD, "if")
        test = self._expr()
        self._eat(TokKind.OP, ":")
        self._eat(TokKind.NEWLINE)
        body = self._suite(expect_indent=True)
        while self._cur().kind == TokKind.NEWLINE:
            self._eat()
        orelse: list[Any] = []
        if self._match(TokKind.KEYWORD, "elif"):
            orelse = [self._if_stmt()]
        elif self._match(TokKind.KEYWORD, "else"):
            self._eat(TokKind.OP, ":")
            self._eat(TokKind.NEWLINE)
            orelse = self._suite(expect_indent=True)
        return If(test=test, body=body, orelse=orelse)

    def _while_stmt(self) -> While:
        self._eat(TokKind.KEYWORD, "while")
        test = self._expr()
        self._eat(TokKind.OP, ":")
        self._eat(TokKind.NEWLINE)
        body = self._suite(expect_indent=True)
        return While(test=test, body=body)

    def _for_stmt(self) -> For:
        self._eat(TokKind.KEYWORD, "for")
        target = self._eat(TokKind.IDENT).value
        self._eat(TokKind.KEYWORD, "in")
        it = self._expr()
        self._eat(TokKind.OP, ":")
        self._eat(TokKind.NEWLINE)
        body = self._suite(expect_indent=True)
        return For(target=target, iter=it, body=body)

    def _def_stmt(self) -> FunctionDef:
        self._eat(TokKind.KEYWORD, "def")
        name = self._eat(TokKind.IDENT).value
        self._eat(TokKind.OP, "(")
        args: list[str] = []
        defaults: list[Any] = []
        if not self._match(TokKind.OP, ")"):
            while True:
                args.append(self._eat(TokKind.IDENT).value)
                if self._match(TokKind.OP, "="):
                    defaults.append(self._expr())
                if not self._match(TokKind.OP, ","):
                    break
            self._eat(TokKind.OP, ")")
        self._eat(TokKind.OP, ":")
        self._eat(TokKind.NEWLINE)
        body = self._suite(expect_indent=True)
        return FunctionDef(name=name, args=args, body=body, defaults=defaults)

    def _expr(self) -> Any:
        return self._compare()

    def _compare(self) -> Any:
        left = self._arith()
        ops: list[str] = []
        comps: list[Any] = []
        cmps = {"==", "!=", "<", "<=", ">", ">="}
        while self._cur().kind == TokKind.OP and self._cur().value in cmps:
            ops.append(self._eat().value)
            comps.append(self._arith())
        if ops:
            return Compare(left=left, ops=ops, comparators=comps)
        return left

    def _arith(self) -> Any:
        left = self._term()
        while self._cur().kind == TokKind.OP and self._cur().value in ("+", "-"):
            op = self._eat().value
            left = BinOp(left=left, op=op, right=self._term())
        return left

    def _term(self) -> Any:
        left = self._factor()
        while self._cur().kind == TokKind.OP and self._cur().value in ("*", "/", "//", "%"):
            op = self._eat().value
            left = BinOp(left=left, op=op, right=self._factor())
        return left

    def _factor(self) -> Any:
        if self._match(TokKind.OP, "+"):
            return UnaryOp(op="+", operand=self._factor())
        if self._match(TokKind.OP, "-"):
            return UnaryOp(op="-", operand=self._factor())
        if self._match(TokKind.KEYWORD, "not"):
            return UnaryOp(op="not", operand=self._factor())
        return self._primary()

    def _primary(self) -> Any:
        t = self._cur()
        if t.kind == TokKind.NUMBER:
            self._eat()
            return Constant(float(t.value) if "." in t.value else int(t.value))
        if t.kind == TokKind.STRING:
            self._eat()
            v = t.value[1:-1]
            return Constant(v)
        if t.kind == TokKind.KEYWORD and t.value in ("True", "False", "None"):
            self._eat()
            return Constant({"True": True, "False": False, "None": None}[t.value])
        if t.kind == TokKind.IDENT:
            name = self._eat().value
            node: Any = Name(id=name)
            while self._match(TokKind.OP, "("):
                args = []
                if not self._match(TokKind.OP, ")"):
                    while True:
                        args.append(self._expr())
                        if not self._match(TokKind.OP, ","):
                            break
                    self._eat(TokKind.OP, ")")
                node = Call(func=node, args=args)
            return node
        if self._match(TokKind.OP, "("):
            e = self._expr()
            self._eat(TokKind.OP, ")")
            return e
        if self._match(TokKind.OP, "["):
            elts = []
            if not self._match(TokKind.OP, "]"):
                while True:
                    elts.append(self._expr())
                    if not self._match(TokKind.OP, ","):
                        break
                self._eat(TokKind.OP, "]")
            return ListLit(elts=elts)
        raise ParseError(f"unexpected token {t.kind} {t.value!r}")


def parse_source(source: str) -> Module:
    from lexer import Lexer
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()
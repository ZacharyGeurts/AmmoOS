"""GrokPy lexer — tokenize Python/Grok source."""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterator


class TokKind(Enum):
    IDENT = auto()
    NUMBER = auto()
    STRING = auto()
    KEYWORD = auto()
    OP = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


KEYWORDS = frozenset({
    "and", "or", "not", "if", "elif", "else", "while", "for", "in",
    "def", "return", "True", "False", "None", "pass", "break", "continue",
    "import", "from", "class", "lambda", "as", "is",
})

OPS = [
    "**", "//", "==", "!=", "<=", ">=", "+=", "-=", "*=", "/=",
    "+", "-", "*", "/", "%", "<", ">", "=", "(", ")", "[", "]", "{", "}",
    ",", ":", ".", "@",
]


@dataclass
class Token:
    kind: TokKind
    value: str
    line: int
    col: int


class LexError(Exception):
    pass


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.line = 1
        self.col = 1
        self.i = 0
        self.indent_stack = [0]

    def _peek(self, n: int = 0) -> str:
        j = self.i + n
        return self.source[j] if j < len(self.source) else ""

    def _advance(self, n: int = 1) -> None:
        for _ in range(n):
            if self.i < len(self.source):
                if self.source[self.i] == "\n":
                    self.line += 1
                    self.col = 1
                else:
                    self.col += 1
                self.i += 1

    def _skip_ws(self, *, newline: bool = False) -> None:
        while self.i < len(self.source):
            c = self.source[self.i]
            if c in " \t\r":
                self._advance()
            elif c == "#":
                while self._peek() and self._peek() != "\n":
                    self._advance()
            elif newline and c == "\n":
                break
            else:
                break

    def _string(self, quote: str) -> str:
        self._advance()
        buf: list[str] = []
        while self.i < len(self.source):
            c = self._peek()
            if c == "\\":
                self._advance(2)
                buf.append("\\")
                continue
            if c == quote:
                self._advance()
                return quote + "".join(buf) + quote
            buf.append(c)
            self._advance()
        raise LexError(f"unterminated string at {self.line}:{self.col}")

    def _number(self) -> str:
        start = self.i
        while self._peek() and (self._peek().isdigit() or self._peek() == "."):
            self._advance()
        return self.source[start:self.i]

    def _ident(self) -> str:
        start = self.i
        while self._peek() and (self._peek().isalnum() or self._peek() == "_"):
            self._advance()
        return self.source[start:self.i]

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        at_line_start = True
        while self.i < len(self.source):
            if at_line_start:
                if self._peek() == "\n":
                    self._advance()
                    tokens.append(Token(TokKind.NEWLINE, "\\n", self.line, self.col))
                    continue
                start = self.i
                while self._peek() in " \t":
                    self._advance()
                indent = self.i - start
                if self._peek() == "\n" or (self._peek() == "#" and not self._peek(1)):
                    if self._peek() == "#":
                        while self._peek() and self._peek() != "\n":
                            self._advance()
                    if self._peek() == "\n":
                        self._advance()
                        tokens.append(Token(TokKind.NEWLINE, "\\n", self.line, self.col))
                    continue
                top = self.indent_stack[-1]
                if indent > top:
                    self.indent_stack.append(indent)
                    tokens.append(Token(TokKind.INDENT, "", self.line, self.col))
                elif indent < top:
                    while self.indent_stack and self.indent_stack[-1] > indent:
                        self.indent_stack.pop()
                        tokens.append(Token(TokKind.DEDENT, "", self.line, self.col))
                    if not self.indent_stack or self.indent_stack[-1] != indent:
                        raise LexError(f"indent mismatch {self.line}")
                at_line_start = False

            self._skip_ws()
            if not self._peek():
                break
            if self._peek() == "\n":
                self._advance()
                tokens.append(Token(TokKind.NEWLINE, "\\n", self.line, self.col))
                at_line_start = True
                continue
            c = self._peek()
            if c in "\"'":
                s = self._string(c)
                tokens.append(Token(TokKind.STRING, s, self.line, self.col))
                continue
            if c.isdigit():
                tokens.append(Token(TokKind.NUMBER, self._number(), self.line, self.col))
                continue
            if c.isalpha() or c == "_":
                ident = self._ident()
                kind = TokKind.KEYWORD if ident in KEYWORDS else TokKind.IDENT
                tokens.append(Token(kind, ident, self.line, self.col))
                continue
            matched = False
            for op in OPS:
                if self.source[self.i:self.i + len(op)] == op:
                    tokens.append(Token(TokKind.OP, op, self.line, self.col))
                    self._advance(len(op))
                    matched = True
                    break
            if not matched:
                raise LexError(f"unknown char {c!r} at {self.line}:{self.col}")
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            tokens.append(Token(TokKind.DEDENT, "", self.line, self.col))
        tokens.append(Token(TokKind.EOF, "", self.line, self.col))
        return tokens
"""GrokPy bytecode — GROKPY12 instruction set."""
from __future__ import annotations

from enum import IntEnum


class Op(IntEnum):
    LOAD_CONST = 1
    LOAD_NAME = 2
    LOAD_GLOBAL = 3
    STORE_NAME = 4
    STORE_GLOBAL = 5
    POP_TOP = 6
    DUP_TOP = 7
    BINARY_ADD = 10
    BINARY_SUB = 11
    BINARY_MUL = 12
    BINARY_TRUE_DIV = 13
    BINARY_FLOOR_DIV = 14
    BINARY_MOD = 15
    BINARY_POW = 16
    UNARY_NEG = 20
    UNARY_NOT = 21
    COMPARE_OP = 30
    JUMP_FORWARD = 40
    JUMP_IF_FALSE = 41
    JUMP_IF_TRUE = 42
    CALL = 50
    RETURN = 51
    BUILD_LIST = 60
    BUILD_TUPLE = 61
    GET_ITER = 70
    FOR_ITER = 71
    MAKE_FUNCTION = 80


COMPARE_EQ = 0
COMPARE_NE = 1
COMPARE_LT = 2
COMPARE_LE = 3
COMPARE_GT = 4
COMPARE_GE = 5

OP_NAMES = {op.value: op.name for op in Op}
import json
from enum import Enum
from typing import NamedTuple, Union, TypedDict

import numpy as np

"""Модуль интерфейса инструкций"""


class Opcode(str, Enum):
    ADD = 'add'  # reg1, reg2, reg_res
    SUB = 'sub'  # reg1, reg2, reg_res
    MOD = 'mod'  # reg1, reg2, reg_res
    INC = 'inc'  # reg1, reg_res
    DEC = 'dec'  # reg1, reg_res
    LD = 'ld'  # addr, #reg_res
    ST = 'st'  # reg, #addr
    MV = 'mv'  # reg1, #reg2
    BE = 'be'  # reg
    BNE = 'bne'  # reg
    JMP = 'jmp'  # reg
    HLT = 'hlt'


class Instr(TypedDict):
    opcode: Opcode
    args: list[int | str]


Cell = Union[np.int32, Instr]


def write_code(filename: str, code: list[Cell]):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(code, indent=4))


def read_code(filename: str) -> list[Cell]:
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())
    for i, cell in enumerate(code):
        if isinstance(cell, int):
            code[i] = np.int32(cell)
        else:
            cell["opcode"] = Opcode(cell["opcode"])

    return code

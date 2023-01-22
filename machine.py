from typing import Union, Optional

MAX_VALUE: int = 2_147_483_647
MIN_VALUE: int = -2_147_483_648
MAX_UVALUE: int = 4_294_967_295


def int_to_bin_str(val: int) -> str:
    res = str(bin(val & 0xffffffff))[2:]
    print(res)
    while len(res) < 32:
        res = '0' + res
    return res


def bin_str_to_int(bin_str: str) -> int:
    res = int(bin_str[:33], 2)
    print(res)
    if res > MAX_VALUE:
        res -= MAX_UVALUE + 1
    return res


def cut_to_machine_word(val: int) -> int:
    return bin_str_to_int(int_to_bin_str(val))


InstrArg = int | str | None


class Instruction:
    opcode: str
    arg1: InstrArg
    arg2: InstrArg


MachineWord = int | Instruction


class Memory:
    _mem: list[MachineWord]

    def __init__(self):
        self._mem = [0 for _ in range(MAX_VALUE)]
        pass

    def read(self, address: int) -> MachineWord:
        return self._mem[address]

    def write(self, address: int, value: MachineWord) -> None:
        self._mem[address] = value


class Registers:
    def __init__(self):
        pass


mem = Memory()
print(mem.read(1))

"""Модель процессора"""
import logging
import sys
from random import randint

from typing import Tuple

from isa import Cell, Instr, Opcode, read_code
import numpy as np


ZERO = np.int32(0)


class DataPath:
    """Тракт данных"""
    _memory_size: int
    memory: list[Cell]
    registers: list[Cell]
    _bus1: Cell
    _bus2: Cell
    _bus1_mux: Cell
    _alu: np.int32
    _zero_flag: bool
    _inverse_alu_in1: bool
    _inverse_alu_in2: bool
    _inc_alu_in1: bool
    _inc_alu_in2: bool
    _add_or_mod: bool
    instr_val: np.int32

    def __init__(self, memory: list[Cell], memory_size: int):
        assert memory_size > 0, "Memory size should be non-zero"
        self._memory_size = memory_size
        self.memory = memory
        self.registers = [ZERO] * 5
        self._bus1 = ZERO
        self._bus2 = ZERO
        self._bus1_mux = ZERO
        self._alu = ZERO
        self._zero_flag = False
        self._inverse_alu_in1 = False
        self._inverse_alu_in2 = False
        self._inc_alu_in1 = False
        self._inc_alu_in2 = False
        self._add_or_mod = False

    def select_registers(self, reg1: int, reg2: int):
        assert reg1 < len(self.registers), "Register R{} does not exists".format(reg1)
        assert reg2 < len(self.registers), "Register R{} does not exists".format(reg2)
        self._bus1 = ZERO
        self._bus2 = ZERO
        if reg1 != -1:
            self._bus1 = self.registers[reg1]
        if reg2 != -1:
            self._bus2 = self.registers[reg2]

    def latch_register(self, reg: int):
        assert reg < len(self.registers), "Register R{} does not exists".format(reg)
        self.registers[reg] = self._alu

    def get_instruction(self) -> Cell:
        if not(isinstance(self.registers[-1], np.int32)):
            address = randint(0, 512)
        else:
            address = int(self.registers[-1])
        return self.memory[address]

    def zero_flag(self):
        return self._zero_flag

    def bus1_mux_signal_bus(self):
        self._bus1_mux = self._bus1

    def bus1_mux_signal_instr(self, instr_val: np.int32):
        self._bus1_mux = instr_val

    def execute_alu(self, save_flag: bool = False):
        in1 = self._bus1_mux
        in2 = self._bus2

        if self._inverse_alu_in1:
            in1 = ~in1

        if self._inverse_alu_in2:
            in2 = ~in2

        if self._inc_alu_in1:
            in1 += np.int32(1)

        if self._inc_alu_in2:
            in2 += np.int32(1)

        if self._add_or_mod:
            self._alu = in1 % in2
        else:
            self._alu = in1 + in2
        if not save_flag:
            self._zero_flag = self._alu == np.int32(0)

    def inc_alu_in1(self):
        self._inc_alu_in1 = True
        self._inc_alu_in2 = False
        self._inverse_alu_in1 = False
        self._inverse_alu_in2 = False

    def negate_alu_in2(self):
        self._inc_alu_in1 = False
        self._inc_alu_in2 = True
        self._inverse_alu_in1 = False
        self._inverse_alu_in2 = True

    def dec_alu_in1(self):
        self._inc_alu_in1 = False
        self._inc_alu_in2 = False
        self._inverse_alu_in1 = False
        self._inverse_alu_in2 = True

    def select_add(self):
        self._add_or_mod = False

    def select_mod(self):
        self._add_or_mod = True

    def pass_alu_in(self):
        self._inc_alu_in1 = False
        self._inc_alu_in2 = False
        self._inverse_alu_in1 = False
        self._inverse_alu_in2 = False

    def read(self):
        assert 0 <= self._alu < self._memory_size, "Invalid address"
        self._alu = self.memory[self._alu]

    def wr(self):
        assert 0 <= self._alu < self._memory_size, "Invalid address"
        self.memory[self._alu] = self._bus2


class ControlUnit:
    _data_path: DataPath
    _tick: int

    def __init__(self, data_path: DataPath):
        self._data_path = data_path
        self._tick = 0
        self.inverse_alu_in2 = False
        self.inc_alu_in1 = False

    def tick(self):
        self._tick += 1

    def current_tick(self):
        return self._tick

    def fetch_instruction(self) -> Cell:
        instr = self._data_path.get_instruction()
        self._data_path.select_registers(4, -1)
        self._data_path.inc_alu_in1()
        self._data_path.bus1_mux_signal_bus()
        self._data_path.select_add()
        self._data_path.execute_alu(True)
        self._data_path.latch_register(4)
        self.tick()
        return instr

    def decode_and_execute_instruction(self, instr: Cell):
        assert isinstance(instr, dict), "bad instruction"
        opcode: Opcode = instr["opcode"]

        if opcode is Opcode.HLT:
            raise StopIteration()

        if opcode is Opcode.JMP:
            assert len(instr["args"]) == 1, "bad instruction"
            self._data_path.select_registers(-1, -1)
            self._data_path.bus1_mux_signal_instr(np.int32(instr["args"][0]))
            self._data_path.pass_alu_in()
            self._data_path.select_add()
            self._data_path.execute_alu()
            self._data_path.latch_register(4)
            self.tick()

        elif opcode is Opcode.BE:
            assert len(instr["args"]) == 1, "bad instruction"
            self.tick()
            if self._data_path.zero_flag():
                self._data_path.select_registers(-1, -1)
                self._data_path.bus1_mux_signal_instr(np.int32(instr["args"][0]))
                self._data_path.pass_alu_in()
                self._data_path.select_add()
                self._data_path.execute_alu()
                self._data_path.latch_register(4)
                self.tick()

        elif opcode is Opcode.BNE:
            assert len(instr["args"]) == 1, "bad instruction"
            self.tick()
            if not(self._data_path.zero_flag()):
                self._data_path.select_registers(-1, -1)
                self._data_path.bus1_mux_signal_instr(np.int32(instr["args"][0]))
                self._data_path.pass_alu_in()
                self._data_path.select_add()
                self._data_path.execute_alu()
                self._data_path.latch_register(4)
                self.tick()

        elif opcode is Opcode.ADD:
            assert len(instr["args"]) == 3, "bad instruction"
            self._data_path.select_registers(instr["args"][0], instr["args"][1])
            self._data_path.bus1_mux_signal_bus()
            self._data_path.pass_alu_in()
            self._data_path.select_add()
            self._data_path.execute_alu()
            self._data_path.latch_register(instr["args"][2])
            self.tick()

        elif opcode is Opcode.SUB:
            assert len(instr["args"]) == 3, "bad instruction"
            self._data_path.select_registers(instr["args"][0], instr["args"][1])
            self._data_path.bus1_mux_signal_bus()
            self._data_path.negate_alu_in2()
            self._data_path.select_add()
            self._data_path.execute_alu()
            self._data_path.latch_register(instr["args"][2])
            self.tick()

        elif opcode is Opcode.MOD:
            assert len(instr["args"]) == 3, "bad instruction"
            self._data_path.select_registers(instr["args"][0], instr["args"][1])
            self._data_path.bus1_mux_signal_bus()
            self._data_path.pass_alu_in()
            self._data_path.select_mod()
            self._data_path.execute_alu()
            self._data_path.latch_register(instr["args"][2])
            self.tick()

        elif opcode is Opcode.INC:
            assert len(instr["args"]) == 2, "bad instruction"
            self._data_path.select_registers(instr["args"][0], -1)
            self._data_path.bus1_mux_signal_bus()
            self._data_path.inc_alu_in1()
            self._data_path.select_add()
            self._data_path.execute_alu()
            self._data_path.latch_register(instr["args"][1])
            self.tick()

        elif opcode is Opcode.DEC:
            assert len(instr["args"]) == 2, "bad instruction"
            self._data_path.select_registers(instr["args"][0], -1)
            self._data_path.bus1_mux_signal_bus()
            self._data_path.dec_alu_in1()
            self._data_path.select_add()
            self._data_path.execute_alu()
            self._data_path.latch_register(instr["args"][1])
            self.tick()

        elif opcode is Opcode.MV:
            assert len(instr["args"]) == 2, "bad instruction"
            self._data_path.select_registers(instr["args"][0], -1)
            self._data_path.bus1_mux_signal_bus()
            self._data_path.pass_alu_in()
            self._data_path.select_add()
            self._data_path.execute_alu()
            self._data_path.latch_register(instr["args"][1])
            self.tick()

        elif opcode is Opcode.LD:
            assert len(instr["args"]) == 2, "bad instruction"
            self._data_path.select_registers(-1, -1)
            self._data_path.bus1_mux_signal_instr(np.int32(instr["args"][0]))
            self._data_path.pass_alu_in()
            self._data_path.select_add()
            self._data_path.execute_alu()
            self._data_path.read()
            self._data_path.latch_register(instr["args"][1])
            self.tick()

        elif opcode is Opcode.ST:
            assert len(instr["args"]) == 2, "bad instruction"
            self._data_path.select_registers(-1, -1)
            self._data_path.bus1_mux_signal_instr(np.int32(instr["args"][1]))
            self._data_path.pass_alu_in()
            self._data_path.select_add()
            self._data_path.execute_alu()
            self._data_path.select_registers(-1, instr["args"][0])
            self._data_path.wr()
            self.tick()

        else:
            assert False, "bad instruction"

    def __repr__(self):
        state = "{{TICK: {}, R4(PC): {}, R0: {}, R1: {}, R2: {}, R3: {}}}".format(
            self._tick,
            self._data_path.registers[-1],
            self._data_path.registers[0],
            self._data_path.registers[1],
            self._data_path.registers[2],
            self._data_path.registers[3]
        )

        instr = self._data_path.memory[self._data_path.registers[-1]]

        return "{} {}".format(state, instr)


def simulation(code, memory_size, limit) -> Tuple[int, int]:
    data_path = DataPath(code, memory_size)
    control_unit = ControlUnit(data_path)
    instr_counter = 0

    logging.debug('%s', control_unit)
    try:
        while True:
            assert limit > instr_counter, "too long execution, increase limit!"
            control_unit.decode_and_execute_instruction(control_unit.fetch_instruction())
            instr_counter += 1
            logging.debug('%s', control_unit)
    except StopIteration:
        pass
    return instr_counter, control_unit.current_tick()


def main(args):
    assert len(args) == 1, "Wrong arguments: machine.py <code_file>"
    code_file = args[0]
    code = read_code(code_file)

    mem_size = 512
    assert len(code) < mem_size, "Not enough memory!"
    code = code + [ZERO] * (mem_size - len(code))

    instr_counter, ticks = simulation(code, mem_size, 30000)

    print("instr_counter: {}, ticks: {}".format(instr_counter, ticks))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])

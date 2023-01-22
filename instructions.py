class Instruction:

    def __init__(self, opcode: str, args_count: int = 0, arg1: int = 0, arg2: int = 0):
        self.opcode = opcode
        self.args_count = args_count
        self.arg1 = arg1
        self.arg2 = arg2


class ErrorInstruction(Instruction):
    def __init__(self):
        super().__init__('err')


class PassInstruction(Instruction):
    def __init__(self):
        super().__init__('pass')


class LoadInstruction(Instruction):
    def __init__(self, mem_cell: int, reg: int):
        super().__init__('ld', 2, mem_cell, reg)


class SaveInstruction(Instruction):
    def __init__(self, reg: int, mem_cell: int):
        super().__init__('sv', 2, reg, mem_cell)


class AddInstruction(Instruction):
    def __init__(self, reg1: int, reg2: int):
        super().__init__('add', 2, reg1, reg2)


class SubInstruction(Instruction):
    def __init__(self, reg1: int, reg2: int):
        super().__init__('sub', 2, reg1, reg2)


class MulInstruction(Instruction):
    def __init__(self, reg1: int, reg2: int):
        super().__init__('mul', 2, reg1, reg2)


class DivInstruction(Instruction):
    def __init__(self, reg1: int, reg2: int):
        super().__init__('div', 2, reg1, reg2)


class IncInstruction(Instruction):
    def __init__(self, reg: int):
        super().__init__('inc', 1, reg)


class CompareInstruction(Instruction):
    def __init__(self, reg1: int, reg2: int):
        super().__init__('cmp', 2, reg1, reg2)


class JumpInstruction(Instruction):
    def __init__(self, mem_cell: int):
        super().__init__('jmp', 1, mem_cell)


class JumpEqualsInstruction(Instruction):
    def __init__(self, mem_cell: int):
        super().__init__('je', 1, mem_cell)


class JumpGreaterInstruction(Instruction):
    def __init__(self, mem_cell: int):
        super().__init__('jg', 1, mem_cell)


class JumpLowerInstruction(Instruction):
    def __init__(self, mem_cell: int):
        super().__init__('jl', 1, mem_cell)
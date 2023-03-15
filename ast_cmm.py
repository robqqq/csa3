

from collections import OrderedDict
from isa import Cell, Opcode
import logging


REG_COUNT = 4

class TranslateState:
    def __init__(self):
        self.text: list[Cell] = []
        self.vars: OrderedDict[str, int] = {}
        self.labels: list[int] = []
        self.pc = 0
        
    def reset_program(self):
        self.text = list(Cell)
        
    def add_var(self, name, value):
        self.vars[name] = value
        
    def get_var_addr(self, name):
        assert name in self.vars, "variable %s does not exist" % name
        return  list(self.vars.keys()).index(name) + len(self.text)
    
    def link(self):
        self.text.append({"opcode": Opcode.HLT})
        text_len = len(self.text)
        for instr in self.text:
            if instr["opcode"] == Opcode.BE or instr["opcode"] == Opcode.BNE or instr["opcode"] == Opcode.JMP:
                instr["args"][0] = self.labels[int(instr["args"][0])]
            elif instr["opcode"] == Opcode.HLT:
                pass
            else:
                for i, name in enumerate(instr["args"]):
                    if isinstance(name, str):
                        instr["args"][i] = self.get_var_addr(name)
        
        for var in self.vars.values():
            self.text.append(var)
            

def translate(ast):
    state: TranslateState = TranslateState()
    ast.eval(state)
    print(state.vars)
    print(state.labels)
    state.link()
    return state.text


class Equality:
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    
class Aexp(Equality):
    pass


class IntAexp(Aexp):
    def __init__(self, i):
        self.i = i
        
    def __repr__(self):
        return 'IntAexp(%d)' % self.i
    
    def eval(self, state):
        return self.i

    
    
class VarAexp(Aexp):
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return 'VarAexp(%s)' % self.name
    
    def eval(self, state: TranslateState, reg: int):
        assert self.name in state.vars, "Error, var %s is not declared" % self.name
        state.text.append({"opcode": Opcode.LD, "args": [self.name, reg]})
        state.pc += 1
        
    

class BinopAexp(Aexp):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
        
    def __repr__(self):
        return 'BinopAexp(%s, %s, %s)' % (self.op, self.left, self.right)
    
    def eval(self, state: TranslateState, reg: int):
        if isinstance(self.left, IntAexp):
            if str(self.left.eval(state)) not in state.vars:
                state.add_var(str(self.left.eval(state)), self.left.eval(state))
            state.text.append({"opcode": Opcode.LD, "args": [str(self.left.eval(state)), 1]})
            state.pc += 1
        else:
            self.left.eval(state, 1)
        if isinstance(self.right, IntAexp):
            if str(self.right.eval(state)) not in state.vars:
                state.add_var(str(self.right.eval(state)), self.right.eval(state))
            state.text.append({"opcode": Opcode.LD, "args": [str(self.right.eval(state)), 2]})
            state.pc += 1    
        else:
            self.right.eval(state, 2)
        if (self.op == '+'):
            state.text.append({"opcode": Opcode.ADD, "args": [1, 2, reg]})
        elif (self.op == '-'):
            state.text.append({"opcode": Opcode.SUB, "args": [1, 2, reg]})
        elif (self.op == '%'):
            state.text.append({"opcode": Opcode.MOD, "args": [1, 2, reg]})
        state.pc += 1
    
    
class Bexp(Equality):
    pass


class RelopBexp(Bexp):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
        
    def __repr__(self):
        return 'RelopBexp(%s, %s, %s)' % (self.op, self.left, self.right)
    
    def eval(self, state: TranslateState):
        if isinstance(self.left, IntAexp):
            if str(self.left.eval(state)) not in state.vars:
                state.add_var(str(self.left.eval(state)), self.left.eval(state))
            state.text.append({"opcode": Opcode.LD, "args": [str(self.left.eval(state)), 1]})
            state.pc += 1
        else:
            self.left.eval(state, 1)   
        if isinstance(self.right, IntAexp):
            if str(self.right.eval(state)) not in state.vars:
                state.add_var(str(self.right.eval(state)), self.right.eval(state))
            state.text.append({"opcode": Opcode.LD, "args": [str(self.right.eval(state)), 2]})
            state.pc += 1    
        else:
            self.right.eval(state, 2)
        state.text.append({"opcode": Opcode.SUB, "args": [1, 2, 0]})
        state.pc += 1
        return self.op == "=="
    
    
    
    
class Statement(Equality):
    pass


class AssignStatement(Statement):
    def __init__(self, name, aexp):
        self.name = name
        self.aexp = aexp
        
    def __repr__(self) -> str:
        return 'AssignStatement(%s, %s)' % (self.name, self.aexp)
    
    def eval(self, state: TranslateState):
        if self.name in state.vars:
            if isinstance(self.aexp, IntAexp):
                if str(self.aexp.eval(state)) not in state.vars:
                    state.add_var(str(self.aexp.eval(state)), self.aexp.eval(state))
                state.text.append({"opcode": Opcode.LD, "args": [str(self.aexp.eval(state)), 0]})
                state.text.append({"opcode": Opcode.ST, "args": [0, self.name]})
                state.pc += 2
            else:
                self.aexp.eval(state, 0)
                state.text.append({"opcode": Opcode.ST, "args": [0, self.name]})
                state.pc += 1
        else:
            if isinstance(self.aexp, IntAexp):
                state.add_var(self.name, self.aexp.eval(state))
            else:
                state.add_var(self.name, 0)
                self.aexp.eval(state, 0)
                state.text.append({"opcode": Opcode.ST, "args": [0, self.name]})
                state.pc += 1
            
    
class CompoundStatement(Statement):
    def __init__(self, first, second) -> None:
        self.first = first
        self.second = second
        
    def __repr__(self) -> str:
        return 'CompoundStatement(%s, %s)' % (self.first, self.second)
    
    def eval(self, state: TranslateState):
        self.first.eval(state)
        self.second.eval(state)
    
    
class IfStatement(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        
    def __repr__(self) -> str:
        return 'IfStatement(%s, %s)' % (self.condition, self.body)
    
    def eval(self, state: TranslateState):
        condition = self.condition.eval(state)
        if_num = len(state.labels)
        state.labels.append(-1)
        if condition:
            opcode = Opcode.BNE
        else:
            opcode = Opcode.BE
        state.text.append({"opcode": opcode, "args": [str(if_num)]})
        state.pc += 1
        self.body.eval(state)
        state.labels[if_num] = state.pc
    
    
class WhileStatement(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        
    def __repr__(self) -> str:
        return 'WhileStatement(%s, %s)' % (self.condition, self.body)
    
    def eval(self, state: TranslateState):
        cond_pc = state.pc
        cond = self.condition.eval(state)
        while_num = len(state.labels)
        state.labels.append(-1)
        state.labels.append(cond_pc)
        if cond:
            opcode = Opcode.BNE
        else:
            opcode = Opcode.BE
        state.text.append({"opcode": opcode, "args": [str(while_num)]})
        state.pc += 1
        self.body.eval(state)
        state.text.append({"opcode": Opcode.JMP, "args": [str(while_num + 1)]})
        state.pc += 1
        state.labels[while_num] = state.pc
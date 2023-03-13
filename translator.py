import logging
import os
import re
import sys
from isa import Cell, Instr

class CellNode:
    data: Cell
    
    def __init__(self, data: Cell):
        self.data = data
        self.next = None
        self.prev = None
        
    def __repr__(self):
        return self.data


class ProgramLinkedList:
    def __init__(self):
        self.head = None

    def to_list(self) -> list [Cell]:
        node = self.head
        nodes = []
        while node is not None:
            nodes.append(node.data)
            node = node.next
        return nodes
    
    def push(self, cell: Cell):
        if self.head == None:
            self.head = CellNode(Cell)
        else:
            curr = self.head
            while (curr.next != None):
                curr = curr.next
            curr.next = CellNode(cell)
            curr.next.prev = curr
        
    def __repr__(self):
        return " -> ".join(self.to_list().append(None))


class Program:
    _args: dict [str, int]
    _text: ProgramLinkedList
    _labels: list [tuple [str, CellNode]]
    _if_counter: int
    _while_counter: int
    
    def __init__(self) -> None:
        self._args = {}
        self._text = ProgramLinkedList()
        self._if_counter = 0
        self._while_counter = 0
        
    def add_arg(self, name: str, val: int) -> None:
        self._args[name] = val
        
    def arg_declared(self, name: str) -> bool:
        return name in self._args
    
    def get_arg(self, name: str) -> int | str:
         return self._args[name]
     
    def add_if(self, jmp_instr: Instr):
        if self.head == None:
            pass #TODO: сделать
        
     
    
   
def translate_cmm_text(text: list[str]) -> Program:
    figure_brackets: int = 0
    prog: Program = Program()
    str_pattern = re.compile(r"^\".*\"$")
    has_digit_pattern = re.compile(r"\d+")
    
    for i, l in enumerate(text):
        if l.find("==") == -1 and l.find("=") != -1 and l.find("!=") == -1 and l.find("+=") == -1 and l.find("-=") == -1:
            assert l.strip()[-1] == ";", "expected ';', line {}".format(i + 1) 
            statement = l.split("=")
            assert len(statement) == 2, "wrong declaration in line {}".format(i + 1)
            left_list = statement[0].split()
            right_list = statement[1].rstrip()[:-1].split()
            assert len(left_list) == 1 or len(left_list) == 2, "wrong declaration in line {}".format(i + 1)
            assert len(right_list) == 1, "wrong declaration in line {}".format(i + 1)
            left = ""
            right = right_list[0]
            
            if len(left_list) == 2:
                assert left_list[0] == "int" or left_list[0] == "string", "{} is wrong type, line {}".format(left_list[0], i + 1)
                assert left_list[0] not in prog._args, "{} already has been declared, line {}".format(left_list[1], i + 1)
                left = left_list[1]
                typ = left_list[0]
                if typ == "int":
                    assert right.isdigit, "{} is not a int, line {}".format(right, i + 1)
                    prog.add_arg(left, int(right))
                else:
                    assert str_pattern.search(right) != None, "{} is not a string, line {}".format(i + 1)
                    prog.add_arg(left, right)
                
            # else: Это надо в трансляцию переприсваивания
                # assert left_list[0] in prog._args, "{} is not declared, line {}" + (left_list[0], i + 1)
                # left = left_list[0]
                # if isinstance(prog.get_arg(left), int):
                #     assert right.isdigit, "{} is not a int, line {}".format(right, i + 1)
                #     prog.add_arg(left, int(right))
                # else:
                #     assert str_pattern.search(right) != None, "{} is not a string, line {}".format(right, i + 1)
                #     prog.add_arg(left, right)
        elif (has_digit_pattern.search(l) != None):
            consts = has_digit_pattern.findall(l)
            for c in consts:
                prog.add_arg(c, int(c))
        
        for c in l:
            if c == '{':
                figure_brackets += 1
            elif c == '}':
                figure_brackets -= 1
            assert figure_brackets >= 0, "found '}' in line" + (i + 1)
    assert figure_brackets == 0, "wrong figure brackets"
    for i, l in enumerate(text):
        if l.find("==") == -1 and l.find("=") != -1 and l.find("!=") == -1 and l.find("+=") == -1 and l.find("-=") == -1:
            pass
        elif 
    
    return prog


    
    
    
    
def main(args) -> None:
    assert len(args) == 1 or len(args) == 2, "Wrong arguments: translator.py <input_file_name> <(Optional) output_file_name>"
    cmm_re = re.compile(r"\.cmm$")
    input_file_name = args[0]
    assert cmm_re.search(input_file_name) != None, "Input file should be .cmm"
    assert os.path.exists(input_file_name), "Input file does not exists"
    output_file_name = input_file_name[:-3] + "json"
    if (len(args) == 2):
        output_file_name = args[1]
        
    input_text = ""
    with open(input_file_name, "rt") as input_file:
        input_text = input_file.read()
        
    prog = translate_cmm_text(input_text.split("\n"))
    pass
    
    

    
    
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
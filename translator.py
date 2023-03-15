from lexer import lex
import logging
import os
import re
import sys
import json

from parser_cmm import parse_cmm
import ast_cmm



def main(args) -> None:
    assert len(args) == 1 or len(args) == 2, "Wrong arguments: translator.py <input_file_name> <(Optional) output_file_name>"
    cmm_re = re.compile(r"\.cmm$")
    input_file_name = args[0]
    assert cmm_re.search(input_file_name) != None, "Input file should be .cmm"
    assert os.path.exists(input_file_name), "Input file does not exists"
    output_file_name = input_file_name[:-3] + "json"
    if (len(args) == 2):
        output_file_name = args[1]
        
    with open(input_file_name, "rt") as input_file:
        input_text = input_file.read()
    tokens = lex(input_text)
    for token in tokens:
        print(token)
    result = parse_cmm(tokens)
    print(result.value)
    text = ast_cmm.translate(result.value)
    
    with open(output_file_name, "wt") as output_file:
        output_file.write(json.dumps(text, indent=4))
    
    
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
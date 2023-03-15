import re
import sys
import logging

RESERVED = 'RESERVED'
INT = 'INT'
ID = 'ID'
STRING = 'STRING'

token_exprs = [
    (re.compile(r'\s+'), None),
    (re.compile(r'//.*\n'), None),
    (re.compile(r'=='), RESERVED),
    (re.compile(r'\('), RESERVED),
    (re.compile(r'\)'), RESERVED),
    (re.compile(r';'), RESERVED),
    (re.compile(r'\+='), RESERVED),
    (re.compile(r'-='), RESERVED),
    (re.compile(r'\+\+'), RESERVED),
    (re.compile(r'--'), RESERVED),
    (re.compile(r'\+'), RESERVED),
    (re.compile(r'-'), RESERVED),
    (re.compile(r'%'), RESERVED),
    (re.compile(r'!='), RESERVED),
    (re.compile(r'='), RESERVED),
    (re.compile(r'if'), RESERVED),
    (re.compile(r'while'), RESERVED),
    (re.compile(r'print'), RESERVED),
    (re.compile(r'scan'), RESERVED),
    (re.compile(r'{'), RESERVED),
    (re.compile(r'}'), RESERVED),
    (re.compile(r'int'), RESERVED),
    (re.compile(r'string'), RESERVED),
    (re.compile(r'\d+'), INT),
    (re.compile(r'[_a-zA-Z][_a-zA-Z\d]*'), ID),
    (re.compile(r'\".*\"'), STRING)
]

def lex(characters):
    characters += '\n'
    pos = 0
    tokens = []
    while pos < len(characters):
        match = None
        for token_expr in token_exprs:
            pattern, tag = token_expr
            char_pos = characters[pos:]
            match = pattern.match(characters, pos)
            if match:
                text = match.group(0)
                if tag:
                    token = (text, tag)
                    tokens.append(token)
                break
        assert match, "Illegal character: {}\n".format(characters[pos])
        pos = match.end(0)
    return tokens
            
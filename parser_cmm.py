from functools import reduce
from ast_cmm import AssignStatement, BinopAexp, CompoundStatement, IfStatement, IntAexp, RelopBexp, VarAexp, WhileStatement
from combinators import Exp, Lazy, Opt, Phrase, Reserved, Tag
from lexer import ID, INT, RESERVED


def keyword(kw):
    return Reserved(kw, RESERVED)

id = Tag(ID)
num = Tag(INT) ^ (lambda i: int(i))

def aexp_value():
    return (num ^ (lambda i: IntAexp(i))) | (id ^ (lambda v: VarAexp(v)))

def process_group(parsed):
    ((_, p), _) = parsed
    return p

def aexp_group():
    return keyword('(') + Lazy(aexp) + keyword(')') ^ process_group

def aexp_term():
    return aexp_value() | aexp_group()

def process_binop(op):
    return lambda l, r: BinopAexp(op, l, r)

def any_operator_in_list(ops):
    op_parsers = [keyword(op) for op in ops]
    parser = reduce(lambda l, r: l | r, op_parsers)
    return parser

aexp_precedence_levels = [
    ['%'],
    ['+', '-']
]

def precedence(value_parser, precedence_levels, combine):
    def op_parser(precedence_level):
        return any_operator_in_list(precedence_level) ^ combine
    parser = value_parser * op_parser(precedence_levels[0])
    for precedence_level in precedence_levels[1:]:
        parser = parser * op_parser(precedence_level)
    return parser

def aexp():
    return precedence(aexp_term(), aexp_precedence_levels, process_binop)


def process_relop(parsed):
    ((left, op), right) = parsed
    return RelopBexp(op, left, right)

def bexp():
    relops = ['==', '!=']
    return aexp() + any_operator_in_list(relops) + aexp() ^ process_relop

def assign_stmt():
    def process(parsed):
        ((name, _), exp) = parsed
        return AssignStatement(name, exp)
    return id + keyword('=') + aexp() ^ process

def stmt_list():
    separator = keyword(';') ^ (lambda x: lambda l, r: CompoundStatement(l, r))
    return Exp(stmt(), separator)

def if_stmt():
    def process(parsed):
        print(parsed)
        ((((_, condition), _), body), _) = parsed
        return IfStatement(condition, body)
    return keyword('if') + bexp() + keyword('{') + Lazy(stmt_list) + keyword('}') ^ process

def while_stmt():
    def process(parsed):
        ((((_, condition), _), body), _) = parsed
        return WhileStatement(condition, body)
    return keyword('while') + bexp() + keyword('{') + Lazy(stmt_list) + keyword('}') ^ process

def stmt():
    return assign_stmt() | if_stmt() | while_stmt()

def parser():
    return Phrase(stmt_list())

def parse_cmm(tokens):
    ast = parser()(tokens, 0)
    return ast
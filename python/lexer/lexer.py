import ply.lex as lex
import ply.yacc as yacc

# I have not made these do anything yet
# reserved = {
#     'else if': 'ELIF',
#     'if': 'IF',
#     'else': 'ELSE',
#     'while': 'WHILE',
#     'str': 'STRING',
#     'int': 'INTEGER',
#     'bool': 'BOOLEAN',
#     'list': 'LIST',
#     'arr': 'ARRAY',
#     'map': 'MAP',
#     'float': 'FLOAT',
#     'range': 'RANGE',
#     'len': 'LENGTH',
#     'for': 'FOR',
#     'ind': 'INDEX',
#     'in': 'IN',
#     'return': 'RETURN',
#     'assert': 'ASSERT',
#     'func': 'FUNC'
# }

tokens = [
    # Literals
    'NAME', 'INTEGER', 'FLOAT', 'STRING', 'NUMBER',

    # Operators
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'EXPON',
    'OR', 'AND',
    'EQUALS', 'TIMESEQ', 'DIVEQ', 'PLUSEQ', 'MINUSEQ',
    'INCREMENT', 'DECREMENT',

    # Comparison
    'EQUIV', 'LESS', 'LEQUALS', 'GREATER', 'GREQUALS', 'NOTEQUALS',

    # Delimeters
    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'LCURLY', 'RCURLY',
    'COMMA', 'PERIOD'
]


# tokens = ('COMMENT')

# Implementation of Tokens
# Enforcing camelCase...
t_NAME             = r'[a-z][a-zA-Z0-9_]*'
t_INTEGER = r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'
t_FLOAT = r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'
t_STRING           = r'\"([^\\\n]|(\\.))*?\"'

# Operators
t_PLUS             = r'\+'
t_MINUS            = r'-'
t_TIMES            = r'\*'
t_DIVIDE           = r'/'
t_MODULO           = r'%'
t_EXPON            = r'\^'
t_OR               = r'\|'
t_AND              = r'&'
t_EQUALS           = r':'
t_TIMESEQ          = r'\*:'
t_DIVEQ            = r'/:'
t_PLUSEQ           = r'\+:'
t_MINUSEQ          = r'-:'
t_INCREMENT        = r'\+\+'
t_DECREMENT        = r'--'


# Comparison
t_EQUIV            = r'='
t_LESS             = r'<'
t_LEQUALS          = r'<='
t_GREATER          = r'>'
t_GREQUALS         = r'>='
t_NOTEQUALS        = r'!='

# Delimiters
t_LPAREN           = r'\('
t_RPAREN           = r'\)'
t_LBRACKET         = r'\['
t_RBRACKET         = r'\]'
t_LCURLY           = r'\{'
t_RCURLY           = r'\}'
t_COMMA            = r','
t_PERIOD           = r'\.'


def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Line {}: Number {} is too large!".format(t.lineno, t.value))
        t.value = 0
    return t


def t_COMMENT(t):
    r'//.*\n'
    t.lexer.lineno += 1
    return t

# Ignore whitespace!
t_ignore = " \t\n"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '{}'".format(t.value[0]))
    t.lexer.skip(1)

lex.lex()

# Potentially need precedence for exponents?
precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
)

names = {}


# This is how we actually handle assignment...
def p_statement_assign(p):
    'statement : NAME EQUALS expression'
    names[p[1]] = p[3]


# Don't totally understand what this does.
def p_statement_expr(p):
    'statement : expression'
    print(p[1])


def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MODULO expression
                  | expression EXPON expression
                  | expression NOTEQUALS expression
                  | expression EQUIV expression"""
    if p[2] == '+'  : p[0] = p[1] + p[3]
    elif p[2] == '-': p[0] = p[1] - p[3]
    elif p[2] == '*': p[0] = p[1] * p[3]
    elif p[2] == '/': p[0] = p[1] / p[3]
    elif p[2] == '%': p[0] = p[1] % p[3]
    elif p[2] == '^': p[0] = p[1] ** p[3]
    elif p[2] == '!=': p[0] = True if p[1] != p[3] else False
    elif p[2] == '=': p[0] = True if p[1] == p[3] else False


def p_expression_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = -p[2]


def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]


# Read more about this method... What makes names an iterable?
def p_expression_name(p):
    'expression : NAME'
    try:
        p[0] = names[p[1]]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0


def p_error(p):
    print("Syntax error at '%s'" % p.value)


def p_empty(p):
    'empty :'
    pass

yacc.yacc()

cont = True
while cont:
    try:
        s = input(">>> ")
    except EOFError:
        break
    if not s: continue
    result = yacc.parse(s)
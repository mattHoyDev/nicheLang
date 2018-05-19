# I have not made these do anything yet
reserved = {
    'else if': 'ELIF',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'str': 'STRING',
    'int': 'INTEGER',
    'bool': 'BOOLEAN',
    'list': 'LIST',
    'arr': 'ARRAY',
    'map': 'MAP',
    'float': 'FLOAT',
    'range': 'RANGE',
    'len': 'LENGTH',
    'for': 'FOR',
    'ind': 'INDEX',
    'in': 'IN',
    'return': 'RETURN',
    'assert': 'ASSERT',
    'func': 'FUNC'
}

tokens = [
    # Literals
    'NAME', 'INTEGER', 'FLOAT', 'STRING',

    # Operators
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'EXPON'
    'OR', 'AND'
    'EQUALS', 'TIMESEQ', 'DIVEQ', 'PLUSEQ', 'MINUSEQ',
    'INCREMENT', 'DECREMENT',

    # Comparison
    'EQUIV', 'LESS', 'LEQUALS', 'GREATER', 'GREQUALS', 'NOTEQUALS'

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
t_STRING = r'\"([^\\\n]|(\\.))*?\"'

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
t_TIMESEQ          = r'*:'
t_DIVEQ            = r'/:'
t_PLUSEQ           = r'+:'
t_MINUSEQ          = r'-:'
t_INCREMENT        = r'++'
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
t_LBRACE           = r'\{'
t_RBRACE           = r'\}'
t_COMMA            = r','
t_PERIOD           = r'\.'

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


# Potentially need precedence for exponents?
# precedence = (
#     ('left','PLUS','MINUS'),
#     ('left','TIMES','DIVIDE'),
#     ('right','UMINUS'),
# )
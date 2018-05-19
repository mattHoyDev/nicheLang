from collections import namedtuple
from enum import Enum

# Each token is a tuple of kind and value. Kind is one of the enumeration values
# in TokenKind. Value is the textual value of the token in that input.

class TokenKind(Enum):
    EOF = -1
    FUNC = -2
    IMPORT = -3
    IDENTIFIER = -4
    DOUBLE = -5
    OPERATOR = -6


# Token() will be used throughout to esablish the exact token pattern of
# all the tokens/reserved keywords
Token = namedtuple('Token', 'kind value')


#########
# LEXER #
#########

class Lexer(object):
    """
    Initialize the lexer with a string buffer. tokens() returns a generator
    that can be queried for tokens. The generator will emit an EOF token
    before stopping.
    """

    def __init__(self, buf):
        assert len(buf) >= 1
        self.buf = buf
        self.pos = 0
        self.lastChar = self.buf[0]

    def tokens(self):
        # While there is a last character
        while self.lastChar:

            # Skip whitespace
            while self.lastChar.isspace():
                self._advance()

            # If the string buffer begins with an alphabetical char...
            if self.lastChar.isalpha():
                id_str = ''

                # While lastChar is alphanumeric...
                while self.lastChar.isalnum():
                    # Advance lastChar until the id_str is complete
                    id_str += self.lastChar
                    self._advance()

                if id_str == 'func':
                    yield Token(kind=TokenKind.FUNC, value=id_str)
                elif id_str == 'import':
                    yield Token(kind=TokenKind.IMPORT, value=id_str)
                else:
                    yield Token(kind=TokenKind.IDENTIFIER, value=id_str)

            # else if the string buffer begins with a numeric or period...
            elif self.lastChar.isdigit() or self.lastChar == '.':
                num_str = ''

                # While lastChar is numeric...
                while self.lastChar.isdigit() or self.lastChar == '.':
                    # Advance lastChar until the num_str is complete
                    num_str += self.lastChar
                    self._advance()

                yield Token(kind=TokenKind.DOUBLE, value=num_str)

            # else if the string buffer is a comment
            elif self.lastChar == '/' and self._getChar() == '/':
                self._advance()
                while self.lastChar and self.lastChar not in ['\r', '\n']:
                    self._advance()

            # else if the string buffer is some other thing
            elif self.lastChar:
                yield Token(kind=TokenKind.OPERATOR, value=self.lastChar)
                self._advance()
        yield Token(kind=TokenKind.EOF, value='')

    def _advance(self):
        try:
            self.pos += 1
            self.lastChar = self.buf[self.pos]
        except IndexError:
            self.lastChar = ''

    def _getChar(self):
        try:
            return self.buf[self.pos+1]
        except IndexError:
            return ''


# AST Hierarchy
class ASTNode(object):
    def dump(self, indent=0):
        raise NotImplementedError


class ExprAST(ASTNode):
    # Eventually this will need a type field
    pass


class DoubleExprAST(ExprAST):
    def __init__(self, val):
        self.val = val

    def dump(self, indent=0):
        return '{0}{1}[{2}]'.format(
            ' ' * indent, self.__class__.__name__, self.val)


class VariableExprAST(ExprAST):
    def __init__(self, name):
        self.name = name

    def dump(self, indent=0):
        return '{0}{1}[{2}]'.format(
            ' ' * indent, self.__class__.__name__, self.name)


class BinaryExprAST:
    def __init__(self, op, lhs, rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def dump(self, indent=0):
        s = '{0}{1}[{2}]\n'.format(
            ' ' * indent, self.__class__.__name__, self.op)
        s += self.lhs.dump(indent + 2) + '\n'
        s += self.rhs.dump(indent + 2)
        return s


class CallExprAST(ExprAST):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

        def dump(self, indent=0):
            s = '{0}{1}[{2}]\n'.format(
                ' ' * indent, self.__class__.__name__, self.callee)
            for arg in self.args:
                s += arg.dump(indent + 2) + '\n'
            return s[:-1]  # snip out trailing '\n'


class PrototypeAST(ASTNode):
    def __init__(self, name, argNames):
        self.name = name
        self.argNames = argNames

    def dum(self, indent=0):
        return '{0}{1}[{2}]'.format(
            ' ' * indent, self.__class__.__name__, ', '.join(self.argNames))


class FunctionAST(ASTNode):
    def __init__(self, proto, body):
        self.proto = proto
        self.body = body

    def dump(self, indent=0):
        s = '{0}{1}[{2}]\n'.format(
            ' ' * indent, self.__class__.__name__, self.proto.dump())
        s += self.body.dump(indent + 2) + '\n'
        return s


class ParseError(Exception): pass


##########
# PARSER #
##########

class Parser(object):
    """
    After the parser is created, invoke parse_toplevel multiple times to parse
    Kaleidoscope source into an AST.
    """
    def __init__(self):
        self.tokenGenerator = None
        self.currentToken = None

    _precedenceMap = {'<': 10, '+': 20, '-': 20, '*': 40}

    # topLevel ::= definition | external | expression | ';'
    def parseTopLevel(self, buf):
        """Given a string, returns an AST node representing it."""
        self.tokenGenerator = Lexer(buf).tokens()
        self.currentToken = None
        self._getNextToken()

        if self.currentToken.kind == TokenKind.IMPORT:
            return self._parseImport()
        elif self.currentToken.kind == TokenKind.FUNC:
            return self._parseFunction()
        elif self._currentTokenIsOperator(';'):
            self._getNextToken()
            return None
        else:
            return self._parseTopLevelExpression()

    def _getNextToken(self):
        self.currentToken = next(self.tokenGenerator)

    def _parseImport(self):
        self._getNextToken()  # consume 'import'
        return self._parsePrototype()

    def _parseFunction(self):
        self._getNextToken()  # consume 'func'
        proto = self._parsePrototype()
        expr = self._parseExpression()
        return FunctionAST(proto, expr)

    def _currentTokenIsOperator(self, op):
        """Query whether the current token is the operator op"""
        return (self.currentToken.kind == TokenKind.OPERATOR and
                self.currentToken.value == op)

    def _parseTopLevelExpression(self):
        expr = self._parseExpression()
        return FunctionAST(PrototypeAST('', []), expr)

    def _parsePrototype(self):
        name = self.currentToken.value
        self._match(TokenKind.IDENTIFIER)
        self._match(TokenKind.OPERATOR, '(')
        argNames = []
        while self.currentToken.kind == TokenKind.IDENTIFIER:
            argNames.append(self.currentToken.value)
            self._getNextToken()
        self._match(TokenKind.OPERATOR, ')')
        return PrototypeAST(name, argNames)

    def _parseExpression(self):
        lhs = self._parsePrimary()
        # Start with precedence 0 because we want to bind any operator to the
        # expression at this point.
        return self._parseBinopRhs(0, lhs)

    def _match(self, expectedKind, expectedValue=None):
        """
        Consume the current token' verify that it's of the expected kind.
        If expectedKind == TokenKind.OPERATOR, verify the operator's value.
        """
        if (expectedKind == TokenKind.OPERATOR and
            not self._currentTokenIsOperator(expectedValue)):
            raise ParseError('Expected "{0}"'.format(expectedValue))
        elif expectedKind != self.currentToken.kind:
            raise ParseError('Expected "{0}"'.format(expectedKind))
        self._getNextToken()

    def _parsePrimary(self):
        if self.currentToken.kind == TokenKind.IDENTIFIER:
            return self._parseIdentifierExpression()
        elif self.currentToken.kind == TokenKind.DOUBLE:
            return self._parseDoubleExpression()
        elif self._currentTokenIsOperator('('):
            return self._parseParentheticalExpression()
        else:
            raise ParseError('Unknown token when expecting an expression.')

    def _parseBinopRhs(self, expressionPrecedence, lhs):
        """
        Parse the right-hand-side of a binary expression.

        expressionPrecedence: minimal precedence to keep going (precedence climbing).
        lhs: AST of the left-hand-side.
        """
        while True:
            currentPrecedence = self._currentTokenPrecedence()
            # If this is a binary operator with precedence lower than the
            # currently parsed sub-expression, bail out. If it binds at least
            # as tightly, keep going.
            # Note that the precedence of non-operators is defined to be -1,
            # so this condition handles cases when the expression ended.
            if currentPrecedence < expressionPrecedence:
                return lhs
            op = self.currentToken.value
            self._getNextToken()  # consume the operator
            rhs = self._parsePrimary()

            nextPrecedence = self._currentTokenPrecedence()

            # There are three options:
            # 1. nextPrecedence > currentPrecedence: we need to make a recursive call
            # 2. nextPrecedence == currentPrecedence: no need for a recursive call, the next
            #    iteration of this loop will handle it.
            # 3. nextPrecedence < currentPrecedence: no need for a recursive call, combine
            #    lhs and the next iteration will immediately bail out.
            if currentPrecedence < nextPrecedence:
                rhs = self._parseBinopRhs(currentPrecedence + 1, rhs)

            # Merge lhs/rhs
            lhs = BinaryExprAST(op, lhs, rhs)

    # identifierExpression
    #   ::= identifier
    #   ::= identifier '(' expression* ')'
    def _parseIdentifierExpression(self):
        idName = self.currentToken.value
        self._getNextToken()
        # If followed by a '(' it's a call; otherwise, a simple variable ref.
        if not self._currentTokenIsOperator('('):
            return VariableExprAST(idName)

        self._getNextToken()
        args = []
        if not self._currentTokenIsOperator(')'):
            while True:
                args.append(self._parseExpression())
                if self._currentTokenIsOperator(')'):
                    break
                self._match(TokenKind.OPERATOR, ',')

        self._getNextToken() # consume the ')'
        return CallExprAST(idName, args)

    # doubleExpression ::= double
    def _parseDoubleExpression(self):
        result = DoubleExprAST(self.currentToken.value)
        self._getNextToken()  # consume the double
        return result

    # parentheticalExpression ::= '(' expression ')'
    def _parseParentheticalExpression(self):
        self._getNextToken()  # consume the '('
        expr = self._parseExpression()
        self._match(TokenKind.OPERATOR, ')')
        return expr

    def _currentTokenPrecedence(self):
        """Get the operator precedence of the current token."""
        try:
            return Parser._precedenceMap[self.currentToken.value]
        except KeyError:
            return -1

if __name__ == '__main__':
    p = Parser()
    print(p.parseTopLevel('func doTheThing(a b) a + b').dump())

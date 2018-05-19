import unittest
from lexParse import (Lexer, Token, TokenKind, DoubleExprAST, VariableExprAST, BinaryExprAST,
                      CallExprAST, PrototypeAST, FunctionAST, Parser)


class LexerTests(unittest.TestCase):
    def _assertTokens(self, tokens, kinds):
        """Assert that the list of tokens has the given kinds"""
        self.assertEqual([t.kind.name for t in tokens], kinds)

    def testLexerSimpleTokensAndValues(self):
        l = Lexer('a+1')
        tokens = list(l.tokens())
        self.assertEqual(tokens[0], Token(TokenKind.IDENTIFIER, 'a'))
        self.assertEqual(tokens[1], Token(TokenKind.OPERATOR, '+'))
        self.assertEqual(tokens[2], Token(TokenKind.DOUBLE, '1'))
        self.assertEqual(tokens[3], Token(TokenKind.EOF, ''))

    def testTokenKinds(self):
        l = Lexer('10.1 func der import foo (')
        self._assertTokens(
            list(l.tokens()),
            ['DOUBLE', 'FUNC', 'IDENTIFIER', 'IMPORT',
             'IDENTIFIER', 'OPERATOR', 'EOF']
        )

        l = Lexer('+- 1 2 22 22.4 a b2 c3d')
        self._assertTokens(
            list(l.tokens()),
            ['OPERATOR', 'OPERATOR', 'DOUBLE', 'DOUBLE',
             'DOUBLE', 'DOUBLE', 'IDENTIFIER', 'IDENTIFIER',
             'IDENTIFIER', 'EOF']
        )

    def testSkipWhitespaceComments(self):
        l = Lexer('''
        func foo // this is a comment
        // another comment
        \t \t \t10
        ''')

        self._assertTokens(
            list(l.tokens()),
            ['FUNC', 'IDENTIFIER', 'DOUBLE', 'EOF']
        )


class ParserTests(unittest.TestCase):
    def _flatten(self, ast):
        """Test helper - flattens the AST into a sexpr-like nested list"""
        if isinstance(ast, DoubleExprAST):
            return ['Double', ast.val]
        elif isinstance(ast, VariableExprAST):
            return ['Variable', ast.name]
        elif isinstance(ast, BinaryExprAST):
            return ['Binop', ast.op,
                    self._flatten(ast.lhs), self._flatten(ast.rhs)]
        elif isinstance(ast, CallExprAST):
            args = [self._flatten(arg) for arg in ast.args]
            return ['Call', ast.callee, args]
        elif isinstance(ast, PrototypeAST):
            return ['Proto', ast.name, ' '.join(ast.argNames)]
        elif isinstance(ast, FunctionAST):
            return ['Function',
                    self._flatten(ast.proto), self._flatten(ast.body)]
        else:
            raise TypeError('unknown type in _flatten: {0}'.format(type(ast)))

    def _assertBody(self, topLevel, expected):
        """Assert the flattened body of the given topLevel function"""
        self.assertIsInstance(topLevel, FunctionAST)
        self.assertEqual(self._flatten(topLevel.body), expected)

    def testBasic(self):
        ast = Parser().parseTopLevel('2')
        self.assertIsInstance(ast, FunctionAST)
        self.assertIsInstance(ast.body, DoubleExprAST)
        self.assertEqual(ast.body.val, '2')

    def testBasicWithFlattening(self):
        ast = Parser().parseTopLevel('2')
        self._assertBody(ast, ['Double', '2'])
        ast = Parser().parseTopLevel('foobar')
        self._assertBody(ast, ['Variable', 'foobar'])

    def testExpressionSinglePrecedent(self):
        ast = Parser().parseTopLevel('2 + 3 - 4')
        self._assertBody(ast,
                         ['Binop',
                          '-', ['Binop', '+', ['Double', '2'], ['Double', '3']],
                          ['Double', '4']])

    def testExpressionMultiplicationPrecedence(self):
        ast = Parser().parseTopLevel('2+3*4-9')
        self._assertBody(ast,
                         ['Binop', '-',
                          ['Binop', '+',
                           ['Double', '2'],
                           ['Binop', '*', ['Double', '3'], ['Double', '4']]],
                          ['Double', '9']])

    def testExpressionParentheses(self):
        ast = Parser().parseTopLevel('2*(3-4)*7')
        self._assertBody(ast,
                         ['Binop', '*',
                          ['Binop', '*',
                           ['Double', '2'],
                           ['Binop', '-', ['Double', '3'], ['Double', '4']]],
                          ['Double', '7']])

    def testImports(self):
        ast = Parser().parseTopLevel('import sin(arg)')
        self.assertEqual(self._flatten(ast), ['Proto', 'sin', 'arg'])
        ast = Parser().parseTopLevel('import Foobar(nom denom abom)')
        self.assertEqual(self._flatten(ast),
                         ['Proto', 'Foobar', 'nom denom abom'])

    def testFunctionDefinition(self):
        ast = Parser().parseTopLevel('func foo(x) 1 + bar(x)')
        self.assertEqual(self._flatten(ast),
                         ['Function', ['Proto', 'foo', 'x'],
                          ['Binop', '+',
                           ['Double', '1'],
                           ['Call', 'bar', [['Variable', 'x']]]]])


if __name__ == '__main__':
    unittest.main()

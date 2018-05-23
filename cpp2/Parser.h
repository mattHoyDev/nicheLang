#include <map>
#include "Lexer.h"
#include "common.h"

#ifndef NICHE_LANG_CPP_PARSER_H
#define NICHE_LANG_CPP_PARSER_H


class Parser
{
public:
    Parser(Lexer lexer);
    Lexer lexer;
    int curTok;
    int getNextToken();
    int getTokPrecendence();
    void handleExternal();
    void handleDefinition();
    void handleTopLevelExpression();
    std::map<char, int> binopPrecedence;
    std::unique_ptr<ExprAST> logError(const char* e);
    std::unique_ptr<PrototypeAST> logErrorP(const char* e);
    std::unique_ptr<ExprAST> parseExpression();
    std::unique_ptr<ExprAST> parsePrimary();
    std::unique_ptr<ExprAST> parseBinOpRHS(int exprPrec, std::unique_ptr<ExprAST> LHS);
    std::unique_ptr<ExprAST> parseIdentifierExpr();
    std::unique_ptr<ExprAST> parseNumberExpr();
    std::unique_ptr<ExprAST> parseParenExpr();
    std::unique_ptr<PrototypeAST> parsePrototype();
    std::unique_ptr<FunctionAST> parseDefinition();
    std::unique_ptr<PrototypeAST> parseExternal();
    std::unique_ptr<FunctionAST> parseTopLevelExpr();
};


#endif //NICHE_LANG_CPP_PARSER_H

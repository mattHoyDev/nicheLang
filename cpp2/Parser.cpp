#include "Parser.h"
#include "common.h"

Parser::Parser(Lexer lexer)
{
    this->lexer = lexer;
    this->binopPrecedence['<'] = 10;
    this->binopPrecedence['+'] = 20;
    this->binopPrecedence['-'] = 20;
    this->binopPrecedence['*'] = 40;
}

int Parser::getNextToken()
{
    curTok = this->lexer.getToken();
}

std::unique_ptr<ExprAST> Parser::logError(const char* e)
{
    fprintf(stderr, "Error :%s\n", e);
    return nullptr;
}

std::unique_ptr<PrototypeAST> Parser::logErrorP(const char* e)
{
    this->logError(e);
    return nullptr;
}

int Parser::getTokPrecedence() {
    if (!isascii(this->curTok))
    {
        return -1;
    }
    int tokPrec = this->binopPrecedence[CurTok];
    if (tokPrec <= 0)
        return -1;
    return tokPrec;
}


void Parser::handleExternal()
{
    if (this->parseExternal())
    {
        fprintf(stderr, "Parsed an import\n");
    }
    else
    {
        this->getNextToken();
    }
}

void Parser::handleDefinition()
{
    if (this->parseDefinition())
    {
        fprintf(stderr, "Parsed a function definition.\n");
    }
    else
    {
        this->getNextToken();
    }
}

void Parser::handleTopLevelExpression()
{
    if (this->parseTopLevelExpr())
    {
        fprintf(stderr, "Parsed a top-level expr\n");
    }
    else
    {
        this->getNextToken();
    }
}

std::unique_ptr<ExprAST> Parser::parsePrimary() {
    switch (CurTok)
    {
        default:
            return LogError("unknown token when expecting an expression");
        case tok_identifier:
            return this.parseIdentifierExpr();
        case tok_number:
            return this->parseNumberExpr();
        case '(':
            return this->parseParenExpr();
    }
}

std::unique_ptr<ExprAST> Parser::parseBinOpRHS(int exprPrec, std::unique_ptr<ExprAST> LHS)
{
    while (true)
    {
        int tokPrec = this->getTokPrecendence();

        if (tokPrec < exprPrec)
        {
            return LHS;
        }

        int binOp = curTok;
        this->getNextToken();

        auto RHS = this->parsePrimary();
        if (!RHS)
        {
            return nullptr;
        }

        int nextPrec = this->getTokPrecendence();
        if (tokPrec < nextPrec)
        {
            RHS = this->parseBinOpRHS(tokPrec + 1, std::move(RHS));
            if (!RHS)
            {
                return nullptr;
            }
        }

        LHS = llvm::make_unique<BinaryExprAST>(binOp, std::move(LHS),
                                               std::move(RHS));
    }
}

std::unique_ptr<ExprAST> Parser::parseIdentifierExpr()
{
    std::string idName = this->lexer.identifierStr;

    this->getNextToken();

    if (this->curTok != '(')
    {
        return llvm::make_unique<VariableExprAST>(idName);
    }

    this->getNextToken();
    std::vector<std::unique_ptr<ExprAST>> args;
    if (this->curTok != ')')
    {
        while (true)
        {
            if (auto arg = this->parseExpression())
            {
                args.push_back(std::move(arg));
            }
            else
            {
                return nullptr;
            }

            if (CurTok == ')')
            {
                break;
            }

            if (CurTok != ',')
            {
                return this->logError("Expected ')' or ',' in argument list");
            }
            this->getNextToken();
        }
    }

    this->getNextToken();

    return llvm::make_unique<CallExprAST>(idName, std::move(args));
}

std::unique_ptr<ExprAST> Parser::parseExpression()
{
    auto LHS = ParsePrimary();
    if (!LHS)
    {
        return nullptr;
    }

    return ParseBinOpRHS(0, std::move(LHS));
}

std::unique_ptr<ExprAST> Parser::parseNumberExpr()
{
    auto result = llvm::make_unique<NumberExprAST>(this->lexer.numVal);
    this->getNextToken();
    return std::move(result);
}

std::unique_ptr<ExprAST> Parser::parseParenExpr()
{
    this->getNextToken();
    auto v = this->parseExpression();
    if (!v)
    {
        return nullptr;
    }
    if (this->curTok != ')')
    {
        return this->logError("expected ')'");
    }
    this->getNextToken();
    return v;
}

std::unique_ptr<PrototypeAST> Parser::parsePrototype()
{
    if (this->curTok != tok_identifier)
    {
        return this->logErrorP("Expected function name in prototype");
    }

    std::string fnName = this->lexer.identifierStr;
    this->getNextToken();

    if (this->curTok != '(')
    {
        return LogErrorP("Expected '(' in prototype");
    }

    std::vector<std::string> argNames;
    while (this->getNextToken() == tok_identifier)
    {
        ArgNames.push_back(IdentifierStr);
    }
    if (CurTok != ')')
    {
        return LogErrorP("Expected ')' in prototype");
    }

    this->getNextToken();

    return llvm::make_unique<PrototypeAST>(fnName, std::move(argNames));
}

std::unique_ptr<FunctionAST> Parser::parseDefinition()
{
    this->getNextToken();
    auto proto = this->parsePrototype();
    if (!proto)
    {
        return nullptr;
    }

    if (auto expr = this->parseExpression())
    {
        return llvm::make_unique<FunctionAST>(std::move(proto), std::move(expr));
    }
    return nullptr;
}

std::unique_ptr<PrototypeAST> Parser::parseExternal()
{
    this->getNextToken();
    return this->parsePrototype();
}

std::unique_ptr<FunctionAST> Parser::parseTopLevelExpr()
{
    if (auto expr = this->parseExpression())
    {
        auto proto = llvm::make_unique<PrototypeAST>("__anon_expr", std::vector<std::string>());
        return llvm::make_unique<FunctionAST>(std::move(proto), std::move(expr));
    }
    return nullptr;
}

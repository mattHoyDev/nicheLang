#include "common.h"
#include "Parser.h"
#include "Lexer.h"

static void mainLoop(Parser parser)
{
    while (true)
    {
        fprintf(stderr, "ready> ");
        switch (parser.curTok)
        {
            case tok_eof:
                return;
            case ';':
                parser.getNextToken();
                break;
            case tok_func:
                parser.handleDefinition();
                break;
            case tok_import:
                parser.handleExternal();
                break;
            default:
                parser.handleTopLevelExpression();
                break;
        }
    }
}


int main()
{
    Lexer lexer;
    Parser parser(lexer);
    parser.getNextToken();
    mainLoop(parser);
    return 0;
}

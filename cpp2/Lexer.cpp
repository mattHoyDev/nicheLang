#include "Lexer.h"
#include "common.h"

int Lexer::getToken()
{
    static int LastChar = ' ';

    while (isspace(LastChar))
    {
        LastChar = getchar();
    }

    if (isalpha(LastChar))
    {
        this->identifierStr = LastChar;
        while (isalnum((LastChar = getchar())))
        {
            this->identifierStr += LastChar;
        }
        if (this->identifierStr == "func")
        {
            return tok_func;
        }
        if (this->identifierStr == "import")
        {
            return tok_import;
        }
        return tok_identifier;
    }

    if (isdigit(LastChar) || LastChar == '.')
    {
        std::string numStr;
        do
        {
            numStr += LastChar;
            LastChar = getchar();
        }
        while (isdigit(LastChar) || LastChar == '.');

        numVal = strtod(numStr.c_str(), nullptr);
        return tok_number;
    }

    if (LastChar == '/' && getchar() == '/')
    {
        do
        {
            LastChar = getchar();
        }
        while (LastChar != EOF && LastChar != '\n' && LastChar != '\r');

        if (LastChar != EOF)
        {
            return getToken();
        }
    }

    if (LastChar == EOF)
    {
        return tok_eof;
    }

    int ThisChar = LastChar;
    LastChar = getchar();
    return ThisChar;
}

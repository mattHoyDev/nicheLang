#include<string>
#include <algorithm>
#include "llvm/ADT/STLExtras.h"
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>

#ifndef NICHE_LANG_LEXER_H
#define NICHE_LANG_LEXER_H

class Lexer
{
public:
    Lexer() = default;
    std::string identifierStr;
    double numVal;
    int getToken();
};


#endif //NICHE_LANG_LEXER_H

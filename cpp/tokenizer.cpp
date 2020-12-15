#include <string>
#include <vector>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <regex>
#include "NicheParser.h"


template<typename T> void printElement(T first, T second, const int& width)
{
    std::cout << "| " << std::left << std::setw(width) << std::setfill(' ') << first << "| " << std::left << std::setw(width) << std::setfill(' ') << second << " |" << std::endl;
}

int main()
{
    std::string src = R"(

func bool isEven(int inputInt) (
    if (inputInt% 2=0 ) (
        arr arrayVariable: int[1, 2, 3 ]
        map mapVar: { "key1": 1, "key2": 2 }; string test: "this is a test string + wow"
        return True
    )else (//thisis also a comment
        return False // this is a comment
    )
))";

//    std::string src = R"(1 + (2 * (3 + 4)))";
    NicheParser nicheParser;

    std::vector<std::string> tokens = nicheParser.tokenize(src);
    std::vector<std::pair<std::string, std::string>> associatedTokens = nicheParser.associate(tokens);
    printElement("TOKEN", "ABSTRACT TYPE", 15);
    std::cout << "------------------------------------" << std::endl;
    for(auto token : associatedTokens)
    {
        printElement(token.first, token.second, 15);
    }
    return 0;
}

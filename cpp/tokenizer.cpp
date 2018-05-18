#include <string>
#include <vector>
#include <sstream>
#include <iostream>
#include <regex>


std::vector<std::string> tokenize(std::string input)
{
    std::vector<std::string> tokens;
    std::stringstream spaceCheck(input);
    std::string buffer;
    while (std::getline(spaceCheck, buffer, ' '))
    {
        std::smatch matcher;
        std::regex specialParseChars(R"(\(|\)|\+|-|\*|\/|%|\^|>|<|=|&|\||!|:|\[|\]|,|;|\{|\}|")");
        while (std::regex_search(buffer, matcher, specialParseChars))
        {
            for (const auto match : matcher)
            {
                if (matcher.prefix() != "" && matcher.prefix() != "\n" && matcher.prefix() != "\t")
                {
                    tokens.push_back(matcher.prefix());
                }
                tokens.push_back(match);
            }
            buffer = matcher.suffix().str();
        }
        std::string finalBuffer;
        if (!buffer.empty())
        {
            for (char c : buffer)
            {
                if (c != ' ' && c != '\n' && c != '\t')
                {
                    finalBuffer += c;
                }
            }
            if (!finalBuffer.empty())
            {
                tokens.push_back(finalBuffer);
            }
        }
    }
    return tokens;
}

int main()
{
//    std::string src = R"(
//
//func bool isEven(int inputInt) (
//    if (inputInt% 2=0 ) (
//        arr arrayVariable: int[1, 2, 3 ]
//        map mapVar: { "key1": 1, "key2": 2 }; string test: "this is a test string + wow"
//        return True
//    )else (//thisis also a comment
//        return False // this is a comment
//    )
//))";

    std::string src = R"(1 + (2 * (3 + 4)))";

    std::vector<std::string> tokens = tokenize(src);
    for (const auto &token : tokens)
    {
        std::cout << token << std::endl;
    }
    return 0;
}

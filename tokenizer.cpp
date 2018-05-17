#include <algorithm>
#include <string>
#include <vector>
#include <sstream>
#include <iostream>
#include <regex>

int main()
{
    std::string src = "func bool isEven((int inputInt) (if (inputInt% 2=0 ) (return True)else (return False))";
    std::vector<std::string> tokens;
    std::stringstream spaceCheck(src);
    std::string buffer;
    while (std::getline(spaceCheck, buffer, ' '))
    {
        std::smatch matcher;
        std::regex specialParseChars(R"(\(|\)|\+|-|\*|/|%|\^|>|<|=|&|\||!|:)");
        while (std::regex_search(buffer, matcher, specialParseChars))
        {
            for (const auto match : matcher)
            {
                if (matcher.prefix() != "")
                {
                    tokens.push_back(matcher.prefix());
                }
                tokens.push_back(match);
            }
            buffer = matcher.suffix().str();
        }
        if (buffer != "" && buffer != " " && buffer != "\n" && buffer != "\t")
        {
            tokens.push_back(buffer);
        }
    }
    for (const auto &token : tokens)
    {
        std::cout << token << std::endl;
    }
    return 0;
}

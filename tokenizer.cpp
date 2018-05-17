#include <string>
#include <vector>
#include <sstream>
#include <iostream>

int main()
{
    std::string src = "func bool isEven(int inputInt) (if (inputInt % 2 = 0) (return True)else (return False))";
    std::vector<std::string> tokens;
    std::stringstream spaceCheck(src);
    std::string buffer;
    while (std::getline(spaceCheck, buffer, ' '))
    {
        unsigned long openParenPos = buffer.find('(');
        if (openParenPos != std::string::npos)
        {
            if (openParenPos != 0)
            {
                tokens.push_back(buffer.substr(0, openParenPos));
                tokens.push_back(buffer.substr(openParenPos, 1));
                tokens.push_back(buffer.substr(openParenPos + 1, (buffer.size() - (openParenPos + 1))));
            } else
            {
                tokens.emplace_back("(");
                tokens.push_back(buffer.substr(1, buffer.size() - 1));
            }
        }

        unsigned long closeParenPos = buffer.find(')');
        if (closeParenPos != std::string::npos)
        {
            if (closeParenPos != 0)
            {
                tokens.push_back(buffer.substr(0, closeParenPos));
                tokens.push_back(buffer.substr(closeParenPos, 1));
            } else
            {
                tokens.emplace_back(")");
                tokens.push_back(buffer.substr(1, buffer.size() - 1));
            }
        }

        if (buffer != " " && buffer != "\n" && buffer != "\t")
        {
            if (openParenPos == std::string::npos && closeParenPos == std::string::npos)
            {
                tokens.push_back(buffer);
            }
        }
    }
    for (const auto &token : tokens)
    {
        std::cout << token << std::endl;
    }
    return 0;
}

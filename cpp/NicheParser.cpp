#include "NicheParser.h"
#include <string>
#include <vector>
#include <sstream>
#include <iostream>
#include <regex>

const static std::regex SPECIAL_PARSE_CHARS_SEARCH(R"(\(|\)|\+|-|\*|\/|%|\^|>|<|=|&|\||!|:|\[|\]|,|;|\{|\}|")");
const static std::regex INT_SEARCH(R"(\d+([uU]|[lL]|[uU][lL]|[lL][uU])?)");
const static std::regex KEYWORD_SEARCH(R"(str|int|bool|list|arr|map|float|range|len|if|else|for|in|return|import|assert|func|ind|True|False)");
const static std::regex FLOAT_SEARCH(R"(((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?)");
const static std::regex OPERATOR_SEARCH(R"(\+|-|\*|\/|%|\^|&|\||<<|<=|>=|!=|=|<|>|!|:|\+:|-:|\*:|\/:|\+\+|--)");
const static std::regex DELIMITER_SEARCH(R"(\.|\,|\"|\[|\]|\{|\})");
const static std::regex OPEN_PAREN_SEARCH(R"(\()");
const static std::regex CLOSE_PAREN_SEARCH(R"(\))");

NicheParser::NicheParser() = default;

std::vector<std::string> NicheParser::tokenize(const std::string &input)
{
    std::vector<std::string> tokens;
    std::stringstream spaceCheck(input);
    std::string buffer;
    while (std::getline(spaceCheck, buffer, ' '))
    {
        std::smatch matcher;
        while (std::regex_search(buffer, matcher, SPECIAL_PARSE_CHARS_SEARCH))
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

std::vector<std::pair<std::string, std::string>> NicheParser::associate(std::vector<std::string> tokens)
{
    std::vector<std::pair<std::string, std::string>> associatedTokens;
    for (const auto &token : tokens)
    {
        std::smatch intMatcher;
        if (std::regex_match(token, INT_SEARCH))
        {
            std::pair<std::string, std::string> pair = { token, "int" };
            associatedTokens.push_back(pair);
        }
        else if (std::regex_match(token, FLOAT_SEARCH))
        {
            std::pair<std::string, std::string> pair = { token, "float" };
            associatedTokens.push_back(pair);
        }
        else if (std::regex_match(token, KEYWORD_SEARCH))
        {
            std::pair<std::string, std::string> pair = { token, "keyword" };
            associatedTokens.push_back(pair);
        }
        else if (std::regex_match(token, OPERATOR_SEARCH))
        {
            std::pair<std::string, std::string> pair = { token, "op" };
            associatedTokens.push_back(pair);
        }
        else if (std::regex_match(token, OPEN_PAREN_SEARCH))
        {
            std::pair<std::string, std::string> pair = { token, "open" };
            associatedTokens.push_back(pair);
        }
        else if (std::regex_match(token, CLOSE_PAREN_SEARCH))
        {
            std::pair<std::string, std::string> pair = { token, "close" };
            associatedTokens.push_back(pair);
        }
        else if (std::regex_match(token, DELIMITER_SEARCH))
        {
            std::pair<std::string, std::string> pair = { token, "delimiter" };
            associatedTokens.push_back(pair);
        }
        else
        {
            std::pair<std::string, std::string> pair = { token, "generic" };
            associatedTokens.push_back(pair);
        }
    }
    return associatedTokens;
}

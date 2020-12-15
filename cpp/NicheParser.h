#ifndef NICHE_LANG_NICHEPARSER_H
#define NICHE_LANG_NICHEPARSER_H


#include <string>
#include <vector>
#include <regex>

class NicheParser
{
public:
    NicheParser();
    std::vector<std::string> tokenize(const std::string &input);
    std::vector<std::pair<std::string, std::string>> associate(std::vector<std::string> tokens);
};


#endif //NICHE_LANG_NICHEPARSER_H

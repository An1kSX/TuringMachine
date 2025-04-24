#pragma once
#include <string>
#include <map>
#include <vector>
#include <utility>

struct Transition {
    int writeSymbol;
    char move;
    std::string nextState;
};

using Program = std::map<std::string, std::vector<Transition>>;

std::pair<Program, std::string> mt_code_read(const std::string& path);


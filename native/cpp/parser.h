#pragma once
#include <string>
#include <stdexcept>
#include <cctype>
#include <cmath>

class Parser {
public:
    Parser(const std::string& expr);
    double parse();
private:
    std::string expr;
    size_t pos;
    void skipWhitespace();
    double parseExpression();
    double parseTerm();
    double parseFactor();
    double parseUnary();
    double parsePrimary();
    double parseNumber();
};


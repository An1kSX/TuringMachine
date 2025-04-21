#include "parser.h"

Parser::Parser(const std::string& expr) : expr(expr), pos(0) {}

void Parser::skipWhitespace() {
    while (pos < expr.size() && std::isspace(expr[pos])) pos++;
}

double Parser::parseExpression() {
    double result = parseTerm();
    skipWhitespace();
    while (pos < expr.size() && (expr[pos] == '+' || expr[pos] == '-')) {
        char op = expr[pos++];
        double term = parseTerm();
        result = (op == '+') ? result + term : result - term;
        skipWhitespace();
    }
    return result;
}

double Parser::parseTerm() {
    double result = parseFactor();
    skipWhitespace();
    while (pos < expr.size()) {
        if (pos + 1 < expr.size() && expr.substr(pos, 2) == "//") {
            pos += 2;
            double right = parseFactor();
            if (right == 0) throw std::runtime_error("Division by zero in // operator");
            result = static_cast<double>(static_cast<int>(result) / static_cast<int>(right));
        }
        else if (expr[pos] == '/') {
            pos++;
            double right = parseFactor();
            if (right == 0) throw std::runtime_error("Division by zero");
            result /= right;
        }
        else if (expr[pos] == '*') {
            if (pos + 1 < expr.size() && expr[pos + 1] == '*') {
                break;
            }
            else {
                pos++;
                double right = parseFactor();
                result *= right;
            }
        }
        else if (expr[pos] == '%') {
            pos++;
            double right = parseFactor();
            if (right == 0) throw std::runtime_error("Modulo division by zero");
            result = std::fmod(result, right);
        }
        else {
            break;
        }
        skipWhitespace();
    }
    return result;
}

double Parser::parseFactor() {
    double result = parseUnary();
    skipWhitespace();
    if (pos + 1 < expr.size() && expr[pos] == '*' && expr[pos + 1] == '*') {
        pos += 2;
        double exponent = parseFactor();
        result = std::pow(result, exponent);
    }
    return result;
}

double Parser::parseUnary() {
    skipWhitespace();
    if (pos < expr.size() && (expr[pos] == '+' || expr[pos] == '-')) {
        char op = expr[pos++];
        double val = parseUnary();
        return (op == '-') ? -val : val;
    }
    return parsePrimary();
}

double Parser::parsePrimary() {
    skipWhitespace();
    if (pos < expr.size() && expr[pos] == '(') {
        pos++;
        double result = parseExpression();
        skipWhitespace();
        if (pos >= expr.size() || expr[pos] != ')')
            throw std::runtime_error("Missing closing parenthesis");
        pos++;
        return result;
    }

    if (pos + 3 <= expr.size() && expr.substr(pos, 3) == "log") {
        pos += 3;
        skipWhitespace();
        if (pos >= expr.size() || expr[pos] != '(')
            throw std::runtime_error("Expected '(' after log");
        pos++;
        double arg = parseExpression();
        skipWhitespace();
        if (pos >= expr.size() || expr[pos] != ')')
            throw std::runtime_error("Missing closing parenthesis in log");
        pos++;
        if (arg <= 0) throw std::runtime_error("Logarithm domain error");
        return std::log(arg);
    }
    return parseNumber();
}

double Parser::parseNumber() {
    skipWhitespace();
    size_t start = pos;
    while (pos < expr.size() && (std::isdigit(expr[pos]) || expr[pos] == '.')) {
        pos++;
    }
    if (start == pos) {
        throw std::runtime_error("Expected number at position " + std::to_string(pos));
    }
    return std::stod(expr.substr(start, pos - start));
}

double Parser::parse() {
    double result = parseExpression();
    skipWhitespace();
    if (pos != expr.size())
        throw std::runtime_error("Unexpected characters at end of expression");
    return result;
}

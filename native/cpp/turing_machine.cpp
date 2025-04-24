#include "turing_machine.h"
#include "parser.h"
#include "read_file.h"
#include <chrono>
#include <sstream>
#include <iostream>
#include <regex>
#include <set>
#include <stdexcept>
#include <algorithm>
#include <functional>
#include <unordered_map>


TuringMachine::TuringMachine() : variables_num(0) {
    movement_encode = { {'R', 1}, {'L', -1}, {'S', 0} };
}

std::string TuringMachine::replaceAll(std::string str, const std::string& from, const std::string& to) {
    size_t start_pos = 0;
    while ((start_pos = str.find(from, start_pos)) != std::string::npos) {
        str.replace(start_pos, from.length(), to);
        start_pos += to.length();
    }
    return str;
}

void TuringMachine::replaceVariables(std::string& expr, const std::vector<std::string>& vars, const std::vector<int>& values) {
    std::vector<std::pair<std::string, int>> varValues;
    for (size_t i = 0; i < vars.size(); i++) {
        varValues.push_back({ vars[i], values[i] });
    }
    std::sort(varValues.begin(), varValues.end(), [](auto& a, auto& b) {
        return a.first.size() > b.first.size();
        });
    for (auto& p : varValues) {
        std::string var = p.first;
        std::string val = std::to_string(p.second);
        expr = replaceAll(expr, var, val);
    }
}

void TuringMachine::processLogFunctions(std::string& expr) {
    std::regex re("log(\\d+)\\((\\d+)\\)");
    std::smatch match;
    while (std::regex_search(expr, match, re)) {
        std::string base = match[1];
        std::string argument = match[2];
        std::string replacement = "log(" + argument + ") / log(" + base + ")";
        expr = match.prefix().str() + replacement + match.suffix().str();
    }
}

int TuringMachine::calculate(const std::vector<int>& values, bool log_flag) {
    std::string expr = function_str;
    replaceVariables(expr, variables_names, values);
    if (log_flag) {
        processLogFunctions(expr);
    }
    try {
        Parser parser(expr);
        double result = parser.parse();
        return static_cast<int>(result);
    }
    catch (const std::exception& e) {
        throw std::runtime_error("Неправильная запись функции.\n"
            "Переменные следует называть: x1, x2, ..., xn\n"
            "Умножение: x1*4 / x1*x2\n"
            "Возведение в степень: x1^2 / x1^x2\n"
            "Сложение: x1+2 / x1+x2\n"
            "Остаток от деления: x1mod7 / x1modx2\n"
            "Деление без остатка: x1div3 / x1divx2\n"
            "Логарифм: log2(x1) / logx2(x1). Основание логарифма - число сразу после log");
    }
}

int TuringMachine::get_mark(int correct_answers, const std::vector<int>& criteria, double mark_multiplier) {
    double score = correct_answers * mark_multiplier;
    if (score >= criteria[0])
        return 5;
    else if (score >= criteria[1])
        return 4;
    else if (score >= criteria[2])
        return 3;
    else
        return 2;
}

int TuringMachine::tape_builder(int current_index) {
    if (current_index >= (int)tape.size()) {
        tape.resize(current_index + 1, '0');
    }
    else if (current_index < 0) {
        tape.insert(0, 1, '0');
        current_index += 1;
    }
    return current_index;
}

bool TuringMachine::run(double time_limit) {
    int current_index = 0;
    std::string current_state = start_state;
    auto start_time = std::chrono::steady_clock::now();
    size_t iteration = 0;

    while (true) {
        if (current_index < 0 || current_index >= static_cast<int>(tape.size())) {
            current_index = tape_builder(current_index);
        }

        int symbol = tape[current_index] - '0';

        auto it = program.find(current_state);
        const std::vector<Transition>& row = it->second;
        const Transition& trans = row[symbol];

        char prev = tape[current_index];
        char new_symbol = char(trans.writeSymbol + '0');
        tape[current_index] = new_symbol;

        if (movement_encode[trans.move] == 0 && current_state == trans.nextState && prev == new_symbol) {
            break;
        }

        current_index += movement_encode[trans.move];
        current_state = trans.nextState;
        iteration++;

        if (iteration % 50 == 0) {
            auto now = std::chrono::steady_clock::now();
            std::chrono::duration<double> elapsed = now - start_time;
            if (elapsed.count() > time_limit) {
                logs += "Превышено время работы программы!";
                return false;
            }
        }
    }
    return true;
}

std::vector<std::vector<int>> TuringMachine::generate_combinations(int max_num) {
    std::vector<std::vector<int>> combinations;
    std::vector<int> current;
    std::function<void(int)> backtrack = [&](int index) {
        if (combinations.size() >= 60) return;
        if (index == variables_num) {
            combinations.push_back(current);
            return;
        }
        for (int value = 0; value <= max_num; value++) {
            current.push_back(value);
            backtrack(index + 1);
            current.pop_back();
        }
        };
    backtrack(0);
    return combinations;
}

std::pair<int, std::string> TuringMachine::test(const std::string& submission_file, const std::string& problem, const std::vector<int>& criteria, int time_limit, int launch_args) {
    auto res = mt_code_read(submission_file);
    program = res.first;
    logs = res.second;
    if (program.empty()) {
        return { 2, logs };
    }

    start_state = program.begin()->first;


    function_str = replaceAll(problem, "div", "//");
    function_str = replaceAll(function_str, "mod", "%");
    function_str = replaceAll(function_str, "^", "**");

    std::regex var_re("x[0-9]+");
    std::sregex_iterator iter(function_str.begin(), function_str.end(), var_re);
    std::sregex_iterator end;
    std::set<std::string> vars_set;
    while (iter != end) {
        vars_set.insert(iter->str());
        ++iter;
    }
    variables_names.assign(vars_set.begin(), vars_set.end());
    std::sort(variables_names.begin(), variables_names.end());
    variables_num = variables_names.size();

    int correct_answers = 0;
    bool log_flag = (function_str.find("log") != std::string::npos);
    auto combinations = generate_combinations(launch_args);
    double mark_multiplier = 100.0 / combinations.size();
    double limit = 30.0 / combinations.size();

    for (auto& combination : combinations) {
        std::vector<int> values;
        for (auto x : combination) {
            values.push_back(x + (log_flag ? 1 : 0));
        }
        tape = "";
        for (size_t i = 0; i < values.size(); i++) {
            if (i > 0) tape += "0";
            tape += std::string(values[i] + 1, '1');
        }
        bool ok = run(limit);
        if (!ok) {
            std::ostringstream oss;
            oss << "Значения переменных: ";
            for (auto v : values) oss << v << " ";
            oss << "\n";
            logs += oss.str();
            continue;
        }
        int func_value = calculate(values, log_flag);
        int MT_value = 0;
        for (char c : tape) {
            MT_value += (c - '0');
        }
        MT_value -= 1;
        if (MT_value != func_value) {
            std::ostringstream oss;
            oss << "Ошибка! Значение функции: " << func_value << ", Значение Машины Тьюринга: " << MT_value << ", Значения переменных: ";
            for (auto v : values) oss << v << " ";
            oss << "\n";
            logs += oss.str();
        }
        else {
            std::ostringstream oss;
            oss << "Успешно! Значение функции: " << func_value << ", Значение Машины Тьюринга: " << MT_value << ", Значения переменных: ";
            for (auto v : values) oss << v << " ";
            oss << "\n";
            logs += oss.str();
            correct_answers++;
        }
    }
    std::ostringstream oss;
    oss << "Количество правильных ответов: " << correct_answers;
    logs += oss.str();
    int mark = get_mark(correct_answers, criteria, mark_multiplier);
    return { mark, logs };
}

std::pair<int, std::string> TuringMachine::test(const std::string& submission_file, const std::string& problem, const std::vector<int>& criteria, int time_limit, const std::vector<int>& testValues) {
    auto res = mt_code_read(submission_file);
    program = res.first;
    logs = res.second;
    if (program.empty()) {
        return { 2, logs };
    }
    start_state = program.begin()->first;

    function_str = replaceAll(problem, "div", "//");
    function_str = replaceAll(function_str, "mod", "%");
    function_str = replaceAll(function_str, "^", "**");

    std::regex var_re("x[0-9]+");
    std::sregex_iterator iter(function_str.begin(), function_str.end(), var_re);
    std::sregex_iterator end;
    std::set<std::string> vars_set;
    while (iter != end) {
        vars_set.insert(iter->str());
        ++iter;
    }
    variables_names.assign(vars_set.begin(), vars_set.end());
    std::sort(variables_names.begin(), variables_names.end());
    variables_num = variables_names.size();

    if (testValues.size() != (size_t)variables_num) {
        throw std::runtime_error("Количество переменных не совпадает с количеством поданных значений. Переменные необходимо называть: x1, x2, ..., xn");
    }
    tape = "";
    for (size_t i = 0; i < testValues.size(); i++) {
        if (i > 0) tape += "0";
        tape += std::string(testValues[i] + 1, '1');
    }
    double limit = 30;
    bool ok = run(limit);
    if (!ok) {
        std::ostringstream oss;
        oss << "Значения переменных: ";
        for (auto v : testValues) oss << v << " ";
        logs += oss.str();
    }
    int MT_value = 0;
    for (char c : tape) {
        MT_value += (c - '0');
    }
    MT_value -= 1;
    int func_value = calculate(testValues, false);
    int mark = (MT_value == func_value) ? 5 : 2;
    if (mark == 2 && ok) {
        std::ostringstream oss;
        oss << "Ошибка! Значение функции: " << func_value << ", Значение Машины Тьюринга: " << MT_value;
        logs += oss.str();
    }
    else if (mark > 2) {
        std::ostringstream oss;
        oss << "Успешно! Значение функции: " << func_value << ", Значение Машины Тьюринга: " << MT_value;
        logs += oss.str();
    }
    return { mark, logs };
}

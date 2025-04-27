#pragma once
#include "read_file.h"
#include <string>
#include <vector>
#include <utility>
#include <unordered_map>
#include <functional>

class TuringMachine {
public:
    TuringMachine();

    std::pair<int, std::string> test(const std::string& submission_file, const std::string& problem, const std::vector<int>& criteria, int time_limit, int launch_args);

    std::pair<int, std::string> test(const std::string& submission_file, const std::string& problem, const std::vector<int>& criteria, int time_limit, const std::vector<int>& testValues);
private:
    Program program;
    std::string tape;
    std::string start_state;
    std::unordered_map<char, int> movement_encode;
    int variables_num;
    std::string function_str;
    std::vector<std::string> variables_names;
    std::string logs;

    int calculate(const std::vector<int>& values, bool log_flag);
    int get_mark(int correct_answers, const std::vector<int>& criteria, double mark_multiplier);
    bool run(double time_limit);
    int tape_builder(int current_index);
    std::vector<std::vector<int>> generate_combinations(int max_num, bool difficult);


    std::string replaceAll(std::string str, const std::string& from, const std::string& to);
    void replaceVariables(std::string& expr, const std::vector<std::string>& vars, const std::vector<int>& values);
    void processLogFunctions(std::string& expr);
    bool containsMulOrPow(const std::string &expr);
};

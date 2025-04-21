#include "turing_machine.h"
#include <iostream>
#include <vector>
#include <string>
#include <locale>
#include <windows.h>

int main() {
    setlocale(LC_ALL, "");
    TuringMachine MT;
    std::string filePath = "test.csv";
    std::string problem = "5*(x1 + 3)^2";
    std::vector<int> criteria = { 90, 76, 60 };

    auto result = MT.test(filePath, problem, criteria, 30, 45);
    std::cout << result.second << "\nMark: " << result.first << std::endl;
    return 0;
}

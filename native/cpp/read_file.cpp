#include "read_file.h"
#include <fstream>
#include <sstream>
#include <set>
#include <algorithm>
#include <cctype>

std::string toUpper(const std::string& s) {
    std::string res = s;
    std::transform(res.begin(), res.end(), res.begin(), ::toupper);
    return res;
}

std::pair<Program, std::string> mt_code_read(const std::string& path) {
    Program program;
    std::string logs;
    size_t dot_pos = path.find_last_of('.');
    if (dot_pos == std::string::npos || path.substr(dot_pos + 1) != "csv") {
        logs = "Неправильный формат файла. Поддерживаемые форматы: .csv";
        return { program, logs };
    }
    std::ifstream infile(path);
    if (!infile.is_open()) {
        logs = "Не удалось открыть файл";
        return { program, logs };
    }
    std::string line;
    std::vector<std::vector<std::string>> rows;
    bool headerRead = false;
    std::vector<std::string> header;
    while (std::getline(infile, line)) {
        std::istringstream ss(line);
        std::string cell;
        std::vector<std::string> cells;
        while (std::getline(ss, cell, ';')) {
            cell.erase(cell.begin(), std::find_if(cell.begin(), cell.end(), [](unsigned char ch) { return !std::isspace(ch); }));
            cell.erase(std::find_if(cell.rbegin(), cell.rend(), [](unsigned char ch) { return !std::isspace(ch); }).base(), cell.end());
            cells.push_back(cell);
        }
        if (!headerRead) {
            header = cells;
            headerRead = true;
        }
        else {
            if (cells.size() < header.size()) {
                logs = "Неправильно заполнена таблица, либо пустые значения в ячейках. Заполняйте строго по шаблону, прикрепленному к разделу на контесте";
                return { program, logs };
            }
            rows.push_back(cells);
        }
    }
    infile.close();
    int idxA = -1, idxQ = -1, idxPhi = -1, idxPsi = -1, idxH = -1;
    for (size_t i = 0; i < header.size(); i++) {
        if (!header.empty()) {
            if (header[0].size() >= 3 &&
                (unsigned char)header[0][0] == 0xEF &&
                (unsigned char)header[0][1] == 0xBB &&
                (unsigned char)header[0][2] == 0xBF)
            {
                header[0].erase(0, 3);
            }
        }
        std::string col = header[i];
        if (col == "A") idxA = i;
        else if (col == "Q") idxQ = i;
        else if (col == "phi") idxPhi = i;
        else if (col == "psi") idxPsi = i;
        else if (col == "H") idxH = i;
    }
    if (idxA == -1 || idxQ == -1 || idxPhi == -1 || idxPsi == -1 || idxH == -1) {
        std::ostringstream oss;
        oss << "Ошибка: Заголовки столбцов не соответствуют требуемым. "
            << "idxA = " << idxA << ", "
            << "idxQ = " << idxQ << ", "
            << "idxPhi = " << idxPhi << ", "
            << "idxPsi = " << idxPsi << ", "
            << "idxH = " << idxH;
        logs = oss.str();
        return { program, logs };
    }
    std::set<std::pair<std::string, std::string>> duplicates;
    std::set<std::pair<std::string, std::string>> seen;
    for (auto& cells : rows) {
        std::string A = cells[idxA];
        std::string Q = cells[idxQ];
        if (A.empty() || Q.empty() || cells[idxPhi].empty() || cells[idxPsi].empty() || cells[idxH].empty()) {
            logs = "Неправильно заполнена таблица, либо пустые значения в ячейках. Заполняйте строго по шаблону, прикрепленному к разделу на контесте";
            return { program, logs };
        }
        std::pair<std::string, std::string> key = { Q, A };
        if (seen.find(key) != seen.end()) {
            duplicates.insert(key);
        }
        else {
            seen.insert(key);
        }
    }
    if (!duplicates.empty()) {
        std::ostringstream oss;
        oss << "Имеются противоречащие друг другу инструкции\n";
        for (auto& p : duplicates) {
            oss << "Q: " << p.first << ", A: " << p.second << "\n";
        }
        logs = oss.str();
        return { program, logs };
    }

    int maxA = 0;
    int maxPsi = 0;
    std::set<char> move_alphabet;
    for (auto& cells : rows) {
        std::string A_str = cells[idxA];
        std::string Q = cells[idxQ];
        std::string phi = cells[idxPhi];
        std::string psi_str = cells[idxPsi];
        std::string H = toUpper(cells[idxH]);
        int A = std::stoi(A_str);
        int psi = std::stoi(psi_str);
        if (A > maxA) maxA = A;
        if (psi > maxPsi) maxPsi = psi;
        move_alphabet.insert(H[0]);

        if (program.find(Q) == program.end()) {
            program[Q] = { {0, 'S', Q}, {1, 'S', Q} };
        }

        if (A < 0 || A > 1) {
            logs = "Входной и выходной алфавиты Машины Тьюринга могут состоять только из 0 и 1";
            program.clear();
            return { program, logs };
        }
        program[Q][A] = { psi, H[0], phi };

        if (program.find(phi) == program.end()) {
            program[phi] = { {0, 'S', phi}, {1, 'S', phi} };
        }
    }
    move_alphabet.insert({'L','R','S'}); 
    logs = "Файл успешно считан\n";
    std::set<char> valid_moves = { 'L', 'R', 'S' };
    if (move_alphabet != valid_moves) {
        logs = "Для перемещения по ленте можно использовать только нижеследующие символы:\nL - налево\nR - направо\nS - остановка";
        program.clear();
    }
    if (maxA > 1 || maxPsi > 1) {
        logs = "Входной и выходной алфавиты Машины Тьюринга могут состоять только из 0 и 1";
        program.clear();
    }
    return { program, logs };
}

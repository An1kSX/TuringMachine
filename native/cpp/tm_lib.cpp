// tm_lib.cpp  ---------------------------------------------------------------
#include "turing_machine.h"

#include <string>
#include <sstream>
#include <vector>
#include <iostream>

// --- CP1251 → UTF‑8 перекодировка (Windows). На Linux просто возвращаем то же. ----
#ifdef _WIN32
#include <Windows.h>
static std::string cp1251_to_utf8(const std::string& s)
{
    if (s.empty()) return {};
    int wlen = MultiByteToWideChar(1251, 0, s.data(),
        static_cast<int>(s.size()), nullptr, 0);
    std::wstring wbuf(wlen, L'\0');
    MultiByteToWideChar(1251, 0, s.data(), static_cast<int>(s.size()),
        wbuf.data(), wlen);

    int u8len = WideCharToMultiByte(CP_UTF8, 0, wbuf.data(), wlen,
        nullptr, 0, nullptr, nullptr);
    std::string out(u8len, '\0');
    WideCharToMultiByte(CP_UTF8, 0, wbuf.data(), wlen,
        out.data(), u8len, nullptr, nullptr);
    return out;
}
#else
static std::string cp1251_to_utf8(const std::string& s) { return s; }
#endif
// -----------------------------------------------------------------------------

// ——— макрос экспорта символов ———
#if defined(_WIN32)
#  define TM_API extern "C" __declspec(dllexport)
#else                    // Linux / macOS
#  define TM_API extern "C" __attribute__((visibility("default")))
#endif

// --- вспомогательная разбивка "85,65,55" -> std::vector<int> -----------------
static std::vector<int> parse_csv_int(const char* csv)
{
    std::vector<int> out;
    std::stringstream ss(csv ? csv : "");
    std::string item;
    while (std::getline(ss, item, ',')) {
        if (!item.empty())
            out.push_back(std::stoi(item));   // item — std::string
    }
    return out;
}

// -------- ГЛАВНАЯ экспортируемая функция ------------------------------------
/*  file          : путь к CSV (или уже сконвертированному XLSX)
    problem       : строка‑условие
    criteria_csv  : "85,65,55"
    time_limit_ms : лимит времени (int)
    launch_args   : число комбинаций

    stdout ← логи (уже в UTF‑8)
    return ← итоговая оценка
*/
TM_API int tm_test(
    const char* file,
    const char* problem,
    const char* criteria_csv,
    int time_limit,
    int launch_args,
    char* log_buf,
    int  log_buf_sz)
{
    try {
        std::vector<int> criteria = parse_csv_int(criteria_csv);

        TuringMachine tm;
        auto [mark, logs] = tm.test(
            file ? file : "",
            problem ? problem : "",
            criteria,
            time_limit,
            launch_args
        );
        if (log_buf && log_buf_sz > 0) {
            std::string utf8 = cp1251_to_utf8(logs);
            strncpy_s(log_buf, log_buf_sz, utf8.c_str(), _TRUNCATE);
        }
        return mark;
    }
    catch (const std::exception& ex) {
        std::cerr << "tm_test exception: " << ex.what() << std::endl;
        return -1;   // особое значение «ошибка»
    }
}

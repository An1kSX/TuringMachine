#include "turing_machine.h"
#include <string>
#include <sstream>
#include <vector>
#include <cstring>
#include <iostream>

#if defined(_WIN32)
#  define TM_API extern "C" __declspec(dllexport)
#  define COPY_STR(dst, src, sz) strncpy_s(dst, sz, src, _TRUNCATE)
#else
#  define TM_API extern "C" __attribute__((visibility("default")))
#  define COPY_STR(dst, src, sz)          \
     do { std::strncpy(dst, src, sz); (dst)[(sz)-1] = '\0'; } while (0)
#endif

static std::string cp1251_to_utf8(const std::string& s) { return s; }

static std::vector<int> parse_csv_int(const char* csv)
{
    std::vector<int> out;
    std::stringstream ss(csv ? csv : "");
    std::string tok;
    while (std::getline(ss, tok, ',')) {
        if (!tok.empty())
            out.push_back(std::stoi(tok));
    }
    return out;
}

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
        auto criteria = parse_csv_int(criteria_csv);

        TuringMachine tm;
        std::pair<int, std::string> res = tm.test(
            file ? file : "",
            problem ? problem : "",
            criteria,
            time_limit,
            launch_args
            );
        int mark = res.first;
        const std::string& logs = res.second;

        if (log_buf && log_buf_sz > 0)
            COPY_STR(log_buf, logs.c_str(), log_buf_sz);

        return mark;
    }
    catch (const std::exception& ex) {
        std::cerr << "tm_test exception: " << ex.what() << std::endl;
        return -1;
    }
}

#include "turing_machine.h"
#include <string>
#include <sstream>
#include <vector>
#include <iostream>
#ifdef _WIN32
  #include <windows.h>
  
#else
  #define COPY_STR(dst, src, sz)          \
      do {                                \
          std::strncpy(dst, src, sz);     \
          (dst)[(sz) - 1] = '\0';         \
      } while (0)
#endif

#ifdef _WIN32
#include <Windows.h>
#define COPY_STR(dst, src, sz) strncpy_s(dst, sz, src, _TRUNCATE)
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
	  #define COPY_STR(dst, src, sz)          \
      do {                                \
          std::strncpy(dst, src, sz);     \
          (dst)[(sz) - 1] = '\0';         \
      } while (0)
static std::string cp1251_to_utf8(const std::string& s) { return s; }
#endif


#if defined(_WIN32)
#  define TM_API extern "C" __declspec(dllexport)
#else
#  define TM_API extern "C" __attribute__((visibility("default")))
#endif


static std::vector<int> parse_csv_int(const char* csv)
{
    std::vector<int> out;
    std::stringstream ss(csv ? csv : "");
    std::string item;
    while (std::getline(ss, item, ',')) {
        if (!item.empty())
            out.push_back(std::stoi(item));
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
            COPY_STR(log_buf, utf8.c_str(), log_buf_sz);
        }
        return mark;
    }
    catch (const std::exception& ex) {
        std::cerr << "tm_test exception: " << ex.what() << std::endl;
        return -1;
    }
}

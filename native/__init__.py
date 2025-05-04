from __future__ import annotations
import os, sys, subprocess, hashlib, shutil
from pathlib import Path
from ctypes import cdll, c_char_p, c_int, create_string_buffer



HERE = Path(__file__).resolve().parent
BUILT = HERE / "_build"
BUILT.mkdir(exist_ok=True)

if sys.platform.startswith("linux"):
    LIB_NAME = "libtm_native.so"
    COMPILER = ["g++", "-std=c++11", "-O2", "-fPIC", "-shared", "-static-libstdc++"]

elif sys.platform == "darwin":
    LIB_NAME = "libtm_native.dylib"
    COMPILER = [
        "g++", "-std=c++11", "-O2", "-fPIC", "-shared",
        "-static-libstdc++",
        "-Wl,-install_name,@rpath/libtm_native.dylib"
        ]

elif sys.platform == "win32":
    LIB_NAME = "tm_native.dll"
    COMPILER = ["cl", "/std:c++11", "/O2", "/LD"]

else:
    raise RuntimeError(f"Unsupported platform: {sys.platform}")

LIB_PATH = BUILT / LIB_NAME

def _build_library():
    if sys.platform == "win32":
        if shutil.which("make"):
            make_cmd = ["make"]

        elif shutil.which("nmake"):
            make_cmd = ["nmake", "/f", "Makefile"]

        elif shutil.which("mingw32-make"):
            make_cmd = ["mingw32-make"]

        else:
            raise RuntimeError("Make не найден")
    else:
        make_cmd = ["make"]

    subprocess.run(make_cmd, check=True, cwd=HERE)

    lib_path = BUILT / LIB_NAME
    if not lib_path.exists():
        raise RuntimeError(f"Сборка завершилась, но библиотека не найдена по пути {lib_path}")

    return lib_path

def _load_library():
    _build_library()
    return cdll.LoadLibrary(str(LIB_PATH))

_lib = _load_library()

_tm_test = _lib.tm_test
_tm_test.argtypes = [
    c_char_p,
    c_char_p,
    c_char_p,
    c_int,
    c_int,
    c_char_p,
    c_int
]
_tm_test.restype = c_int


def tm_test(file_b: bytes,
             prob_b: bytes,
             crit_csv_b: bytes,
             time_limit: int,
             launch_args: int,
             log_buf, log_sz: int
             ):

    return _tm_test(file_b, prob_b, crit_csv_b,
                     time_limit, launch_args,
                     log_buf, log_sz)
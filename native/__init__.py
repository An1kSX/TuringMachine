from __future__ import annotations
import os, sys, subprocess, hashlib, shutil
from pathlib import Path
from ctypes import cdll, c_char_p, c_int, create_string_buffer



HERE = Path(__file__).resolve().parent
BUILT = HERE / "_build"
BUILT.mkdir(exist_ok=True)

if sys.platform.startswith("linux"):
    LIB_NAME = "libtm_native.so"
    COMPILER = ["g++", "-std=c++17", "-O2", "-fPIC", "-shared"]

elif sys.platform == "win32":
    LIB_NAME = "tm_native.dll"
    COMPILER = ["cl", "/std:c++17", "/O2", "/LD"]

else:
    raise RuntimeError(f"Unsupported platform: {sys.platform}")

LIB_PATH = BUILT / LIB_NAME

def _build_library():
    cpp_dir = HERE / "cpp"
    sources = sorted(str(p) for p in cpp_dir.glob("*.cpp"))
    if not sources:
        raise FileNotFoundError("No .cpp files found in cpp/ folder")

    if sys.platform == "win32":
        cmd = COMPILER + sources + [f"/Fe{LIB_PATH}"]

    else:
        cmd = COMPILER + sources + ["-o", str(LIB_PATH)]

    print("Compiling native library:")
    print("  ", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=cpp_dir)

    if not LIB_PATH.exists():
        raise RuntimeError("Compilation finished but .so/.dll not found")

    return LIB_PATH

def _load_library():
    if not LIB_PATH.exists():
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
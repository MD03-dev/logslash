"""Wrapper Python cho module C tăng tốc detect format.

Tự động fallback về Python thuần nếu không load được .so.
"""

import ctypes
import os
import sys

_LIB = None
_LOADED = False

FMT_MAP = {0: "plain", 1: "json", 2: "syslog"}

LIB_NAME = "libcdetect.so"
LIB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), LIB_NAME)


def load_library(path=None):
    """Load .so, trả về True nếu thành công."""
    global _LIB, _LOADED
    if _LOADED:
        return _LIB is not None

    target = path or LIB_PATH
    if not os.path.exists(target):
        _LOADED = True
        _LIB = None
        return False

    try:
        lib = ctypes.CDLL(target)
        lib.detect_format.argtypes = [ctypes.c_char_p, ctypes.c_int]
        lib.detect_format.restype = ctypes.c_int
        lib.count_formats.argtypes = [
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
        ]
        lib.count_formats.restype = None
        _LIB = lib
        _LOADED = True
        return True
    except OSError as e:
        print(f"Cảnh báo: không load được {target}: {e}", file=sys.stderr)
        _LOADED = True
        _LIB = None
        return False


def is_available():
    """Kiểm tra C module có sẵn không."""
    if not _LOADED:
        load_library()
    return _LIB is not None


def detect_format_c(line):
    """Detect format bằng C. Trả về 'json'|'syslog'|'plain' hoặc None nếu C không có."""
    if not is_available():
        return None
    if isinstance(line, str):
        b = line.encode("utf-8", errors="replace")
    else:
        b = line
    fmt_int = _LIB.detect_format(b, len(b))
    return FMT_MAP.get(fmt_int, "plain")


def count_formats_c(lines):
    """Đếm format cho list dòng. Trả về dict hoặc None nếu C không có."""
    if not is_available():
        return None

    encoded = [l.encode("utf-8", errors="replace") if isinstance(l, str) else l
               for l in lines]
    n = len(encoded)
    if n == 0:
        return {"plain": 0, "json": 0, "syslog": 0}

    arr = (ctypes.c_char_p * n)()
    lens = (ctypes.c_int * n)()
    for i, b in enumerate(encoded):
        arr[i] = b
        lens[i] = len(b)

    counts = (ctypes.c_int * 3)()
    _LIB.count_formats(arr, lens, n, counts)
    return {"plain": counts[0], "json": counts[1], "syslog": counts[2]}


def detect_file_format_c(lines):
    """Detect format chủ đạo của cả file bằng C."""
    counts = count_formats_c(lines)
    if counts is None:
        return None
    total = sum(counts.values())
    if total == 0:
        return "plain"
    return max(counts, key=counts.get)

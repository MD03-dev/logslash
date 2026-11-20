"""CLI entry point cho logslash."""

import argparse
import sys

try:
    from logslash import __version__
    from logslash.detector import detect_format, detect_file_format
    from logslash.parsers.registry import parse_file
    from logslash.parsers.regex_parser import load_regex_parser
    from logslash.filters.engine import build_filter, apply_filter, FilterError
    from logslash.outputs import OUTPUTS
    from logslash import cdetect
except ImportError:
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from logslash import __version__
    from logslash.detector import detect_format, detect_file_format
    from logslash.parsers.registry import parse_file
    from logslash.parsers.regex_parser import load_regex_parser
    from logslash.filters.engine import build_filter, apply_filter, FilterError
    from logslash.outputs import OUTPUTS
    from logslash import cdetect


def _read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


def _print_file_error(path, err):
    if isinstance(err, FileNotFoundError):
        print(f"Lỗi: không tìm thấy file '{path}'", file=sys.stderr)
    elif isinstance(err, PermissionError):
        print(f"Lỗi: không có quyền đọc '{path}'", file=sys.stderr)
    else:
        print(f"Lỗi đọc file: {err}", file=sys.stderr)


def _load_regex(args):
    if not getattr(args, "patterns", None):
        return None
    rp = load_regex_parser(args.patterns)
    if rp is None:
        print(f"Cảnh báo: không load được pattern file '{args.patterns}'.",
              file=sys.stderr)
    return rp


def _emit(records, args):
    """In record theo output format user chọn."""
    if args.limit and args.limit > 0:
        records = records[: args.limit]

    fmt = getattr(args, "output", "ndjson") or "ndjson"

    # Tương thích flag cũ --ndjson
    if getattr(args, "ndjson", False) and fmt == "ndjson":
        pass  # giữ nguyên

    output_fn = OUTPUTS.get(fmt)
    if output_fn is None:
        print(f"Lỗi: output format không hỗ trợ: '{fmt}'", file=sys.stderr)
        print(f"Hỗ trợ: {', '.join(sorted(OUTPUTS))}", file=sys.stderr)
        return 2

    output_fn(records, sys.stdout)

    if args.stats:
        print(f"\n# {len(records)} record", file=sys.stderr)
    return 0


def cmd_detect(args):
    try:
        lines = _read_lines(args.file)
    except OSError as e:
        _print_file_error(args.file, e)
        return 1

    if not lines:
        print(f"File '{args.file}' trống.")
        return 0

    file_format = detect_file_format(lines)
    print(f"File: {args.file}")
    print(f"Số dòng: {len(lines)}")
    print(f"Format chủ đạo: {file_format}")
    print()
    print("Chi tiết 20 dòng đầu:")
    print("-" * 60)
    for i, line in enumerate(lines[:20], 1):
        if not line.strip():
            print(f"{i:4d}  [trống]")
            continue
        fmt = detect_format(line)
        preview = line.rstrip("\n")[:50]
        print(f"{i:4d}  [{fmt:6s}] {preview}")
    if len(lines) > 20:
        print(f"... và {len(lines) - 20} dòng nữa")
    return 0


def cmd_parse(args):
    try:
        lines = _read_lines(args.file)
    except OSError as e:
        _print_file_error(args.file, e)
        return 1

    regex_parser = _load_regex(args)
    records = parse_file(lines, regex_parser=regex_parser)
    return _emit(records, args)


def cmd_filter(args):
    try:
        lines = _read_lines(args.file)
    except OSError as e:
        _print_file_error(args.file, e)
        return 1

    regex_parser = _load_regex(args)
    records = parse_file(lines, regex_parser=regex_parser)

    try:
        f = build_filter(args)
    except FilterError as e:
        print(f"Lỗi filter: {e}", file=sys.stderr)
        return 2

    if args.show_filter:
        print(f"# Filter: {f}", file=sys.stderr)

    filtered = apply_filter(records, f)

    if args.stats:
        print(f"# Trước lọc: {len(records)} record", file=sys.stderr)
        print(f"# Sau lọc:  {len(filtered)} record", file=sys.stderr)

    return _emit(filtered, args)



def cmd_bench(args):
    """Benchmark detect format: C vs Python."""
    import time
    try:
        lines = _read_lines(args.file)
    except OSError as e:
        _print_file_error(args.file, e)
        return 1

    if not lines:
        print("File trống.")
        return 0

    # Lặp để đủ mẫu
    repeat = args.repeat
    big = lines * repeat

    from logslash.detector import _detect_python, detect_file_format
    from logslash import cdetect as cd

    print(f"File: {args.file}")
    print(f"Số dòng gốc: {len(lines)}")
    print(f"Lặp: {repeat}x → {len(big)} dòng")
    print()

    # Python
    t0 = time.perf_counter()
    py_counts = {"json": 0, "syslog": 0, "plain": 0}
    for line in big:
        py_counts[_detect_python(line)] += 1
    py_time = time.perf_counter() - t0

    print(f"Python thuần: {py_time:.4f}s")
    print(f"  {py_counts}")
    print(f"  {len(big)/py_time:.0f} dòng/giây")
    print()

    # C
    if not cd.is_available():
        print("C module chưa build. Chạy: bash scripts/build_c.sh")
        return 0

    t0 = time.perf_counter()
    c_counts = cd.count_formats_c(big)
    c_time = time.perf_counter() - t0

    print(f"C module:     {c_time:.4f}s")
    print(f"  {c_counts}")
    print(f"  {len(big)/c_time:.0f} dòng/giây")
    print()

    if c_time > 0:
        speedup = py_time / c_time
        print(f"Tăng tốc: {speedup:.1f}x")
    return 0


def cmd_version(args):
    print(f"logslash v{__version__}")
    return 0


def _add_common_parse_args(p):
    p.add_argument("file", help="Đường dẫn tới file log")
    p.add_argument("--ndjson", action="store_true",
                   help="Tương thích cũ, tương đương --output ndjson")
    p.add_argument("--output", "-o", default="ndjson",
                   choices=sorted(OUTPUTS.keys()),
                   help="Định dạng xuất (mặc định: ndjson)")
    p.add_argument("--limit", type=int, default=0, help="Chỉ in N record đầu")
    p.add_argument("--stats", action="store_true", help="In thống kê ra stderr")
    p.add_argument("--patterns", default=None,
                   help="File JSON chứa custom regex pattern")


def _add_filter_args(p):
    p.add_argument("--level", default=None, help="Lọc chính xác level")
    p.add_argument("--level-min", dest="level_min", default=None,
                   help="Lọc level >= ngưỡng")
    p.add_argument("--source", default=None, help="Lọc source chứa substring")
    p.add_argument("--contains", default=None, help="Message chứa substring")
    p.add_argument("--not-contains", dest="not_contains", default=None,
                   help="Message KHÔNG chứa substring")
    p.add_argument("--since", default=None, help="Timestamp >= mốc (ISO)")
    p.add_argument("--until", default=None, help="Timestamp <= mốc (ISO)")
    p.add_argument("--format", dest="format", default=None,
                   help="Lọc format (json/syslog/plain/regex:*)")
    p.add_argument("--show-filter", dest="show_filter", action="store_true",
                   help="In filter ra stderr để debug")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="logslash",
        description="Lọc và phân tích log hỗn hợp (JSON, syslog, plain text).",
        epilog="Ví dụ: logslash filter app.log --level error -o table",
    )
    parser.add_argument("--version", action="store_true", help="In version và thoát")

    sub = parser.add_subparsers(dest="command", help="Lệnh con")

    p_detect = sub.add_parser("detect", help="Detect format của file log")
    p_detect.add_argument("file", help="Đường dẫn tới file log")
    p_detect.set_defaults(func=cmd_detect)

    p_parse = sub.add_parser("parse", help="Parse file log thành JSON record")
    _add_common_parse_args(p_parse)
    p_parse.set_defaults(func=cmd_parse)

    p_filter = sub.add_parser("filter", help="Parse rồi lọc record theo điều kiện")
    _add_common_parse_args(p_filter)
    _add_filter_args(p_filter)
    p_filter.set_defaults(func=cmd_filter)

    p_bench = sub.add_parser("bench", help="Benchmark detect format C vs Python")
    p_bench.add_argument("file", help="Đường dẫn tới file log")
    p_bench.add_argument("--repeat", type=int, default=100,
                         help="Số lần lặp file (mặc định 100)")
    p_bench.set_defaults(func=cmd_bench)

    p_version = sub.add_parser("version", help="In version")
    p_version.set_defaults(func=cmd_version)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"logslash v{__version__}")
        return 0

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

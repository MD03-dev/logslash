"""CLI entry point cho logslash (Đã tối ưu Streaming - Chống tràn RAM)."""

import argparse
import json
import sys

from logslash import __version__
from logslash.detector import detect_format, detect_file_format
from logslash.parsers.registry import parse_line, parse_file
from logslash.parsers.regex_parser import load_regex_parser
from logslash.filters.engine import build_filter, apply_filter, FilterError
from logslash.outputs import OUTPUTS

# Hàm đọc dòng (Generator) thay vì readlines()
def _read_lines(path):
    if path == "-":
        # Đọc từ luồng (Pipe/Stdin)
        for line in sys.stdin:
            yield line
    else:
        # Đọc từ file (từng dòng một, không nạp cả file vào RAM)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    yield line
        except OSError as e:
            if isinstance(e, FileNotFoundError):
                print(f"Lỗi: không tìm thấy file '{path}'", file=sys.stderr)
            else:
                print(f"Lỗi đọc file: {e}", file=sys.stderr)
            sys.exit(1)

def _load_regex(args):
    if not getattr(args, "patterns", None):
        return None
    return load_regex_parser(args.patterns)

def _emit(records, args):
    # Vì records bây giờ là một generator, ta không dùng len() hay cắt mảng trực tiếp được
    # Phải dùng cơ chế đếm và lọc (islice) nếu có limit
    import itertools
    if args.limit and args.limit > 0:
        records = itertools.islice(records, args.limit)
    
    fmt = getattr(args, "output", "ndjson") or "ndjson"
    output_fn = OUTPUTS.get(fmt)
    
    kwargs = {}
    if getattr(args, "no_color", False):
        kwargs["use_color"] = False
        
    # Các hàm output cần nhận list, nhưng vì ta muốn streaming nên phải viết custom cho ndjson
    # Riêng json/table/csv cần đọc hết nên ta phải ép thành list (chỉ khi user yêu cầu)
    if fmt in ["json", "table", "csv", "pretty"]:
        records = list(records) # Ép thành list (tốn RAM, nhưng đây là do user muốn format phức tạp)
        output_fn(records, sys.stdout, **kwargs)
        count = len(records)
    else:
        # NDJSON có thể in từng dòng, cực kỳ tiết kiệm RAM
        count = 0
        for rec in records:
            print(json.dumps(rec, ensure_ascii=False))
            count += 1
            
    if args.stats:
        print(f"\n# {count} record", file=sys.stderr)
    return 0

def cmd_detect(args):
    lines = list(_read_lines(args.file))
    if not lines:
        return 0
    file_format = detect_file_format(lines)
    print(f"File: {args.file}")
    print(f"Format chủ đạo: {file_format}")
    return 0

def cmd_parse(args):
    regex_parser = _load_regex(args)
    lines = _read_lines(args.file)
    # Trả về generator
    records = parse_file(lines, regex_parser=regex_parser, ignore_errors=True)
    return _emit(records, args)

def cmd_filter(args):
    regex_parser = _load_regex(args)
    lines = _read_lines(args.file)
    records = parse_file(lines, regex_parser=regex_parser, ignore_errors=True)
    
    try:
        f = build_filter(args)
    except FilterError as e:
        print(f"Lỗi filter: {e}", file=sys.stderr)
        return 2
        
    # Lọc generator
    filtered = (rec for rec in records if f.match(rec))
    return _emit(filtered, args)

def cmd_bench(args):
    import time
    lines = list(_read_lines(args.file))
    big = lines * args.repeat
    from logslash.detector import _detect_python
    from logslash import cdetect as cd
    
    t0 = time.perf_counter()
    for line in big: _detect_python(line)
    py_time = time.perf_counter() - t0
    
    if cd.is_available():
        t0 = time.perf_counter()
        cd.count_formats_c(big)
        c_time = time.perf_counter() - t0
        print(f"Python: {py_time:.4f}s | C: {c_time:.4f}s | Tăng tốc: {py_time/c_time:.1f}x")
    return 0

def cmd_version(args):
    print(f"logslash v{__version__}")
    return 0

def main(argv=None):
    parser = argparse.ArgumentParser(prog="logslash")
    parser.add_argument("--version", action="store_true")
    sub = parser.add_subparsers(dest="command")

    p_detect = sub.add_parser("detect")
    p_detect.add_argument("file")
    p_detect.set_defaults(func=cmd_detect)

    for cmd_name, func in [("parse", cmd_parse), ("filter", cmd_filter)]:
        p = sub.add_parser(cmd_name)
        p.add_argument("file")
        p.add_argument("--output", "-o", default="ndjson", choices=["json","ndjson","table","csv","pretty"])
        p.add_argument("--no-color", action="store_true")
        p.add_argument("--patterns")
        p.add_argument("--limit", type=int, default=0)
        p.add_argument("--stats", action="store_true")
        if cmd_name == "filter":
            p.add_argument("--level", default=None)
            p.add_argument("--level-min", dest="level_min", default=None)
            p.add_argument("--contains", default=None)
            p.add_argument("--source", default=None)
            p.add_argument("--show-filter", dest="show_filter", action="store_true")
        p.set_defaults(func=func)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"): return 0
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())

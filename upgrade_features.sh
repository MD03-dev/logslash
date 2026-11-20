#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "🚀 Bắt đầu nâng cấp logslash..."

# 1. SỬA LỖI ĐỌC TỪ STDIN (PIPE)
cat > logslash/cli.py.tmp << 'PYEOF'
import sys
import argparse
from logslash import __version__
from logslash.parsers.registry import parse_file, parse_line
from logslash.filters.engine import build_filter, apply_filter, FilterError
from logslash.outputs import OUTPUTS
from logslash.parsers.regex_parser import load_regex_parser

def _read_lines(path):
    # Nếu path là "-" thì đọc từ stdin (hỗ trợ pipe)
    if path == "-":
        return sys.stdin.readlines()
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()

def _emit(records, args):
    if args.limit and args.limit > 0:
        records = records[: args.limit]
    
    fmt = getattr(args, "output", "ndjson") or "ndjson"
    output_fn = OUTPUTS.get(fmt)
    if output_fn is None:
        print(f"Lỗi: output format không hỗ trợ: '{fmt}'", file=sys.stderr)
        return 2
    
    # Nếu có flag --no-color thì ghi đè
    kwargs = {}
    if getattr(args, "no_color", False):
        kwargs["use_color"] = False
        
    output_fn(records, sys.stdout, **kwargs)

    if args.stats:
        print(f"\n# {len(records)} record", file=sys.stderr)
    return 0

def cmd_parse(args):
    try:
        lines = _read_lines(args.file)
    except OSError as e:
        print(f"Lỗi đọc file: {e}", file=sys.stderr)
        return 1
    
    regex_parser = load_regex_parser(args.patterns) if args.patterns else None
    
    # Bọc lỗi ở đây để bỏ qua các dòng log bị hỏng
    records = parse_file(lines, regex_parser=regex_parser, ignore_errors=True)
    return _emit(records, args)

def cmd_filter(args):
    try:
        lines = _read_lines(args.file)
    except OSError as e:
        print(f"Lỗi đọc file: {e}", file=sys.stderr)
        return 1
        
    regex_parser = load_regex_parser(args.patterns) if args.patterns else None
    records = parse_file(lines, regex_parser=regex_parser, ignore_errors=True)
    
    try:
        f = build_filter(args)
    except FilterError as e:
        print(f"Lỗi filter: {e}", file=sys.stderr)
        return 2

    if getattr(args, "show_filter", False):
        print(f"# Filter: {f}", file=sys.stderr)
        
    filtered = apply_filter(records, f)
    return _emit(filtered, args)

def cmd_version(args):
    print(f"logslash v{__version__}")
    return 0

def main(argv=None):
    parser = argparse.ArgumentParser(prog="logslash")
    parser.add_argument("--version", action="store_true")
    sub = parser.add_subparsers(dest="command")

    # Parse
    p_parse = sub.add_parser("parse")
    p_parse.add_argument("file", help="Đường dẫn file hoặc '-' để đọc từ stdin")
    p_parse.add_argument("--output", "-o", default="table", choices=["json","ndjson","table","csv","pretty"])
    p_parse.add_argument("--no-color", action="store_true", help="Tắt màu sắc")
    p_parse.add_argument("--patterns")
    p_parse.add_argument("--limit", type=int, default=0)
    p_parse.add_argument("--stats", action="store_true")
    p_parse.set_defaults(func=cmd_parse)

    # Filter
    p_filter = sub.add_parser("filter")
    p_filter.add_argument("file", help="Đường dẫn file hoặc '-' để đọc từ stdin")
    p_filter.add_argument("--output", "-o", default="table", choices=["json","ndjson","table","csv","pretty"])
    p_filter.add_argument("--no-color", action="store_true", help="Tắt màu sắc")
    p_filter.add_argument("--patterns")
    p_filter.add_argument("--limit", type=int, default=0)
    p_filter.add_argument("--stats", action="store_true")
    p_filter.add_argument("--level", default=None)
    p_filter.add_argument("--level-min", dest="level_min", default=None)
    p_filter.add_argument("--source", default=None)
    p_filter.add_argument("--contains", default=None)
    p_filter.add_argument("--not-contains", dest="not_contains", default=None)
    p_filter.add_argument("--since", default=None)
    p_filter.add_argument("--until", default=None)
    p_filter.add_argument("--format", dest="format", default=None)
    p_filter.add_argument("--show-filter", dest="show_filter", action="store_true")
    p_filter.set_defaults(func=cmd_filter)

    # Version
    p_v = sub.add_parser("version")
    p_v.set_defaults(func=cmd_version)

    args = parser.parse_args(argv)
    if args.version:
        print(f"logslash v{__version__}")
        return 0
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return args.func(args)
PYEOF
mv logslash/cli.py.tmp logslash/cli.py

# 2. SỬA LỖI PARSER CRASH KHI GẶP DÒNG HỎNG (Error Handling)
cat > logslash/parsers/registry.py << 'PYEOF'
import sys
from logslash.detector import detect_format
from logslash.parsers.json_parser import parse_json
from logslash.parsers.plain_parser import parse_plain
from logslash.parsers.syslog_parser import parse_syslog

PARSERS = {
    "json": parse_json,
    "syslog": parse_syslog,
}

def parse_line(line, regex_parser=None):
    if not line or not line.strip():
        return None

    fmt = detect_format(line)
    parser = PARSERS.get(fmt)

    try:
        if parser is not None:
            result = parser(line)
            if result is not None:
                return result

        if regex_parser is not None:
            result = regex_parser.parse(line)
            if result is not None:
                return result
    except Exception:
        # Bắt mọi lỗi parse (JSON hỏng, lỗi regex...) để không crash
        return None

    return parse_plain(line)

def parse_file(lines, regex_parser=None, ignore_errors=True):
    records = []
    for line in lines:
        try:
            rec = parse_line(line, regex_parser=regex_parser)
            if rec is not None:
                records.append(rec)
        except Exception as e:
            if not ignore_errors:
                raise e
            # Nếu ignore_errors=True thì lặng lẽ bỏ qua dòng hỏng
            pass
    return records
PYEOF

# 3. TỰ ĐỘNG TẮT MÀU KHI PIPE (Themes)
# Sửa table_out.py và pretty_out.py để auto-detect
python - << 'PYEOF'
import re

# Sửa table_out
with open("logslash/outputs/table_out.py", "r") as f:
    content = f.read()
    content = content.replace(
        'if use_color is None:\n        use_color = hasattr(stream, "isatty") and stream.isatty()',
        'if use_color is None:\n        # Tự động tắt màu nếu đang pipe ra file\n        use_color = hasattr(stream, "isatty") and stream.isatty()'
    )
    # Thêm tham số use_color vào hàm output_table nếu chưa có
    if "def output_table(records, stream, use_color=None, max_width=60):" not in content:
        content = re.sub(r"def output_table\(records, stream.*?\):", "def output_table(records, stream, use_color=None, max_width=60):", content)
    with open("logslash/outputs/table_out.py", "w") as f:
        f.write(content)

# Sửa pretty_out
with open("logslash/outputs/pretty_out.py", "r") as f:
    content = f.read()
    content = content.replace(
        'if use_color is None:\n        use_color = hasattr(stream, "isatty") and stream.isatty()',
        'if use_color is None:\n        use_color = hasattr(stream, "isatty") and stream.isatty()'
    )
    with open("logslash/outputs/pretty_out.py", "w") as f:
        f.write(content)
PYEOF

echo "✅ Đã nâng cấp xong code!"

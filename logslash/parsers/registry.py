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

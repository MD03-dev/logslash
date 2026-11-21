from logslash.detector import detect_format
from logslash.parsers.json_parser import parse_json
from logslash.parsers.plain_parser import parse_plain
from logslash.parsers.syslog_parser import parse_syslog

PARSERS = {"json": parse_json, "syslog": parse_syslog}

def parse_line(line, regex_parser=None):
    if not line or not line.strip(): return None
    fmt = detect_format(line)
    parser = PARSERS.get(fmt)
    try:
        if parser:
            res = parser(line)
            if res: return res
        if regex_parser:
            res = regex_parser.parse(line)
            if res: return res
    except Exception:
        return None
    return parse_plain(line)

# Thay đổi: Trả về Generator thay vì list
def parse_file(lines, regex_parser=None, ignore_errors=True):
    for line in lines:
        rec = parse_line(line, regex_parser)
        if rec is not None:
            yield rec

"""Registry dispatch parser theo format."""

from logslash.detector import detect_format
from logslash.parsers.json_parser import parse_json
from logslash.parsers.plain_parser import parse_plain
from logslash.parsers.syslog_parser import parse_syslog

# plain KHÔNG nằm trong PARSERS vì nó là fallback cuối cùng.
PARSERS = {
    "json": parse_json,
    "syslog": parse_syslog,
}


def parse_line(line, regex_parser=None):
    """Detect format rồi dispatch parser.

    Thứ tự ưu tiên:
    1. json/syslog parser (nếu detect được)
    2. regex_parser (nếu user cung cấp)
    3. plain parser (fallback)
    """
    if not line or not line.strip():
        return None

    fmt = detect_format(line)
    parser = PARSERS.get(fmt)

    if parser is not None:
        result = parser(line)
        if result is not None:
            return result

    if regex_parser is not None:
        result = regex_parser.parse(line)
        if result is not None:
            return result

    return parse_plain(line)


def parse_file(lines, regex_parser=None):
    """Parse toàn bộ file, trả về list record. Bỏ qua dòng None."""
    records = []
    for line in lines:
        rec = parse_line(line, regex_parser=regex_parser)
        if rec is not None:
            records.append(rec)
    return records

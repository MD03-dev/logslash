"""Các parser cho từng format log.

Mỗi parser là 1 function nhận str, trả về dict theo schema chung:
- timestamp, level, source, message, raw, format, extra
"""

from logslash.parsers.json_parser import parse_json
from logslash.parsers.plain_parser import parse_plain
from logslash.parsers.registry import parse_line, PARSERS

__all__ = ["parse_json", "parse_plain", "parse_line", "PARSERS"]

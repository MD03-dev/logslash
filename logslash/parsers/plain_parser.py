"""Parser cho log dạng plain text.

Plain text không có cấu trúc cố định, nên parser này:
- Cố gắng đoán level nếu dòng bắt đầu bằng [INFO], [WARN], ERROR:, v.v.
- Cố gắng đoán timestamp nếu dòng bắt đầu bằng ISO date
- Còn lại đưa nguyên dòng vào message
"""

import re

from logslash.parsers.base import make_record

# [INFO] ... hoặc [WARN] ...
BRACKET_LEVEL = re.compile(r"^\[(?P<level>[A-Za-z]+)\]\s*(?P<rest>.*)$")

# INFO: ... hoặc ERROR: ...
PREFIX_LEVEL = re.compile(r"^(?P<level>[A-Za-z]+):\s+(?P<rest>.*)$")

# 2025-01-05T12:00:00 hoặc 2025-01-05 12:00:00
ISO_TIMESTAMP = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s+"
    r"(?P<rest>.*)$"
)

VALID_LEVELS = {
    "trace", "debug", "info", "information", "notice",
    "warn", "warning", "error", "err", "critical", "crit",
    "fatal", "emerg", "alert", "emergency",
}


def parse_plain(line):
    """Parse 1 dòng plain text log.

    Args:
        line: str

    Returns:
        dict record (luôn trả về, không None, vì plain là fallback)

    Ví dụ:
        >>> r = parse_plain("[INFO] server started")
        >>> r["level"]
        'info'
        >>> r["message"]
        'server started'

        >>> r = parse_plain("2025-01-05T12:00:00Z hello")
        >>> r["timestamp"]
        '2025-01-05T12:00:00Z'
    """
    raw = line.rstrip("\n")
    stripped = raw.strip()

    if not stripped:
        return make_record(fmt="plain", raw=raw, message="")

    level = None
    timestamp = None
    rest = stripped

    # Thử timestamp ISO ở đầu
    m_ts = ISO_TIMESTAMP.match(rest)
    if m_ts:
        timestamp = m_ts.group("ts")
        rest = m_ts.group("rest").strip()

    # Thử level dạng [INFO]
    m_br = BRACKET_LEVEL.match(rest)
    if m_br and m_br.group("level").lower() in VALID_LEVELS:
        level = m_br.group("level")
        rest = m_br.group("rest").strip()
    else:
        # Thử level dạng INFO:
        m_pf = PREFIX_LEVEL.match(rest)
        if m_pf and m_pf.group("level").lower() in VALID_LEVELS:
            level = m_pf.group("level")
            rest = m_pf.group("rest").strip()

    return make_record(
        fmt="plain",
        raw=raw,
        message=rest,
        timestamp=timestamp,
        level=level,
    )

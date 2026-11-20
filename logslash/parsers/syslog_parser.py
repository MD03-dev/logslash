"""Parser cho syslog RFC 3164.

Format chuẩn:
    Mon DD HH:MM:SS hostname process[pid]: message

Ví dụ:
    Jan  5 12:00:00 myhost sshd[1234]: Accepted password for user

Lưu ý:
- Không có năm trong timestamp → gán năm hiện tại
- Mon DD có thể có 1 hoặc 2 space ở giữa (Jan  5 vs Jan 15)
- process có thể không có [pid]
"""

import re
from datetime import datetime

from logslash.parsers.base import make_record

SYSLOG_PATTERN = re.compile(
    r"^(?P<month>[A-Z][a-z]{2})\s+"
    r"(?P<day>\d{1,2})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<host>\S+)\s+"
    r"(?P<process>[^:\[]+?)"
    r"(?:\[(?P<pid>\d+)\])?:\s*"
    r"(?P<message>.*)$"
)

MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def _build_timestamp(month, day, time_str):
    """Ghép Mon DD HH:MM:SS thành ISO timestamp với năm hiện tại.

    Trả về str ISO hoặc None nếu không hợp lệ.
    """
    try:
        month_num = MONTHS.get(month)
        if month_num is None:
            return None
        day_num = int(day)
        h, m, s = (int(x) for x in time_str.split(":"))
        year = datetime.now().year
        dt = datetime(year, month_num, day_num, h, m, s)
        return dt.isoformat()
    except (ValueError, KeyError):
        return None


def parse_syslog(line):
    """Parse 1 dòng syslog RFC 3164.

    Args:
        line: str

    Returns:
        dict record, hoặc None nếu không khớp pattern
    """
    stripped = line.strip()
    m = SYSLOG_PATTERN.match(stripped)
    if not m:
        return None

    timestamp = _build_timestamp(m.group("month"), m.group("day"), m.group("time"))
    process = m.group("process").strip()
    pid = m.group("pid")

    extra = {}
    if pid is not None:
        extra["pid"] = int(pid)
    extra["process"] = process
    extra["host"] = m.group("host")

    return make_record(
        fmt="syslog",
        raw=line.rstrip("\n"),
        message=m.group("message"),
        timestamp=timestamp,
        level=None,  # RFC 3164 không có level chuẩn
        source=m.group("host"),
        extra=extra,
    )

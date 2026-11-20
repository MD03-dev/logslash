"""Detect format của log line.

Ưu tiên dùng C module nếu có, nhưng LUÔN verify lại bằng Python
để đảm bảo kết quả chính xác (C chỉ là fast path).
"""

import json
import re

try:
    from logslash import cdetect
except ImportError:
    cdetect = None

SYSLOG_PATTERN = re.compile(
    r"^(?P<month>[A-Z][a-z]{2})\s+"
    r"(?P<day>\d{1,2})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<host>\S+)\s+"
    r"(?P<process>[^:\[]+)"
    r"(?:\[(?P<pid>\d+)\])?:\s*"
    r"(?P<message>.*)$"
)

FORMAT_JSON = "json"
FORMAT_SYSLOG = "syslog"
FORMAT_PLAIN = "plain"


def _detect_python(line):
    """Detect format bằng Python thuần."""
    if not line or not line.strip():
        return FORMAT_PLAIN

    stripped = line.strip()

    if stripped.startswith("{"):
        try:
            json.loads(stripped)
            return FORMAT_JSON
        except (json.JSONDecodeError, ValueError):
            pass

    if SYSLOG_PATTERN.match(stripped):
        return FORMAT_SYSLOG

    return FORMAT_PLAIN


def detect_format(line):
    """Detect format của 1 dòng log.

    Chiến lược: C làm fast path, nhưng LUÔN verify bằng Python.
    """
    if not line or not line.strip():
        return FORMAT_PLAIN

    if cdetect is not None:
        c_result = cdetect.detect_format_c(line)

        if c_result == FORMAT_JSON:
            try:
                json.loads(line.strip())
                return FORMAT_JSON
            except (json.JSONDecodeError, ValueError):
                return _detect_python(line)

        if c_result == FORMAT_SYSLOG:
            if SYSLOG_PATTERN.match(line.strip()):
                return FORMAT_SYSLOG
            return _detect_python(line)

        # C nói plain: vẫn verify để không bỏ sót syslog
        return _detect_python(line)

    return _detect_python(line)


def detect_file_format(lines):
    """Detect format chủ đạo của cả file."""
    if not lines:
        return FORMAT_PLAIN
    return _detect_file_python(lines)


def _detect_file_python(lines):
    counts = {FORMAT_JSON: 0, FORMAT_SYSLOG: 0, FORMAT_PLAIN: 0}
    total = 0
    for line in lines:
        if not line.strip():
            continue
        counts[_detect_python(line)] += 1
        total += 1
    if total == 0:
        return FORMAT_PLAIN
    return max(counts, key=counts.get)

"""Parser cho log dạng JSON (mỗi dòng là 1 object JSON)."""

import json

from logslash.parsers.base import make_record

# Các key thường gặp cho từng field, ưu tiên theo thứ tự
TIMESTAMP_KEYS = ("timestamp", "time", "ts", "@timestamp", "datetime", "date")
LEVEL_KEYS = ("level", "severity", "lvl", "loglevel", "log_level")
SOURCE_KEYS = ("source", "logger", "service", "host", "hostname", "app")
MESSAGE_KEYS = ("message", "msg", "text", "log", "event")


def _pick(d, keys):
    """Lấy value đầu tiên có trong dict theo danh sách key ưu tiên."""
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def parse_json(line):
    """Parse 1 dòng JSON log thành record chuẩn.

    Args:
        line: str, 1 dòng JSON

    Returns:
        dict record, hoặc None nếu không parse được

    Ví dụ:
        >>> r = parse_json('{"level":"info","msg":"ok","ts":"2025-01-05T12:00:00Z"}')
        >>> r["level"]
        'info'
        >>> r["message"]
        'ok'
        >>> r["format"]
        'json'
    """
    stripped = line.strip()
    if not stripped:
        return None

    try:
        data = json.loads(stripped)
    except (json.JSONDecodeError, ValueError):
        return None

    # Chỉ nhận object, không nhận array hay scalar
    if not isinstance(data, dict):
        return None

    timestamp = _pick(data, TIMESTAMP_KEYS)
    level = _pick(data, LEVEL_KEYS)
    source = _pick(data, SOURCE_KEYS)
    message = _pick(data, MESSAGE_KEYS)

    # Nếu message không phải str, ép về str
    if message is not None and not isinstance(message, str):
        message = str(message)

    # Các field còn lại (không thuộc 4 nhóm trên) đưa vào extra
    known = set(TIMESTAMP_KEYS) | set(LEVEL_KEYS) | set(SOURCE_KEYS) | set(MESSAGE_KEYS)
    extra = {k: v for k, v in data.items() if k not in known}

    return make_record(
        fmt="json",
        raw=stripped,
        message=message or "",
        timestamp=str(timestamp) if timestamp is not None else None,
        level=level,
        source=str(source) if source is not None else None,
        extra=extra,
    )

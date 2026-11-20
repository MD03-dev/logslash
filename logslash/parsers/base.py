"""Schema chung cho mọi parser.

Mọi parser phải trả về dict có đủ các key trong BASE_SCHEMA.
Key nào không có dữ liệu thì để None (trừ message/raw/format/extra).
"""

BASE_SCHEMA = {
    "timestamp": None,
    "level": None,
    "source": None,
    "message": "",
    "raw": "",
    "format": "",
    "extra": {},
}

# Map các tên level khác nhau về 1 chuẩn
LEVEL_ALIASES = {
    "warning": "warn",
    "warn": "warn",
    "error": "error",
    "err": "error",
    "critical": "critical",
    "crit": "critical",
    "fatal": "critical",
    "info": "info",
    "information": "info",
    "debug": "debug",
    "trace": "trace",
    "notice": "notice",
    "emerg": "critical",
    "emergency": "critical",
    "alert": "critical",
}


def normalize_level(level):
    """Chuẩn hóa tên level.

    Args:
        level: str hoặc None

    Returns:
        str chuẩn hoặc None

    Ví dụ:
        >>> normalize_level("WARNING")
        'warn'
        >>> normalize_level("Critical")
        'critical'
        >>> normalize_level(None) is None
        True
    """
    if level is None:
        return None
    key = str(level).strip().lower()
    return LEVEL_ALIASES.get(key, key)


def make_record(fmt, raw, message="", timestamp=None, level=None,
                source=None, extra=None):
    """Tạo record chuẩn từ các field rời.

    Dùng để đảm bảo mọi parser trả về cùng schema.
    """
    record = dict(BASE_SCHEMA)
    record["format"] = fmt
    record["raw"] = raw
    record["message"] = message or ""
    record["timestamp"] = timestamp
    record["level"] = normalize_level(level)
    record["source"] = source
    record["extra"] = extra or {}
    return record

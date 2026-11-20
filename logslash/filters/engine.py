"""Filter engine: lọc record theo nhiều điều kiện.

Thiết kế:
- Mỗi điều kiện là 1 function nhận record → bool
- Filter là list các điều kiện, kết hợp bằng AND
- build_filter() nhận tham số CLI, trả về Filter
- apply_filter() chạy Filter trên list record

Điều kiện hỗ trợ:
- level: khớp chính xác level (info/warn/error/...)
- level_min: level >= ngưỡng (theo thứ tự trace<debug<info<warn<error<critical)
- source: khớp substring source
- contains: message chứa substring
- not_contains: message KHÔNG chứa substring
- since: timestamp >= mốc (so sánh string ISO)
- until: timestamp <= mốc
- format: khớp format (json/syslog/plain/regex:*)
"""

import re

LEVEL_ORDER = {
    "trace": 0,
    "debug": 1,
    "info": 2,
    "notice": 3,
    "warn": 4,
    "error": 5,
    "critical": 6,
}


class FilterError(ValueError):
    """Lỗi cấu hình filter."""


class Filter:
    """Tập hợp điều kiện lọc, kết hợp AND."""

    def __init__(self):
        self.conditions = []
        self.descriptions = []

    def add(self, func, desc):
        """Thêm 1 điều kiện."""
        self.conditions.append(func)
        self.descriptions.append(desc)
        return self

    def match(self, record):
        """Trả về True nếu record thỏa TẤT CẢ điều kiện."""
        for cond in self.conditions:
            if not cond(record):
                return False
        return True

    def apply(self, records):
        """Lọc list record."""
        return [r for r in records if self.match(r)]

    def __bool__(self):
        return len(self.conditions) > 0

    def __repr__(self):
        if not self.conditions:
            return "Filter(<empty>)"
        return f"Filter({', '.join(self.descriptions)})"


def _make_level_eq(level):
    target = level.lower()
    def cond(rec):
        return (rec.get("level") or "").lower() == target
    return cond


def _make_level_min(level):
    if level.lower() not in LEVEL_ORDER:
        raise FilterError(f"level_min không hợp lệ: '{level}'")
    threshold = LEVEL_ORDER[level.lower()]
    def cond(rec):
        lv = (rec.get("level") or "").lower()
        if lv not in LEVEL_ORDER:
            return False
        return LEVEL_ORDER[lv] >= threshold
    return cond


def _make_source(substr):
    sub = substr.lower()
    def cond(rec):
        src = rec.get("source") or ""
        return sub in src.lower()
    return cond


def _make_contains(substr):
    sub = substr.lower()
    def cond(rec):
        return sub in (rec.get("message") or "").lower()
    return cond


def _make_not_contains(substr):
    sub = substr.lower()
    def cond(rec):
        return sub not in (rec.get("message") or "").lower()
    return cond


def _make_since(ts):
    def cond(rec):
        rt = rec.get("timestamp")
        return rt is not None and rt >= ts
    return cond


def _make_until(ts):
    def cond(rec):
        rt = rec.get("timestamp")
        return rt is not None and rt <= ts
    return cond


def _make_format(fmt):
    def cond(rec):
        rf = rec.get("format") or ""
        if fmt.endswith("*"):
            return rf.startswith(fmt[:-1])
        return rf == fmt
    return cond


def build_filter(args):
    """Xây Filter từ argparse args.

    Args:
        args: object có các attribute level, level_min, source,
              contains, not_contains, since, until, format
              (giá trị None = không dùng điều kiện đó)

    Returns:
        Filter (có thể rỗng nếu không có điều kiện nào)

    Raises:
        FilterError nếu tham số không hợp lệ
    """
    f = Filter()

    level = getattr(args, "level", None)
    if level:
        f.add(_make_level_eq(level), f"level={level}")

    level_min = getattr(args, "level_min", None)
    if level_min:
        f.add(_make_level_min(level_min), f"level_min={level_min}")

    source = getattr(args, "source", None)
    if source:
        f.add(_make_source(source), f"source~{source}")

    contains = getattr(args, "contains", None)
    if contains:
        f.add(_make_contains(contains), f"contains~{contains}")

    not_contains = getattr(args, "not_contains", None)
    if not_contains:
        f.add(_make_not_contains(not_contains), f"!contains~{not_contains}")

    since = getattr(args, "since", None)
    if since:
        f.add(_make_since(since), f"since>={since}")

    until = getattr(args, "until", None)
    if until:
        f.add(_make_until(until), f"until<={until}")

    fmt = getattr(args, "format", None)
    if fmt:
        f.add(_make_format(fmt), f"format={fmt}")

    return f


def apply_filter(records, filter_obj):
    """Áp filter lên list record. Nếu filter rỗng, trả nguyên list."""
    if not filter_obj:
        return records
    return filter_obj.apply(records)

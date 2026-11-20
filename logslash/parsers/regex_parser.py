"""Parser dùng regex do user tự định nghĩa.

User cung cấp file JSON chứa danh sách pattern:
{
    "patterns": [
        {
            "name": "myapp",
            "regex": "^(?P<timestamp>\\\\S+) (?P<level>\\\\w+) (?P<message>.*)$"
        }
    ]
}

Parser sẽ thử từng pattern theo thứ tự, pattern nào khớp trước thì dùng.
Named group được map vào record:
- timestamp, level, source, message → field tương ứng
- các group khác → extra
"""

import json
import re

from logslash.parsers.base import make_record


class RegexParser:
    """Parser dùng danh sách regex pattern."""

    def __init__(self, patterns):
        """Khởi tạo từ list dict pattern.

        Args:
            patterns: list[dict] với key "name" (str) và "regex" (str)
        """
        self.patterns = []
        for p in patterns:
            name = p.get("name", "unnamed")
            try:
                compiled = re.compile(p["regex"])
            except (re.error, KeyError) as e:
                raise ValueError(f"Pattern '{name}' không hợp lệ: {e}")
            self.patterns.append((name, compiled))

    @classmethod
    def from_file(cls, path):
        """Load pattern từ file JSON."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "patterns" not in data or not isinstance(data["patterns"], list):
            raise ValueError("File pattern phải có key 'patterns' là list")
        return cls(data["patterns"])

    def parse(self, line):
        """Thử từng pattern, trả về record đầu tiên khớp.

        Returns:
            dict record hoặc None nếu không pattern nào khớp
        """
        stripped = line.strip()
        if not stripped:
            return None

        for name, pattern in self.patterns:
            m = pattern.match(stripped)
            if not m:
                continue

            groups = m.groupdict()
            timestamp = groups.pop("timestamp", None)
            level = groups.pop("level", None)
            source = groups.pop("source", None)
            message = groups.pop("message", "")

            extra = dict(groups)
            extra["pattern_name"] = name

            return make_record(
                fmt=f"regex:{name}",
                raw=line.rstrip("\n"),
                message=message or "",
                timestamp=timestamp,
                level=level,
                source=source,
                extra=extra,
            )

        return None


def load_regex_parser(path):
    """Wrapper tiện dụng: load RegexParser từ file, trả về None nếu lỗi."""
    try:
        return RegexParser.from_file(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return None

"""Output dạng bảng ASCII.

Cột: TIME | LEVEL | SOURCE | MESSAGE
- TIME rút gọn (bỏ date nếu cùng ngày, chỉ giữ HH:MM:SS)
- LEVEL có màu ANSI (đỏ error, vàng warn, xanh info, xám debug)
- Cột tự co giãn theo nội dung, có giới hạn max width
"""

import sys

# Mã màu ANSI
COLORS = {
    "trace": "\033[90m",     # xám đậm
    "debug": "\033[90m",     # xám
    "info": "\033[36m",      # cyan
    "notice": "\033[34m",    # xanh dương
    "warn": "\033[33m",      # vàng
    "error": "\033[31m",     # đỏ
    "critical": "\033[1;31m",  # đỏ đậm
}
RESET = "\033[0m"
DIM = "\033[2m"

DEFAULT_MAX_WIDTH = 60
DEFAULT_COLS = ["timestamp", "level", "source", "message"]


def _short_time(ts):
    """Rút gọn timestamp: bỏ date nếu có dạng YYYY-MM-DDTHH:MM:SS."""
    if not ts:
        return "-"
    s = str(ts)
    # 2025-01-05T12:00:05Z -> 12:00:05
    if "T" in s:
        time_part = s.split("T", 1)[1]
        if time_part.endswith("Z"):
            time_part = time_part[:-1]
        return time_part
    # 2025-01-05 12:00:05 -> 12:00:05
    if " " in s and s[4:5] == "-":
        return s.split(" ", 1)[1]
    return s


def _colorize_level(level, use_color):
    if not level:
        return "-"
    lv = str(level).lower()
    if not use_color:
        return lv
    color = COLORS.get(lv, "")
    if not color:
        return lv
    return f"{color}{lv}{RESET}"


def _truncate(s, max_width):
    s = str(s) if s is not None else ""
    if len(s) <= max_width:
        return s
    return s[: max_width - 1] + "…"


def _visible_len(s):
    """Độ dài hiển thị, bỏ qua ANSI escape."""
    import re
    return len(re.sub(r"\033\[[0-9;]*m", "", s))


def _pad(s, width):
    """Pad phải cho đủ width, tính theo visible length."""
    return s + " " * max(0, width - _visible_len(s))


def output_table(records, stream, use_color=None, max_width=60):
    """In bảng ASCII.

    Args:
        records: list[dict]
        stream: file-like object (mặc định sys.stdout)
        use_color: bool hoặc None. None = tự detect TTY.
        max_width: độ rộng tối đa cột message
    """
    if use_color is None:
        # Tự động tắt màu nếu đang pipe ra file
        use_color = hasattr(stream, "isatty") and stream.isatty()

    if not records:
        stream.write("(không có record)\n")
        return

    # Chuẩn bị dữ liệu từng dòng
    rows = []
    for rec in records:
        rows.append({
            "timestamp": _short_time(rec.get("timestamp")),
            "level": rec.get("level") or "-",
            "source": rec.get("source") or "-",
            "message": _truncate(rec.get("message") or "", max_width),
        })

    # Tính width từng cột
    widths = {}
    for col in DEFAULT_COLS:
        w = max(len(col.upper()), max(_visible_len(r[col]) for r in rows))
        widths[col] = min(w, max_width)

    # Header
    header = "  ".join(_pad(c.upper(), widths[c]) for c in DEFAULT_COLS)
    stream.write(header + "\n")
    stream.write("-" * _visible_len(header) + "\n")

    # Data rows
    for r in rows:
        line = "  ".join([
            _pad(r["timestamp"], widths["timestamp"]),
            _pad(_colorize_level(r["level"], use_color), widths["level"]),
            _pad(_truncate(r["source"], widths["source"]), widths["source"]),
            _pad(r["message"], widths["message"]),
        ])
        stream.write(line.rstrip() + "\n")

    # Footer
    stream.write("-" * _visible_len(header) + "\n")
    stream.write(f"{len(records)} record\n")

"""Output JSON có màu syntax highlight.

Nếu terminal không hỗ trợ màu (không phải TTY), fallback về JSON thường.
"""

import json

RESET = "\033[0m"
KEY_COLOR = "\033[34m"
STR_COLOR = "\033[32m"
NUM_COLOR = "\033[33m"
BOOL_COLOR = "\033[35m"


def _fmt(obj, indent, use_color):
    sp = "  " * indent
    sp_in = "  " * (indent + 1)

    if isinstance(obj, dict):
        if not obj:
            return "{}"
        parts = []
        for k, v in obj.items():
            key_str = json.dumps(k, ensure_ascii=False)
            if use_color:
                key_str = f"{KEY_COLOR}{key_str}{RESET}"
            parts.append(f"{sp_in}{key_str}: {_fmt(v, indent + 1, use_color)}")
        return "{\n" + ",\n".join(parts) + f"\n{sp}}}"

    if isinstance(obj, list):
        if not obj:
            return "[]"
        parts = [f"{sp_in}{_fmt(v, indent + 1, use_color)}" for v in obj]
        return "[\n" + ",\n".join(parts) + f"\n{sp}]"

    # scalar: dùng json.dumps để escape đúng chuẩn
    s = json.dumps(obj, ensure_ascii=False)
    if not use_color:
        return s
    if isinstance(obj, str):
        return f"{STR_COLOR}{s}{RESET}"
    if isinstance(obj, bool) or obj is None:
        return f"{BOOL_COLOR}{s}{RESET}"
    if isinstance(obj, (int, float)):
        return f"{NUM_COLOR}{s}{RESET}"
    return s


def output_pretty(records, stream, use_color=None):
    """In JSON có màu."""
    if use_color is None:
        use_color = hasattr(stream, "isatty") and stream.isatty()
    stream.write(_fmt(records, 0, use_color))
    stream.write("\n")

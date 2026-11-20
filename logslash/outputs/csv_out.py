"""Output CSV để mở Excel / Google Sheets."""

import csv

DEFAULT_COLS = ["timestamp", "level", "source", "message", "format", "raw"]


def _flatten_extra(extra, prefix="extra."):
    """Flatten dict extra thành các cột riêng."""
    out = {}
    if not isinstance(extra, dict):
        return out
    for k, v in extra.items():
        out[prefix + k] = v
    return out


def output_csv(records, stream, columns=None):
    """In CSV với header.

    Args:
        records: list[dict]
        stream: file-like object
        columns: list[str] tùy chọn. Nếu None, dùng DEFAULT_COLS
                 + tất cả extra.* xuất hiện.
    """
    if not records:
        # Vẫn in header rỗng để downstream tool khỏi vỡ
        writer = csv.writer(stream)
        writer.writerow(columns or DEFAULT_COLS)
        return

    if columns is None:
        # Tự build cột: DEFAULT_COLS + mọi extra.* có trong bất kỳ record nào
        extra_keys = set()
        for rec in records:
            extra_keys.update(_flatten_extra(rec.get("extra") or {}).keys())
        columns = DEFAULT_COLS + sorted(extra_keys)

    writer = csv.writer(stream, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    writer.writerow(columns)

    for rec in records:
        row = []
        flat_extra = _flatten_extra(rec.get("extra") or {})
        for col in columns:
            if col in rec:
                v = rec[col]
            elif col in flat_extra:
                v = flat_extra[col]
            else:
                v = ""
            if isinstance(v, (dict, list)):
                import json
                v = json.dumps(v, ensure_ascii=False)
            row.append("" if v is None else v)
        writer.writerow(row)

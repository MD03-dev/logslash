"""Output JSON và NDJSON."""

import json


def output_json(records, stream):
    """In JSON array pretty indent 2."""
    json.dump(records, stream, ensure_ascii=False, indent=2)
    stream.write("\n")


def output_ndjson(records, stream):
    """In mỗi record 1 dòng JSON."""
    for rec in records:
        stream.write(json.dumps(rec, ensure_ascii=False))
        stream.write("\n")

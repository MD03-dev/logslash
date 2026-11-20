"""Output formatters cho logslash."""

from logslash.outputs.json_out import output_json, output_ndjson
from logslash.outputs.table_out import output_table
from logslash.outputs.csv_out import output_csv
from logslash.outputs.pretty_out import output_pretty

OUTPUTS = {
    "json": output_json,
    "ndjson": output_ndjson,
    "table": output_table,
    "csv": output_csv,
    "pretty": output_pretty,
}

__all__ = ["OUTPUTS", "output_json", "output_ndjson",
           "output_table", "output_csv", "output_pretty"]

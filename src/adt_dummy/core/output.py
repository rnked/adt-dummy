"""Output formatting helpers."""

import csv
import io
import json

from tabulate import tabulate


def format_table(columns, rows):
    return tabulate(rows, headers=columns, tablefmt="github")


def format_csv(columns, rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(columns)
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def format_json(columns, rows):
    data = [dict(zip(columns, row)) for row in rows]
    return json.dumps(data, indent=2, default=str)


def format_output(columns, rows, fmt):
    if fmt == "table":
        return format_table(columns, rows)
    if fmt == "csv":
        return format_csv(columns, rows)
    if fmt == "json":
        return format_json(columns, rows)
    raise ValueError(f"Unsupported format: {fmt}")

import json

from adt_dummy.core import output


def test_format_table():
    columns = ["a", "b"]
    rows = [(1, "x"), (2, "y")]
    rendered = output.format_output(columns, rows, "table")
    assert "a" in rendered
    assert "b" in rendered
    assert "1" in rendered


def test_format_csv():
    columns = ["a", "b"]
    rows = [(1, "x")]
    rendered = output.format_output(columns, rows, "csv")
    normalized = rendered.replace("\r\n", "\n")
    assert normalized == "a,b\n1,x\n"


def test_format_json():
    columns = ["a", "b"]
    rows = [(1, "x")]
    rendered = output.format_output(columns, rows, "json")
    data = json.loads(rendered)
    assert data == [{"a": 1, "b": "x"}]

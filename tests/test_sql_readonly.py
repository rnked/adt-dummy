import pytest

from adt_dummy.services import trino


def test_read_only_allows_select_and_with():
    assert trino.is_read_only_sql("SELECT 1")
    assert trino.is_read_only_sql("WITH t AS (SELECT 1) SELECT * FROM t")


def test_read_only_allows_session_commands():
    assert trino.is_read_only_sql("SET SESSION foo = 'bar'")
    assert trino.is_read_only_sql("RESET SESSION foo")


def test_read_only_rejects_destructive():
    assert not trino.is_read_only_sql("INSERT INTO t VALUES (1)")
    assert not trino.is_read_only_sql("DROP TABLE t")
    assert not trino.is_read_only_sql("SELECT 1; DELETE FROM t")
    assert not trino.is_read_only_sql("WITH t AS (SELECT 1) INSERT INTO x SELECT * FROM t")


def test_read_only_ignores_strings_and_comments():
    assert trino.is_read_only_sql("SELECT 'DELETE' AS word")
    assert trino.is_read_only_sql("-- DROP TABLE\nSELECT 1")


def test_read_only_allows_keyword_as_identifier():
    assert trino.is_read_only_sql("SELECT comment FROM t")


def test_read_only_blocks_set_role():
    assert not trino.is_read_only_sql("SET ROLE admin")

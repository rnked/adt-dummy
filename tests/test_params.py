import pytest

from adt_dummy.core.errors import AppError
from adt_dummy.services import trino


def test_apply_params():
    params = trino.parse_params(["TABLE=foo", "VALUE=42"])
    sql = "SELECT * FROM {{TABLE}} WHERE id={{VALUE}}"
    assert trino.apply_params(sql, params) == "SELECT * FROM foo WHERE id=42"


def test_parse_params_rejects_invalid():
    with pytest.raises(AppError):
        trino.parse_params(["NOEQUALS"])

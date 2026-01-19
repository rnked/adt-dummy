"""Environment variable helpers."""

import os

from adt_dummy.core.errors import AppError

PREFIX = "ADT_DUMMY_"

TRUE_VALUES = {"1", "true", "yes", "y", "on"}
FALSE_VALUES = {"0", "false", "no", "n", "off"}


def _ensure_prefixed(name):
    if not name.startswith(PREFIX):
        raise ValueError(f"Env var must start with {PREFIX}: {name}")


def get_env(name, default=None, required=False):
    _ensure_prefixed(name)
    value = os.getenv(name)
    if value is None or value == "":
        if required:
            raise AppError(f"Missing required environment variable: {name}")
        return default
    return value


def get_int_env(name, default=None, required=False):
    value = get_env(name, default=default, required=required)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise AppError(f"Invalid integer for {name}: {value}") from exc


def get_bool_env(name, default=False):
    value = get_env(name, default=None)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise AppError(f"Invalid boolean for {name}: {value}. Use true/false.")


def is_in_cluster():
    return get_bool_env("ADT_DUMMY_IN_CLUSTER", default=False)

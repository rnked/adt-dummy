"""Trino query execution and SQL safety checks."""

import re

from trino.auth import BasicAuthentication
from trino.dbapi import connect

from adt_dummy.core import env
from adt_dummy.core.errors import AppError

ALLOWED_START = {
    "SELECT",
    "WITH",
    "SHOW",
    "DESCRIBE",
    "EXPLAIN",
    "VALUES",
    "USE",
}

FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "MERGE",
    "CREATE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "GRANT",
    "REVOKE",
    "CALL",
    "COMMENT",
    "RENAME",
}

FORBIDDEN_PHRASES = {
    "SET ROLE",
    "RESET ROLE",
}


def parse_params(param_pairs):
    params = {}
    for item in param_pairs:
        if "=" not in item:
            raise AppError(f"Invalid --param value: {item}. Use KEY=VALUE.")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise AppError(f"Invalid --param value: {item}. Use KEY=VALUE.")
        params[key] = value
    return params


def apply_params(sql, params):
    for key, value in params.items():
        sql = sql.replace("{{" + key + "}}", value)
    return sql


def split_sql_statements(sql):
    statements = []
    buffer = []
    in_single = False
    in_double = False
    in_line_comment = False
    in_block_comment = False
    i = 0
    while i < len(sql):
        ch = sql[i]
        nxt = sql[i + 1] if i + 1 < len(sql) else ""

        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
            i += 1
            continue

        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue

        if in_single:
            if ch == "'" and nxt == "'":
                buffer.append(ch)
                buffer.append(nxt)
                i += 2
                continue
            if ch == "'":
                in_single = False
            buffer.append(ch)
            i += 1
            continue

        if in_double:
            if ch == '"':
                in_double = False
            buffer.append(ch)
            i += 1
            continue

        if ch == "-" and nxt == "-":
            in_line_comment = True
            i += 2
            continue

        if ch == "/" and nxt == "*":
            in_block_comment = True
            i += 2
            continue

        if ch == "'":
            in_single = True
            buffer.append(ch)
            i += 1
            continue

        if ch == '"':
            in_double = True
            buffer.append(ch)
            i += 1
            continue

        if ch == ";":
            statement = "".join(buffer).strip()
            if statement:
                statements.append(statement)
            buffer = []
            i += 1
            continue

        buffer.append(ch)
        i += 1

    trailing = "".join(buffer).strip()
    if trailing:
        statements.append(trailing)
    return statements


def strip_comments_and_strings(sql):
    output = []
    in_single = False
    in_double = False
    in_line_comment = False
    in_block_comment = False
    i = 0
    while i < len(sql):
        ch = sql[i]
        nxt = sql[i + 1] if i + 1 < len(sql) else ""

        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
                output.append(" ")
            i += 1
            continue

        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue

        if in_single:
            if ch == "'" and nxt == "'":
                i += 2
                continue
            if ch == "'":
                in_single = False
            i += 1
            continue

        if in_double:
            if ch == '"':
                in_double = False
            i += 1
            continue

        if ch == "-" and nxt == "-":
            output.append(" ")
            in_line_comment = True
            i += 2
            continue

        if ch == "/" and nxt == "*":
            output.append(" ")
            in_block_comment = True
            i += 2
            continue

        if ch == "'":
            output.append(" ")
            in_single = True
            i += 1
            continue

        if ch == '"':
            output.append(" ")
            in_double = True
            i += 1
            continue

        output.append(ch)
        i += 1

    return "".join(output)


def is_read_only_sql(sql):
    statements = split_sql_statements(sql)
    if not statements:
        return True

    for statement in statements:
        cleaned = strip_comments_and_strings(statement)
        upper = cleaned.upper()
        tokens = re.findall(r"[A-Z_]+", upper)
        if not tokens:
            continue

        first = tokens[0]
        second = tokens[1] if len(tokens) > 1 else ""

        if first == "SET" and second == "SESSION":
            pass
        elif first == "RESET" and second == "SESSION":
            pass
        elif first in ALLOWED_START:
            pass
        else:
            return False

        for phrase in FORBIDDEN_PHRASES:
            if phrase in upper:
                return False
        for keyword in FORBIDDEN_KEYWORDS:
            if re.search(rf"\b{keyword}\b", upper):
                return False

    return True


def ensure_read_only(sql):
    if not is_read_only_sql(sql):
        raise AppError(
            "Query rejected: read-only mode blocks DDL/DML. "
            "Use --allow-write to override."
        )


def _trino_connection():
    host = env.get_env("ADT_DUMMY_TRINO_HOST", required=True)
    port = env.get_int_env("ADT_DUMMY_TRINO_PORT", default=443)
    scheme = env.get_env("ADT_DUMMY_TRINO_HTTP_SCHEME", default="https")
    user = env.get_env("ADT_DUMMY_TRINO_USER", required=True)
    password = env.get_env("ADT_DUMMY_TRINO_PASSWORD", required=True)
    verify = env.get_bool_env("ADT_DUMMY_TRINO_VERIFY", default=False)

    auth = BasicAuthentication(user, password)
    return connect(host=host, port=port, user=user, http_scheme=scheme, auth=auth, verify=verify)


def execute_query(sql, max_rows=200):
    conn = _trino_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)

        columns = [desc[0] for desc in (cursor.description or [])]
        truncated = False

        if max_rows and max_rows > 0:
            rows = cursor.fetchmany(max_rows + 1)
            if len(rows) > max_rows:
                truncated = True
                rows = rows[:max_rows]
        else:
            rows = cursor.fetchall()

        return columns, rows, truncated
    finally:
        try:
            conn.close()
        except Exception:
            pass

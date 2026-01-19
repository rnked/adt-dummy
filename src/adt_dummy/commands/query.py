"""Query command."""

from pathlib import Path

import click

from adt_dummy.core.errors import AppError
from adt_dummy.core.output import format_output
from adt_dummy.local import proxy_to_remote
from adt_dummy.services import trino


def _load_sql(sql, file_path, stdin):
    sources = [bool(sql), bool(file_path), stdin]
    if sum(sources) != 1:
        raise AppError("Provide SQL via argument or --file.")

    if stdin:
        return click.get_text_stream("stdin").read()
    if file_path:
        return Path(file_path).read_text()
    return sql


def _validate_max_rows(max_rows):
    if max_rows is None:
        return
    if max_rows < 0:
        raise AppError("--max-rows must be >= 0")


def _run_query(sql_text, params, allow_write, fmt, output_path, max_rows):
    _validate_max_rows(max_rows)
    parsed_params = trino.parse_params(params)
    sql_text = trino.apply_params(sql_text, parsed_params)
    if not allow_write:
        trino.ensure_read_only(sql_text)

    columns, rows, truncated = trino.execute_query(sql_text, max_rows=max_rows)
    rendered = format_output(columns, rows, fmt)

    if output_path:
        Path(output_path).write_text(rendered)
        click.echo(f"Wrote {len(rows)} rows to {output_path}")
    else:
        click.echo(rendered)

    if truncated:
        click.echo(
            "Output truncated. Use --max-rows 0 to disable the limit.", err=True
        )


@click.command(name="query")
@click.option("-f", "--file", "file_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--format", "fmt", type=click.Choice(["table", "csv", "json"]), default="table")
@click.option("--output", "output_path", type=click.Path(dir_okay=False))
@click.option("--max-rows", type=int, default=200)
@click.option("--param", "params", multiple=True)
@click.option("--allow-write", is_flag=True, default=False)
@click.argument("sql", required=False)
@click.pass_context
def query_cmd(ctx, file_path, fmt, output_path, max_rows, params, allow_write, sql):
    if ctx.obj.get("in_cluster"):
        sql_text = _load_sql(sql, file_path, stdin=False)
        _run_query(sql_text, params, allow_write, fmt, output_path, max_rows)
        return

    sql_text = _load_sql(sql, file_path, stdin=False)
    remote_args = ["query", "--stdin", "--format", fmt, "--max-rows", str(max_rows)]
    if allow_write:
        remote_args.append("--allow-write")
    for item in params:
        remote_args += ["--param", item]

    output_text = proxy_to_remote(
        ["dami", "__remote"] + remote_args,
        stdin_data=sql_text,
        capture_output=bool(output_path),
    )

    if output_path:
        Path(output_path).write_text(output_text or "")
        click.echo(f"Wrote output to {output_path}")


@click.command(name="query")
@click.option("-f", "--file", "file_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--format", "fmt", type=click.Choice(["table", "csv", "json"]), default="table")
@click.option("--output", "output_path", type=click.Path(dir_okay=False))
@click.option("--max-rows", type=int, default=200)
@click.option("--param", "params", multiple=True)
@click.option("--allow-write", is_flag=True, default=False)
@click.option("--stdin", is_flag=True, hidden=True)
@click.argument("sql", required=False)
def query_remote_cmd(file_path, fmt, output_path, max_rows, params, allow_write, stdin, sql):
    sql_text = _load_sql(sql, file_path, stdin=stdin)
    _run_query(sql_text, params, allow_write, fmt, output_path, max_rows)

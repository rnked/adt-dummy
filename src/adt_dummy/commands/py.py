"""Python execution command."""

import os
import shlex
import tempfile
from pathlib import Path

import click

from adt_dummy.core.errors import AppError
from adt_dummy.local import proxy_to_remote
from adt_dummy.services import pyrunner


def _read_file(path):
    try:
        return Path(path).read_text()
    except OSError as exc:
        raise AppError(f"Failed to read file: {path}") from exc


def _edit_code():
    editor = os.getenv("ADT_DUMMY_EDITOR") or "vi"
    fd, path = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    try:
        command = shlex.split(editor) + [path]
        try:
            result = os.spawnvp(os.P_WAIT, command[0], command)
        except OSError as exc:
            raise AppError(f"Editor launch failed: {exc}") from exc
        if result != 0:
            raise AppError(f"Editor failed with exit code {result}")
        return _read_file(path)
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def _normalize_args(mode, path, args):
    if mode == "-" and path:
        return None, (path,) + tuple(args)
    return path, args


def _load_code(mode, path, stdin_flag):
    if stdin_flag or mode == "-":
        return click.get_text_stream("stdin").read()
    if mode == "run":
        if not path:
            raise AppError("Missing script path for 'py run'")
        if path == "-":
            return click.get_text_stream("stdin").read()
        return _read_file(path)
    if mode == "edit":
        return _edit_code()
    raise AppError("Mode must be one of: run, edit, -")


def _run_remote(mode, path, args, stdin_flag):
    code = _load_code(mode, path, stdin_flag)
    exit_code = pyrunner.run_code(code, args)
    raise SystemExit(exit_code)


@click.command(
    name="py",
    help="Run Python code inside the toolbox pod.",
    epilog=(
        "\b\n"
        "MODE can be: run, edit, - (stdin).\n"
        "Examples:\n"
        "  dami py run script.py -- arg1 arg2\n"
        "  cat script.py | dami py - -- arg1 arg2\n"
        "  dami py edit -- arg1 arg2\n"
    ),
)
@click.argument("mode", metavar="MODE")
@click.argument("path", required=False, metavar="PATH")
@click.argument("args", nargs=-1, type=click.UNPROCESSED, metavar="[ARGS]...")
@click.pass_context
def py_cmd(ctx, mode, path, args):
    path, args = _normalize_args(mode, path, args)

    if ctx.obj.get("in_cluster"):
        _run_remote(mode, path, args, stdin_flag=False)
        return

    if mode == "edit":
        code = _edit_code()
    elif mode == "run":
        if not path:
            raise AppError("Missing script path for 'py run'")
        if path == "-":
            code = click.get_text_stream("stdin").read()
        else:
            code = _read_file(path)
    elif mode == "-":
        code = click.get_text_stream("stdin").read()
    else:
        raise AppError("Mode must be one of: run, edit, -")

    remote_args = ["py", "--stdin", "run"]
    if args:
        remote_args.append("--")
        remote_args += list(args)

    proxy_to_remote(["dami", "__remote"] + remote_args, stdin_data=code)


@click.command(name="py", help="Run Python code inside the toolbox pod.")
@click.option("--stdin", is_flag=True, hidden=True)
@click.argument("mode", metavar="MODE")
@click.argument("path", required=False, metavar="PATH")
@click.argument("args", nargs=-1, type=click.UNPROCESSED, metavar="[ARGS]...")
def py_remote_cmd(stdin, mode, path, args):
    path, args = _normalize_args(mode, path, args)
    _run_remote(mode, path, args, stdin_flag=stdin)

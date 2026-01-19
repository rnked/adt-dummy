"""Shell command."""

import os

import click

from adt_dummy.core.errors import AppError
from adt_dummy.core.proc import run_interactive
from adt_dummy.local import proxy_to_remote


def _pick_shell():
    return "/bin/bash" if os.path.exists("/bin/bash") else "/bin/sh"


def _shell_in_cluster():
    shell = _pick_shell()
    exit_code = run_interactive([shell])
    if exit_code != 0:
        raise AppError("Shell exited with an error", exit_code=exit_code)


def _shell_local():
    proxy_to_remote(
        ["dami", "__remote", "shell"], tty=True, interactive=True
    )


@click.command(name="shell")
@click.pass_context
def shell_cmd(ctx):
    if ctx.obj.get("in_cluster"):
        _shell_in_cluster()
    else:
        _shell_local()


@click.command(name="shell")
def shell_remote_cmd():
    _shell_in_cluster()

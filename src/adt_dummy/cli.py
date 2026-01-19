"""CLI entrypoint for adt-dummy."""

import click

from adt_dummy import __version__
from adt_dummy.commands.doctor import doctor_cmd, doctor_remote_cmd
from adt_dummy.commands.net import net_cmd, net_remote_cmd
from adt_dummy.commands.py import py_cmd, py_remote_cmd
from adt_dummy.commands.query import query_cmd, query_remote_cmd
from adt_dummy.commands.shell import shell_cmd, shell_remote_cmd
from adt_dummy.core.env import is_in_cluster
from adt_dummy.core.errors import AppError


@click.group()
@click.version_option(__version__, prog_name="dami")
@click.pass_context
def cli(ctx):
    ctx.obj = {"in_cluster": is_in_cluster()}


@cli.group(name="__remote", hidden=True)
def remote_group():
    pass


cli.add_command(doctor_cmd)
cli.add_command(shell_cmd)
cli.add_command(query_cmd)
cli.add_command(net_cmd)
cli.add_command(py_cmd)

remote_group.add_command(doctor_remote_cmd)
remote_group.add_command(shell_remote_cmd)
remote_group.add_command(query_remote_cmd)
remote_group.add_command(net_remote_cmd)
remote_group.add_command(py_remote_cmd)


def main():
    try:
        cli(standalone_mode=False)
    except AppError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(exc.exit_code)
    except click.ClickException as exc:
        exc.show()
        raise SystemExit(exc.exit_code)

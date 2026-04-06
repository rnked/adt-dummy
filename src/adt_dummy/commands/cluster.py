"""Cluster-related helper commands."""

import click

from adt_dummy.core import env
from adt_dummy.core.errors import AppError
from adt_dummy.core.proc import run_command, run_interactive, which_or_error
from adt_dummy.k8s import kubectl_base_cmd

CLUSTER_ENV_DEFAULTS = {
    "prod": ("ADT_DUMMY_CLUSTER_PROD", "odmt-p-mskdc-mskx5-c15.kaas.raiffeisen.ru"),
    "preview": ("ADT_DUMMY_CLUSTER_PREVIEW", "odmt-v-dmz5v-msk34-c14.kaas.raiffeisen.ru"),
    "test": ("ADT_DUMMY_CLUSTER_TEST", ""),
}


def _ensure_local(ctx, command_name):
    if ctx.obj.get("in_cluster"):
        raise AppError(f"{command_name} is local-only.")


def _get_cluster_name(target):
    env_key, default = CLUSTER_ENV_DEFAULTS[target]
    value = env.get_env(env_key, default=default)
    if not value:
        raise AppError(f"Cluster is not configured. Set {env_key}.")
    return value


@click.command(name="ls", help="List pods in the configured namespace.")
@click.pass_context
def ls_cmd(ctx):
    _ensure_local(ctx, "dami ls")
    namespace = env.get_env("ADT_DUMMY_NAMESPACE", default="adt-dynamic")
    cmd = kubectl_base_cmd() + ["get", "pods", "-n", namespace]
    result = run_command(cmd)
    if result.stdout:
        click.echo(result.stdout, nl=False)


@click.command(
    name="go",
    help="Switch Kubernetes cluster using tsh kube login.",
    epilog=(
        "\b\n" "Targets are: prod, preview, test.\n" "Set ADT_DUMMY_CLUSTER_* to override defaults."
    ),
)
@click.argument("target", type=click.Choice(["prod", "preview", "test"], case_sensitive=False))
@click.pass_context
def go_cmd(ctx, target):
    _ensure_local(ctx, "dami go")
    cluster = _get_cluster_name(target)
    which_or_error("tsh")
    click.echo(f"Logging into {target} ({cluster})")
    exit_code = run_interactive(["tsh", "kube", "login", cluster])
    if exit_code != 0:
        raise AppError("tsh kube login failed", exit_code=exit_code)

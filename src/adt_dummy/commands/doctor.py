"""Doctor command."""

import click

from adt_dummy.core import env
from adt_dummy.core.errors import AppError
from adt_dummy.core.proc import which_or_error
from adt_dummy.k8s import can_exec, find_pod, get_current_context


def _check_trino_env():
    missing = []
    if not env.get_env("ADT_DUMMY_TRINO_HOST", default=None):
        missing.append("ADT_DUMMY_TRINO_HOST")
    if not env.get_env("ADT_DUMMY_TRINO_USER", default=None):
        missing.append("ADT_DUMMY_TRINO_USER")
    if not env.get_env("ADT_DUMMY_TRINO_PASSWORD", default=None):
        missing.append("ADT_DUMMY_TRINO_PASSWORD")
    return missing


def _doctor_local():
    namespace = env.get_env("ADT_DUMMY_NAMESPACE", default="adt-dynamic")
    selector = env.get_env(
        "ADT_DUMMY_POD_SELECTOR", default="app.kubernetes.io/name=adt-dummy"
    )
    explicit_pod = env.get_env("ADT_DUMMY_POD", default=None)
    exec_timeout = env.get_int_env("ADT_DUMMY_EXEC_TIMEOUT_SECONDS", default=60)

    kubectl = env.get_env("ADT_DUMMY_KUBECTL_BIN", default="kubectl")
    kubectl_path = which_or_error(kubectl)
    click.echo("Mode: local")
    click.echo(f"kubectl: {kubectl_path}")

    context = get_current_context()
    click.echo(f"Context: {context}")
    click.echo(f"Namespace: {namespace}")
    click.echo(f"Pod selector: {selector}")
    if explicit_pod:
        click.echo(f"Pod override: {explicit_pod}")

    pod = find_pod(namespace, selector, explicit_pod=explicit_pod, timeout=exec_timeout)
    click.echo(f"Selected pod: {pod}")

    auth = can_exec(namespace)
    if auth:
        click.echo(f"kubectl auth can-i create pods/exec: {auth}")


def _doctor_remote():
    click.echo("Mode: in-cluster")
    missing = _check_trino_env()
    if missing:
        raise AppError(
            "Missing required environment variables: " + ", ".join(missing)
        )
    click.echo("Trino environment: ok")


@click.command(
    name="doctor",
    help="Check kubectl access locally or Trino configuration in the pod.",
    epilog="Local mode validates kubectl context, namespace access, and pod discovery.",
)
@click.pass_context
def doctor_cmd(ctx):
    if ctx.obj.get("in_cluster"):
        _doctor_remote()
    else:
        _doctor_local()


@click.command(
    name="doctor",
    help="Check Trino configuration inside the toolbox pod.",
)
def doctor_remote_cmd():
    _doctor_remote()

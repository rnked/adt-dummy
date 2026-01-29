"""Local execution that proxies commands into a toolbox pod."""

import click

from adt_dummy.core import env
from adt_dummy.core.errors import AppError
from adt_dummy.core.proc import run_command, run_interactive
from adt_dummy.k8s import build_exec_cmd, find_pod


def proxy_to_remote(
    command_args, stdin_data=None, timeout=None, tty=False, interactive=False, capture_output=False
):
    namespace = env.get_env("ADT_DUMMY_NAMESPACE", default="adt-dynamic")
    selector = env.get_env(
        "ADT_DUMMY_POD_SELECTOR", default="app.kubernetes.io/name=adt-dummy"
    )
    explicit_pod = env.get_env("ADT_DUMMY_POD", default=None)
    exec_timeout = env.get_int_env("ADT_DUMMY_EXEC_TIMEOUT_SECONDS", default=60)
    timeout = timeout if timeout is not None else exec_timeout

    pod = find_pod(namespace, selector, explicit_pod=explicit_pod, timeout=timeout)
    needs_stdin = stdin_data is not None
    cmd = build_exec_cmd(
        namespace,
        pod,
        command_args,
        tty=tty,
        interactive=interactive or needs_stdin,
    )

    if interactive:
        exit_code = run_interactive(cmd)
        if exit_code != 0:
            raise AppError("Remote shell exited with an error", exit_code=exit_code)
        return

    result = run_command(cmd, input_text=stdin_data, timeout=timeout, check=False)
    if result.stderr:
        click.echo(result.stderr, err=True, nl=False)
    if result.returncode != 0:
        message = result.stderr.strip() or "Remote command failed"
        raise AppError(message, exit_code=result.returncode)
    if capture_output:
        return result.stdout
    if result.stdout:
        click.echo(result.stdout, nl=False)
    return None

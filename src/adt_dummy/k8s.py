"""Kubernetes helpers for locating toolbox pods and running kubectl."""

import json

from adt_dummy.core import env
from adt_dummy.core.errors import AppError
from adt_dummy.core.proc import run_command, which_or_error


def kubectl_bin():
    return env.get_env("ADT_DUMMY_KUBECTL_BIN", default="kubectl")


def kubectl_context():
    return env.get_env("ADT_DUMMY_KUBECTL_CONTEXT", default=None)


def kubectl_base_cmd():
    binary = kubectl_bin()
    which_or_error(binary)
    cmd = [binary]
    context = kubectl_context()
    if context:
        cmd += ["--context", context]
    return cmd


def get_current_context():
    context = kubectl_context()
    if context:
        return context
    result = run_command(kubectl_base_cmd() + ["config", "current-context"])
    return result.stdout.strip()


def get_pods_json(namespace, selector, timeout=None):
    cmd = kubectl_base_cmd() + [
        "get",
        "pods",
        "-n",
        namespace,
        "-l",
        selector,
        "-o",
        "json",
    ]
    result = run_command(cmd, timeout=timeout)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AppError("Failed to parse kubectl JSON output") from exc


def get_pod_json(namespace, pod_name, timeout=None):
    cmd = kubectl_base_cmd() + ["get", "pod", pod_name, "-n", namespace, "-o", "json"]
    result = run_command(cmd, timeout=timeout)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AppError("Failed to parse kubectl JSON output") from exc


def select_pod_from_json(data, explicit_pod=None):
    items = data.get("items") or []
    if not items:
        raise AppError("No pods found for selector")

    if explicit_pod:
        for item in items:
            if item.get("metadata", {}).get("name") == explicit_pod:
                return explicit_pod
        raise AppError(f"Pod not found: {explicit_pod}")

    running = [item for item in items if item.get("status", {}).get("phase") == "Running"]
    selected = running[0] if running else items[0]
    name = selected.get("metadata", {}).get("name")
    if not name:
        raise AppError("Pod selection failed: missing pod name")
    return name


def find_pod(namespace, selector, explicit_pod=None, timeout=None):
    if explicit_pod:
        get_pod_json(namespace, explicit_pod, timeout=timeout)
        return explicit_pod
    data = get_pods_json(namespace, selector, timeout=timeout)
    return select_pod_from_json(data, explicit_pod=explicit_pod)


def can_exec(namespace):
    cmd = kubectl_base_cmd() + ["auth", "can-i", "create", "pods/exec", "-n", namespace]
    result = run_command(cmd, check=False)
    return result.stdout.strip()


def build_exec_cmd(namespace, pod, command_args, tty=False, interactive=False):
    cmd = kubectl_base_cmd() + ["exec"]
    if tty:
        cmd.append("-t")
    if interactive:
        cmd.append("-i")
    cmd += ["-n", namespace, pod, "--"] + command_args
    return cmd

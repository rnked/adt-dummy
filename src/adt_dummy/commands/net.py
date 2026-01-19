"""Network command group."""

import json
from pathlib import Path

import requests

import click

from adt_dummy.core.errors import AppError
from adt_dummy.local import proxy_to_remote
from adt_dummy.services import net as net_service


def _parse_host_port(target):
    if target.startswith("[") and "]" in target:
        host, rest = target.split("]", 1)
        host = host.lstrip("[")
        if not rest.startswith(":"):
            raise AppError("Invalid target. Use HOST:PORT or [IPv6]:PORT")
        port_str = rest[1:]
    else:
        if ":" not in target:
            raise AppError("Invalid target. Use HOST:PORT")
        host, port_str = target.rsplit(":", 1)

    try:
        port = int(port_str)
    except ValueError as exc:
        raise AppError("Port must be an integer") from exc

    return host, port


def _load_payload(value):
    if value is None:
        return None
    if value.startswith("@"):  # file path
        path = Path(value[1:])
        if not path.exists():
            raise AppError(f"File not found: {path}")
        return path.read_text()
    return value


def _http_logic(
    method,
    url,
    header_items,
    timeout,
    data,
    json_value,
    show_body,
    allow_http_errors,
    data_is_raw=False,
    json_is_raw=False,
):
    headers = net_service.parse_headers(header_items)

    if data is not None and json_value is not None:
        raise AppError("Use either --data or --json, not both.")

    data_payload = data if data_is_raw else _load_payload(data)
    json_payload = json_value if json_is_raw else _load_payload(json_value)
    json_body = None
    if json_payload is not None:
        try:
            json_body = json.loads(json_payload)
        except json.JSONDecodeError as exc:
            raise AppError(f"Invalid JSON body: {exc}") from exc

    try:
        response, duration = net_service.http_request(
            url=url,
            method=method,
            headers=headers,
            timeout=timeout,
            data=data_payload,
            json_body=json_body,
        )
    except requests.RequestException as exc:
        raise AppError(f"HTTP request failed: {exc}") from exc

    duration_ms = int(duration * 1000)
    click.echo(f"Status: {response.status_code} {response.reason} ({duration_ms} ms)")

    if show_body:
        click.echo(response.text)

    if response.status_code >= 400 and not allow_http_errors:
        raise AppError(f"HTTP request failed with status {response.status_code}")


@click.group(name="net")
@click.pass_context
def net_cmd(ctx):
    pass


@net_cmd.command(name="dns")
@click.argument("name")
@click.pass_context
def net_dns_cmd(ctx, name):
    if not ctx.obj.get("in_cluster"):
        proxy_to_remote(["dami", "__remote", "net", "dns", name])
        return

    addresses = net_service.resolve_dns(name)
    if not addresses:
        raise AppError(f"No DNS results for {name}")
    for record_type, address in addresses:
        click.echo(f"{record_type}\t{address}")


@net_cmd.command(name="tcp")
@click.argument("target")
@click.pass_context
def net_tcp_cmd(ctx, target):
    if not ctx.obj.get("in_cluster"):
        proxy_to_remote(["dami", "__remote", "net", "tcp", target])
        return

    host, port = _parse_host_port(target)
    net_service.tcp_check(host, port)
    click.echo(f"TCP connection ok: {host}:{port}")


@net_cmd.command(name="http")
@click.argument("url")
@click.option("--method", default="GET")
@click.option("--header", "header_items", multiple=True)
@click.option("--timeout", type=int, default=10)
@click.option("--data")
@click.option("--json", "json_value")
@click.option("--show-body", is_flag=True, default=False)
@click.option("--allow-http-errors", is_flag=True, default=False)
@click.pass_context
def net_http_cmd(
    ctx, url, method, header_items, timeout, data, json_value, show_body, allow_http_errors
):
    if not ctx.obj.get("in_cluster"):
        remote_args = [
            "net",
            "http",
            url,
            "--method",
            method,
            "--timeout",
            str(timeout),
        ]
        for header in header_items:
            remote_args += ["--header", header]

        if data is not None:
            resolved = _load_payload(data)
            remote_args += ["--data-raw", resolved]
        if json_value is not None:
            resolved = _load_payload(json_value)
            remote_args += ["--json-raw", resolved]
        if show_body:
            remote_args.append("--show-body")
        if allow_http_errors:
            remote_args.append("--allow-http-errors")

        proxy_to_remote(["dami", "__remote"] + remote_args)
        return

    _http_logic(method, url, header_items, timeout, data, json_value, show_body, allow_http_errors)


@click.group(name="net")
def net_remote_cmd():
    pass


@net_remote_cmd.command(name="dns")
@click.argument("name")
def net_dns_remote_cmd(name):
    addresses = net_service.resolve_dns(name)
    if not addresses:
        raise AppError(f"No DNS results for {name}")
    for record_type, address in addresses:
        click.echo(f"{record_type}\t{address}")


@net_remote_cmd.command(name="tcp")
@click.argument("target")
def net_tcp_remote_cmd(target):
    host, port = _parse_host_port(target)
    net_service.tcp_check(host, port)
    click.echo(f"TCP connection ok: {host}:{port}")


@net_remote_cmd.command(name="http")
@click.argument("url")
@click.option("--method", default="GET")
@click.option("--header", "header_items", multiple=True)
@click.option("--timeout", type=int, default=10)
@click.option("--data")
@click.option("--data-raw", hidden=True)
@click.option("--json", "json_value")
@click.option("--json-raw", hidden=True)
@click.option("--show-body", is_flag=True, default=False)
@click.option("--allow-http-errors", is_flag=True, default=False)
def net_http_remote_cmd(
    url,
    method,
    header_items,
    timeout,
    data,
    data_raw,
    json_value,
    json_raw,
    show_body,
    allow_http_errors,
):
    _http_logic(
        method,
        url,
        header_items,
        timeout,
        data_raw if data_raw is not None else data,
        json_raw if json_raw is not None else json_value,
        show_body,
        allow_http_errors,
        data_is_raw=data_raw is not None,
        json_is_raw=json_raw is not None,
    )

"""Network utility helpers."""

import socket
import time

import requests

from adt_dummy.core.errors import AppError


def parse_headers(header_items):
    headers = {}
    for item in header_items:
        if ":" not in item:
            raise AppError(f"Invalid header: {item}. Use 'Key: Value'.")
        key, value = item.split(":", 1)
        headers[key.strip()] = value.strip()
    return headers


def resolve_dns(name):
    addresses = []
    try:
        infos = socket.getaddrinfo(name, None)
    except socket.gaierror as exc:
        raise AppError(f"DNS lookup failed for {name}: {exc}") from exc

    for family, _, _, _, sockaddr in infos:
        if family == socket.AF_INET:
            addresses.append(("A", sockaddr[0]))
        elif family == socket.AF_INET6:
            addresses.append(("AAAA", sockaddr[0]))
    return addresses


def tcp_check(host, port, timeout=5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError as exc:
        raise AppError(f"TCP connection failed to {host}:{port}: {exc}") from exc


def http_request(url, method, headers, timeout, data=None, json_body=None):
    start = time.monotonic()
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        timeout=timeout,
        data=data,
        json=json_body,
    )
    duration = time.monotonic() - start
    return response, duration

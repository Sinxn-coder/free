#!/usr/bin/env python3
"""Check HTTP and HTTPS URLs from a text file."""

from __future__ import annotations

import argparse
import concurrent.futures
import http.client
import ipaddress
import math
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class URLCheckError(ValueError):
    """An input URL is invalid or resolves to a disallowed destination."""


@dataclass(frozen=True)
class Result:
    url: str
    status: str
    detail: str

    def __str__(self) -> str:
        return f"{self.status:8} {self.url} ({self.detail})"


def _resolve_public_addresses(host: str, port: int) -> list[tuple]:
    try:
        records = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise URLCheckError(f"could not resolve host: {exc}") from exc

    addresses = []
    for family, socktype, proto, _canonname, sockaddr in records:
        try:
            address = ipaddress.ip_address(sockaddr[0])
        except ValueError as exc:
            raise URLCheckError(f"host resolved to an invalid IP address: {sockaddr[0]}") from exc
        if not address.is_global:
            raise URLCheckError(f"host resolves to a non-public IP address: {address}")
        addresses.append((family, socktype, proto, sockaddr))

    if not addresses:
        raise URLCheckError("host did not resolve to any IP addresses")
    return addresses


def validate_url(url: str) -> urllib.parse.SplitResult:
    try:
        parsed = urllib.parse.urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise URLCheckError(f"invalid URL: {exc}") from exc

    if parsed.scheme.lower() not in ("http", "https"):
        raise URLCheckError("only http and https URLs are supported")
    if not parsed.hostname:
        raise URLCheckError("URL must include a hostname")
    if parsed.username is not None or parsed.password is not None:
        raise URLCheckError("URLs containing credentials are not supported")

    effective_port = port or (443 if parsed.scheme.lower() == "https" else 80)
    _resolve_public_addresses(parsed.hostname, effective_port)
    return parsed


def _connect_to_public_address(address: tuple, timeout: float, source_address=None):
    host, port = address
    candidates = _resolve_public_addresses(host, port)
    last_error = None
    for family, socktype, proto, sockaddr in candidates:
        sock = socket.socket(family, socktype, proto)
        try:
            if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            sock.connect(sockaddr)
            return sock
        except OSError as exc:
            last_error = exc
            sock.close()
    if last_error:
        raise last_error
    raise URLCheckError("host did not resolve to any IP addresses")


class _PublicHTTPConnection(http.client.HTTPConnection):
    _create_connection = staticmethod(_connect_to_public_address)


class _PublicHTTPSConnection(http.client.HTTPSConnection):
    _create_connection = staticmethod(_connect_to_public_address)


class _PublicHTTPHandler(urllib.request.HTTPHandler):
    def http_open(self, request):
        return self.do_open(_PublicHTTPConnection, request)


class _PublicHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, request):
        return self.do_open(
            _PublicHTTPSConnection,
            request,
            context=self._context,
            check_hostname=self._check_hostname,
        )


class _PublicRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(request, fp, code, message, headers, newurl)


def _check_one(url: str, timeout: float) -> Result:
    try:
        validate_url(url)
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            _PublicHTTPHandler(),
            _PublicHTTPSHandler(context=ssl.create_default_context()),
            _PublicRedirectHandler(),
        )
        with opener.open(url, timeout=timeout) as response:
            status = response.getcode()
            reason = getattr(response, "reason", "")
            return Result(url, "OK", f"HTTP {status} {reason}".strip())
    except urllib.error.HTTPError as exc:
        exc.close()
        return Result(url, "HTTP_ERROR", f"HTTP {exc.code} {exc.reason}")
    except URLCheckError as exc:
        return Result(url, "BLOCKED", str(exc))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        reason = getattr(exc, "reason", exc)
        return Result(url, "ERROR", str(reason))


def _read_urls(path: Path) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"could not read {path}: {exc}") from exc
    return [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]


def check_urls(urls: Iterable[str], timeout: float, workers: int) -> list[Result]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(lambda url: _check_one(url, timeout), urls))


def _positive_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive number") from exc
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be a positive number")
    return number


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if number < 1 or number > 64:
        raise argparse.ArgumentTypeError("must be an integer from 1 to 64")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check HTTP/HTTPS URLs listed one per line in a text file."
    )
    parser.add_argument("input_file", type=Path, help="text file containing URLs")
    parser.add_argument(
        "--timeout",
        type=_positive_float,
        default=10.0,
        help="per-request timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--workers",
        type=_positive_int,
        default=4,
        help="maximum concurrent requests (1-64; default: 4)",
    )
    args = parser.parse_args(argv)

    try:
        urls = _read_urls(args.input_file)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    results = check_urls(urls, args.timeout, args.workers)
    for result in results:
        print(result)
    return int(any(result.status not in ("OK",) for result in results))


if __name__ == "__main__":
    raise SystemExit(main())

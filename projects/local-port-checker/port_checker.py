#!/usr/bin/env python3
"""Check whether a TCP host and port accept a connection."""

import argparse
import math
import socket
import sys

EXIT_SUCCESS = 0
EXIT_UNREACHABLE = 1
EXIT_USAGE = 2

DEFAULT_TIMEOUT = 2.0
MAX_TIMEOUT = 30.0


def parse_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be an integer from 1 to 65535") from exc
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def parse_timeout(value: str) -> float:
    try:
        timeout = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be a number greater than 0 and no more than 30 seconds") from exc
    if not math.isfinite(timeout) or not 0 < timeout <= MAX_TIMEOUT:
        raise argparse.ArgumentTypeError("timeout must be greater than 0 and no more than 30 seconds")
    return timeout


def check_connection(host: str, port: int, timeout: float) -> tuple[bool, str]:
    """Return whether a TCP connection succeeds and a diagnostic message."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"Connected to {host}:{port}"
    except OSError as exc:
        return False, f"Could not connect to {host}:{port}: {exc}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check whether one TCP host and port accept a connection."
    )
    parser.add_argument("host", help="hostname or IP address to check")
    parser.add_argument("port", type=parse_port, help="TCP port (1-65535)")
    parser.add_argument(
        "--timeout",
        type=parse_timeout,
        default=DEFAULT_TIMEOUT,
        help=(
            "connection timeout in seconds "
            f"(greater than 0, at most {MAX_TIMEOUT:g}; default: {DEFAULT_TIMEOUT:g})"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.host.strip():
        build_parser().error("host must not be empty")
    success, message = check_connection(args.host, args.port, args.timeout)
    print(message, file=sys.stdout if success else sys.stderr)
    return EXIT_SUCCESS if success else EXIT_UNREACHABLE


if __name__ == "__main__":
    raise SystemExit(main())

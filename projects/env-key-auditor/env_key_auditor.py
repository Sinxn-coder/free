#!/usr/bin/env python3
"""Compare environment variable names without displaying their values."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ASSIGNMENT_RE = re.compile(r"^(?:export[ \t]+)?([A-Za-z_][A-Za-z0-9_]*)[ \t]*=")


class EnvFileError(Exception):
    """An input file contains a line that is not a KEY=value assignment."""


def read_keys(path: Path, label: str) -> set[str]:
    """Read variable names only; never retain or display assignment values."""
    keys: set[str] = set()

    with path.open(encoding="utf-8") as env_file:
        for line_number, line in enumerate(env_file, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            match = ASSIGNMENT_RE.match(stripped)
            if match is None:
                raise EnvFileError(f"{label}: invalid assignment on line {line_number}")

            keys.add(match.group(1))

    return keys


def format_keys(keys: set[str]) -> str:
    return ", ".join(sorted(keys)) if keys else "(none)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare variable names in an example env file and an env file."
    )
    parser.add_argument(
        "template",
        nargs="?",
        type=Path,
        default=Path(".env.example"),
        help="template file to check (default: .env.example)",
    )
    parser.add_argument(
        "env_file",
        nargs="?",
        type=Path,
        default=Path(".env"),
        help="local env file to check (default: .env)",
    )
    args = parser.parse_args(argv)

    try:
        template_keys = read_keys(args.template, "template")
        env_keys = read_keys(args.env_file, "env")
    except (EnvFileError, OSError, UnicodeError) as error:
        print(f"env-key-auditor: {error}", file=sys.stderr)
        return 1

    missing = template_keys - env_keys
    extra = env_keys - template_keys
    print(f"Missing keys in .env: {format_keys(missing)}")
    print(f"Extra keys in .env: {format_keys(extra)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

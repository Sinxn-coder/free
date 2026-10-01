#!/usr/bin/env python3
"""Print a unified diff between two UTF-8 text files."""

import argparse
import difflib
import sys
from pathlib import Path
from typing import Sequence


def non_negative_int(value: str) -> int:
    """Parse a non-negative integer for argparse."""
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a non-negative integer") from error
    if number < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return number


def read_lines(path: Path) -> list[str]:
    """Read UTF-8 text, normalizing platform line endings."""
    with path.open(encoding="utf-8-sig", newline=None) as source:
        return source.read().splitlines()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show a unified diff between two UTF-8 text files."
    )
    parser.add_argument(
        "-U",
        "--context",
        type=non_negative_int,
        default=3,
        metavar="LINES",
        help="number of context lines to show (default: 3)",
    )
    parser.add_argument("old_file", type=Path, help="original file")
    parser.add_argument("new_file", type=Path, help="updated file")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    files = []
    for path in (args.old_file, args.new_file):
        try:
            files.append(read_lines(path))
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2
        except IsADirectoryError:
            print(f"error: not a file: {path}", file=sys.stderr)
            return 2
        except UnicodeDecodeError:
            print(f"error: file is not valid UTF-8: {path}", file=sys.stderr)
            return 2
        except OSError as error:
            print(f"error: cannot read {path}: {error.strerror}", file=sys.stderr)
            return 2

    old_lines, new_lines = files
    difference = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=str(args.old_file),
        tofile=str(args.new_file),
        n=args.context,
        lineterm="",
    )
    output = list(difference)
    if output:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write("\n".join(output) + "\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

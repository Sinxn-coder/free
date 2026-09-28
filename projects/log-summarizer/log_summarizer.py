#!/usr/bin/env python3
"""Count common log levels and print matching error lines."""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, TextIO


LEVELS = ("ERROR", "WARNING", "INFO", "DEBUG")
LEVEL_PATTERN = re.compile(r"\b(ERROR|WARNING|INFO|DEBUG)\b", re.IGNORECASE)


def summarize_lines(
    lines: Iterable[str],
    error_output: TextIO | None = None,
) -> Counter[str]:
    """Count lines containing each level and optionally stream error lines."""
    counts: Counter[str] = Counter({level: 0 for level in LEVELS})

    for line in lines:
        found_levels = {match.group(1).upper() for match in LEVEL_PATTERN.finditer(line)}
        for level in found_levels:
            counts[level] += 1
        if error_output is not None and "ERROR" in found_levels:
            error_output.write(line)
            if not line.endswith(("\n", "\r")):
                error_output.write("\n")

    return counts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Count ERROR, WARNING, INFO, and DEBUG log lines."
    )
    parser.add_argument("log_file", type=Path, help="path to the log file to analyze")
    parser.add_argument(
        "--no-error-lines",
        action="store_true",
        help="show counts only, without printing matching ERROR lines",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="text encoding used to read the log file (default: utf-8)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    error_output = None
    if not args.no_error_lines:
        print("Matching error lines:")
        error_output = sys.stdout

    try:
        with args.log_file.open("r", encoding=args.encoding) as log_file:
            counts = summarize_lines(log_file, error_output)
    except (OSError, UnicodeError, LookupError) as error:
        parser.error(f"cannot read {args.log_file}: {error}")

    print("Log level counts:")
    for level in LEVELS:
        print(f"{level}: {counts[level]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

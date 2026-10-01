#!/usr/bin/env python3
"""Redact common email addresses and phone-number-like strings."""

import argparse
import re
import sys
from pathlib import Path


EMAIL_PATTERN = re.compile(
    r"(?<![\w.+-])[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}(?![\w-])"
)
PHONE_PATTERN = re.compile(r"(?<!\w)\+?(?:\d[(). \t-]*){6,14}\d(?!\w)")
REDACTION = "[REDACTED]"


def redact(text: str) -> str:
    """Replace heuristic email and phone matches, preserving other text."""
    return PHONE_PATTERN.sub(
        REDACTION, EMAIL_PATTERN.sub(REDACTION, text)
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Redact common email addresses and phone-number-like strings "
            "from a UTF-8 text file."
        ),
        epilog=(
            "Patterns are heuristics and redaction does not guarantee "
            "anonymization. Results go to stdout unless --output is given; "
            "an existing output file is never overwritten."
        ),
    )
    parser.add_argument("input", type=Path, help="input text file")
    parser.add_argument(
        "-o", "--output", type=Path, help="write to a new file instead of stdout"
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    try:
        text = args.input.read_text(encoding="utf-8")
        result = redact(text)
        if args.output is None:
            sys.stdout.write(result)
            return 0

        input_path = args.input.resolve()
        output_path = args.output.resolve()
        if input_path == output_path:
            raise ValueError("output path must be different from the input path")
        if args.output.exists() and args.output.samefile(args.input):
            raise ValueError("output path refers to the input file")

        try:
            with args.output.open("x", encoding="utf-8", newline="") as output_file:
                output_file.write(result)
        except FileExistsError as error:
            raise ValueError(f"output file already exists: {args.output}") from error
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f"redactor: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

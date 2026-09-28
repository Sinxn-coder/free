"""Validate and inspect JSON Lines files."""

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


def inspect_jsonl(input_file: TextIO, output_file: TextIO | None = None) -> tuple[int, list[str]]:
    """Return the valid record count and malformed-line messages."""
    record_count = 0
    errors = []
    output_record_count = 0

    for line_number, line in enumerate(input_file, start=1):
        if not line.strip():
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"Line {line_number}: {error.msg}")
            continue

        record_count += 1
        if output_file is not None:
            if output_record_count:
                output_file.write("\n")
            output_file.write(json.dumps(record, indent=2, ensure_ascii=False))
            output_file.write("\n")
            output_record_count += 1

    return record_count, errors


def _same_file(input_path: Path, output_path: Path) -> bool:
    """Check whether output resolves to the input, including existing aliases."""
    try:
        return input_path.samefile(output_path)
    except FileNotFoundError:
        return input_path.resolve() == output_path.resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a JSON Lines file and optionally pretty-print valid records."
    )
    parser.add_argument("input", type=Path, help="path to the JSON Lines input")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write valid records as pretty-printed JSON to this separate file",
    )
    args = parser.parse_args(argv)

    if args.output is not None and _same_file(args.input, args.output):
        parser.error("output must be a different file from input")

    try:
        with args.input.open(encoding="utf-8") as input_file:
            if args.output is None:
                record_count, errors = inspect_jsonl(input_file)
            else:
                with args.output.open("w", encoding="utf-8") as output_file:
                    record_count, errors = inspect_jsonl(input_file, output_file)
    except OSError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    for error in errors:
        print(error, file=sys.stderr)
    print(f"Total records: {record_count}")
    print(f"Malformed lines: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

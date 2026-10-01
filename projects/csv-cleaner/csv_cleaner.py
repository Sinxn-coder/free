"""Trim whitespace from CSV cells and optionally normalize header names."""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import TextIO


def normalize_header(header: str) -> str:
    """Convert a header to lowercase words separated by underscores."""
    return re.sub(r"\W+", "_", header.strip().casefold()).strip("_")


def clean_csv(
    input_path: Path,
    output_path: Path,
    *,
    normalize_headers: bool = False,
    overwrite: bool = False,
) -> None:
    """Write a cleaned CSV, refusing to replace files unless requested."""
    input_path = Path(input_path)
    output_path = Path(output_path)

    if input_path.resolve() == output_path.resolve():
        raise ValueError("input and output paths must be different")

    output_mode = "w" if overwrite else "x"
    with input_path.open("r", encoding="utf-8-sig", newline="") as source:
        with output_path.open(output_mode, encoding="utf-8", newline="") as destination:
            _write_cleaned_csv(
                source, destination, normalize_headers=normalize_headers
            )


def _write_cleaned_csv(
    source: TextIO, destination: TextIO, *, normalize_headers: bool
) -> None:
    reader = csv.reader(source, strict=True)
    writer = csv.writer(destination)

    for row_number, row in enumerate(reader):
        cleaned = [cell.strip() for cell in row]
        if row_number == 0 and normalize_headers:
            cleaned = [normalize_header(cell) for cell in cleaned]
        writer.writerow(cleaned)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Trim whitespace from CSV cells and optionally normalize headers."
    )
    parser.add_argument("input", type=Path, help="source CSV file")
    parser.add_argument("output", type=Path, help="destination CSV file")
    parser.add_argument(
        "--normalize-headers",
        action="store_true",
        help="lowercase headers and replace punctuation or whitespace with underscores",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="allow replacing an existing output file",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        clean_csv(
            args.input,
            args.output,
            normalize_headers=args.normalize_headers,
            overwrite=args.overwrite,
        )
    except (OSError, csv.Error, ValueError) as error:
        print(f"csv-cleaner: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

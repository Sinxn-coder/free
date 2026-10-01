"""Convert a CSV file with a header row to a JSON array of objects."""

import argparse
import csv
import json
import os
from pathlib import Path
import tempfile
from typing import Iterator, TextIO


class CsvToJsonError(Exception):
    """Raised when the CSV cannot be converted without data loss."""


def _validate_headers(headers: list[str]) -> None:
    if not headers:
        raise CsvToJsonError("CSV is missing a header row")

    missing = [str(index + 1) for index, header in enumerate(headers) if not header.strip()]
    if missing:
        raise CsvToJsonError(
            "CSV has missing header names in column(s): " + ", ".join(missing)
        )

    seen: set[str] = set()
    duplicates: set[str] = set()
    for header in headers:
        if header in seen:
            duplicates.add(header)
        seen.add(header)
    if duplicates:
        names = ", ".join(repr(name) for name in sorted(duplicates))
        raise CsvToJsonError(f"CSV has duplicate header name(s): {names}")


def _same_file(input_path: Path, output_path: Path) -> bool:
    if input_path.resolve() == output_path.resolve():
        return True
    try:
        return output_path.exists() and os.path.samefile(input_path, output_path)
    except OSError:
        return False


def _write_json_with_headers(
    rows: Iterator[list[str]], output: TextIO, headers: list[str]
) -> None:
    writer = json.JSONEncoder(ensure_ascii=False, separators=(",", ":"))
    output.write("[")
    first = True
    for record_number, row in enumerate(rows, start=2):
        if not row:
            continue
        if len(row) != len(headers):
            raise CsvToJsonError(
                f"CSV record {record_number} has {len(row)} field(s); "
                f"expected {len(headers)}"
            )
        if not first:
            output.write(",")
        output.write("\n")
        output.write(writer.encode(dict(zip(headers, row))))
        first = False
    if not first:
        output.write("\n")
    output.write("]\n")


def convert_csv_to_json(input_path: Path, output_path: Path) -> None:
    """Convert input_path to output_path, replacing output only on success."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    if _same_file(input_path, output_path):
        raise CsvToJsonError("input and output must be different files")

    temporary_path: Path | None = None
    try:
        with input_path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.reader(source, strict=True)
            try:
                headers = next(reader)
            except StopIteration as error:
                raise CsvToJsonError("CSV is missing a header row") from error
            _validate_headers(headers)

            if not output_path.parent.is_dir():
                raise CsvToJsonError(
                    f"output directory does not exist: {output_path.parent}"
                )
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                newline="",
                dir=output_path.parent,
                prefix=f".{output_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as destination:
                temporary_path = Path(destination.name)
                _write_json_with_headers(reader, destination, headers)

        os.replace(temporary_path, output_path)
    except (OSError, UnicodeError, csv.Error, CsvToJsonError) as error:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError as cleanup_error:
                raise CsvToJsonError(
                    f"{error}; could not remove temporary output "
                    f"{temporary_path}: {cleanup_error}"
                ) from error
        if isinstance(error, CsvToJsonError):
            raise
        raise CsvToJsonError(str(error)) from error


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert a CSV file with a header row to a JSON array of objects."
    )
    parser.add_argument("input", type=Path, help="source CSV file")
    parser.add_argument("output", type=Path, help="destination JSON file")
    args = parser.parse_args()

    try:
        convert_csv_to_json(args.input, args.output)
    except CsvToJsonError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Summarize rows, column names, and non-empty values in a CSV file."""

import argparse
import csv
from pathlib import Path


class CsvSummaryError(Exception):
    """Raised when a CSV file cannot be summarized."""


def _validate_delimiter(delimiter: str) -> None:
    """Validate that the delimiter is a single character."""
    if not delimiter or len(delimiter) != 1:
        raise CsvSummaryError(
            f"Delimiter must be a single character, got: {repr(delimiter)}"
        )


def summarize_csv(
    path: Path, delimiter: str = ","
) -> tuple[int, list[str], list[int]]:
    """Return the data-row count, column names, and non-empty count per column.
    
    Args:
        path: Path to the CSV file.
        delimiter: Field delimiter character (default: comma).
    """
    _validate_delimiter(delimiter)
    try:
        with path.open(encoding="utf-8", newline="") as csv_file:
            reader = csv.reader(csv_file, delimiter=delimiter, strict=True)
            try:
                columns = next(reader)
            except StopIteration as error:
                raise CsvSummaryError("CSV file is empty or has no header") from error
            if not columns:
                raise CsvSummaryError("CSV file is empty or has no header")

            counts = [0] * len(columns)
            row_count = 0
            for line_number, row in enumerate(reader, start=2):
                if not row:
                    continue
                if len(row) != len(columns):
                    raise CsvSummaryError(
                        f"row {line_number} has {len(row)} fields; "
                        f"expected {len(columns)}"
                    )
                row_count += 1
                for index, value in enumerate(row):
                    if value.strip():
                        counts[index] += 1
    except (OSError, UnicodeError, csv.Error) as error:
        raise CsvSummaryError(str(error)) from error

    return row_count, columns, counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="CSV file to summarize")
    parser.add_argument(
        "--delimiter",
        default=",",
        help="Field delimiter character (default: comma)",
    )
    args = parser.parse_args()

    try:
        row_count, columns, counts = summarize_csv(args.file, delimiter=args.delimiter)
    except CsvSummaryError as error:
        parser.error(f"cannot summarize {args.file}: {error}")

    print(f"Data rows: {row_count}")
    print(f"Columns: {', '.join(columns)}")
    print("Non-empty values:")
    for column, count in zip(columns, counts):
        print(f"  {column}: {count}")


if __name__ == "__main__":
    main()

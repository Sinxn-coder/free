"""Print lines in a UTF-8 file that match a regular expression."""

import argparse
from collections.abc import Iterable, Iterator
from pathlib import Path
import re
import sys


def filter_lines(
    lines: Iterable[str], pattern: re.Pattern[str], invert: bool = False
) -> Iterator[str]:
    for line in lines:
        if bool(pattern.search(line)) != invert:
            yield line


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pattern", help="regular expression to search for")
    parser.add_argument("file", type=Path, help="UTF-8 file to read")
    parser.add_argument(
        "--invert",
        action="store_true",
        help="print lines that do not match the regular expression",
    )
    args = parser.parse_args(argv)

    try:
        pattern = re.compile(args.pattern)
    except re.error as error:
        parser.error(f"invalid regular expression {args.pattern!r}: {error}")

    try:
        with args.file.open("r", encoding="utf-8", newline="") as source:
            for line in filter_lines(source, pattern, args.invert):
                sys.stdout.buffer.write(line.encode("utf-8"))
    except (OSError, UnicodeError) as error:
        parser.error(f"cannot read {args.file}: {error}")


if __name__ == "__main__":
    main()

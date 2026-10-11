"""Find the largest files in a directory."""

import argparse
from pathlib import Path


def format_size(size: int) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB")
    value = float(size)
    for unit in units[:-1]:
        if value < 1024:
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} {units[-1]}"


def non_negative_int(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return number


def largest_files(
    directory: Path, limit: int = 10, min_size: int = 0
) -> list[tuple[int, Path]]:
    if limit < 0:
        raise ValueError("limit must be non-negative")
    if min_size < 0:
        raise ValueError("minimum size must be non-negative")

    files = []
    for path in directory.rglob("*"):
        if path.is_file():
            size = path.stat().st_size
            if size >= min_size:
                files.append((size, path))
    return sorted(files, reverse=True)[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--top", type=non_negative_int, default=10)
    parser.add_argument(
        "--min-size",
        type=non_negative_int,
        default=0,
        help="include only files at least this many bytes (default: 0)",
    )
    parser.add_argument(
        "--human-readable",
        action="store_true",
        help="display sizes using binary units (KiB, MiB, GiB, ...)",
    )
    args = parser.parse_args()
    for size, path in largest_files(args.directory, args.top, args.min_size):
        if args.human_readable:
            print(f"{format_size(size):>10}  {path}")
        else:
            print(f"{size:>10} bytes  {path}")


if __name__ == "__main__":
    main()

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


def largest_files(directory: Path, limit: int = 10) -> list[tuple[int, Path]]:
    files = [(path.stat().st_size, path) for path in directory.rglob("*") if path.is_file()]
    return sorted(files, reverse=True)[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument(
        "--human-readable",
        action="store_true",
        help="display sizes using binary units (KiB, MiB, GiB, ...)",
    )
    args = parser.parse_args()
    for size, path in largest_files(args.directory, args.top):
        if args.human_readable:
            print(f"{format_size(size):>10}  {path}")
        else:
            print(f"{size:>10} bytes  {path}")


if __name__ == "__main__":
    main()

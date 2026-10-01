"""Find the largest files in a directory."""

import argparse
from pathlib import Path


def largest_files(directory: Path, limit: int = 10) -> list[tuple[int, Path]]:
    files = [(path.stat().st_size, path) for path in directory.rglob("*") if path.is_file()]
    return sorted(files, reverse=True)[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()
    for size, path in largest_files(args.directory, args.top):
        print(f"{size:>10} bytes  {path}")


if __name__ == "__main__":
    main()

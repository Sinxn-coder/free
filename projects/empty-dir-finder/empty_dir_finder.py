"""Find empty directories below a root directory without following symlinks."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def find_empty_directories(
    root: str | os.PathLike[str], max_depth: int | None = None
) -> list[str]:
    """Return empty descendant directories as sorted, root-relative paths."""
    if max_depth is not None and max_depth < 0:
        raise ValueError("max_depth must be zero or greater")

    root_path = Path(root)
    if root_path.is_symlink():
        raise ValueError(f"root must not be a symbolic link: {root_path}")
    if not root_path.is_dir():
        raise NotADirectoryError(f"root is not a directory: {root_path}")

    empty_directories: list[str] = []

    def scan(directory: Path, parts: tuple[str, ...]) -> None:
        with os.scandir(directory) as entries:
            children = sorted(entries, key=lambda entry: entry.name)

        if not children:
            empty_directories.append(Path(*parts).as_posix())
            return

        depth = len(parts)
        if max_depth is not None and depth >= max_depth:
            return

        for entry in children:
            if entry.is_dir(follow_symlinks=False):
                scan(Path(entry.path), (*parts, entry.name))

    with os.scandir(root_path) as entries:
        children = sorted(entries, key=lambda entry: entry.name)

    for entry in children:
        if entry.is_dir(follow_symlinks=False):
            scan(Path(entry.path), (entry.name,))

    return sorted(empty_directories)


def non_negative_int(value: str) -> int:
    """Parse an argparse integer option that cannot be negative."""
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if number < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="List empty directories below a root directory."
    )
    parser.add_argument("root", type=Path, help="directory to scan")
    parser.add_argument(
        "--max-depth",
        type=non_negative_int,
        help="maximum directory levels below root to scan (default: unlimited)",
    )
    args = parser.parse_args(argv)

    try:
        for directory in find_empty_directories(args.root, args.max_depth):
            print(directory)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

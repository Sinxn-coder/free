"""Find files with identical content beneath a directory."""

import argparse
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import sys
from typing import Sequence


@dataclass(frozen=True)
class DuplicateGroup:
    size: int
    paths: tuple[Path, ...]


@dataclass(frozen=True)
class ScanError:
    path: Path
    message: str


@dataclass(frozen=True)
class ScanResult:
    duplicates: tuple[DuplicateGroup, ...]
    errors: tuple[ScanError, ...]


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(directory: Path) -> ScanResult:
    """Return duplicate-content groups and any paths that could not be scanned."""
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError(f"not a directory: {directory}")

    files_by_size: dict[int, list[Path]] = {}
    errors: list[ScanError] = []

    def record_walk_error(error: OSError) -> None:
        path = Path(error.filename) if error.filename else directory
        errors.append(ScanError(path, str(error)))

    for current, subdirectories, filenames in os.walk(
        directory, onerror=record_walk_error
    ):
        subdirectories.sort()
        for filename in sorted(filenames):
            path = Path(current) / filename
            try:
                size = path.stat().st_size
            except OSError as error:
                errors.append(ScanError(path, str(error)))
                continue
            files_by_size.setdefault(size, []).append(path)

    duplicates: list[DuplicateGroup] = []
    for size, paths in files_by_size.items():
        if len(paths) < 2:
            continue

        files_by_digest: dict[str, list[Path]] = {}
        for path in paths:
            try:
                digest = file_digest(path)
            except OSError as error:
                errors.append(ScanError(path, str(error)))
                continue
            files_by_digest.setdefault(digest, []).append(path)

        for matching_paths in files_by_digest.values():
            if len(matching_paths) > 1:
                duplicates.append(DuplicateGroup(size, tuple(matching_paths)))

    duplicates.sort(key=lambda group: tuple(str(path) for path in group.paths))
    return ScanResult(tuple(duplicates), tuple(errors))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Find files with identical content recursively without changing them."
    )
    parser.add_argument("directory", type=Path, help="directory to scan")
    args = parser.parse_args(argv)

    try:
        result = find_duplicates(args.directory)
    except OSError as error:
        parser.exit(2, f"{parser.prog}: error: {error}\n")

    if result.duplicates:
        count = len(result.duplicates)
        print(f"Found {count} duplicate group{'s' if count != 1 else ''}:")
        for group in result.duplicates:
            print(f"  {group.size} bytes:")
            for path in group.paths:
                print(f"    {path}")
    elif result.errors:
        print("No duplicates could be confirmed because some paths could not be scanned.")
    else:
        print("No duplicate files found.")

    for error in result.errors:
        print(f"Error: {error.path}: {error.message}", file=sys.stderr)
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

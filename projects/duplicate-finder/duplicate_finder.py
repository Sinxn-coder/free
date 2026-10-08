#!/usr/bin/env python3
"""Find exact duplicate files without modifying scanned files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from dataclasses import dataclass
from typing import BinaryIO, Iterator, Sequence


CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class DuplicateGroup:
    size: int
    sha256: str
    files: tuple[str, ...]

    @property
    def bytes_reclaimable(self) -> int:
        return self.size * (len(self.files) - 1)


@dataclass(frozen=True)
class ScanError:
    path: str
    message: str


@dataclass(frozen=True)
class ScanResult:
    groups: tuple[DuplicateGroup, ...]
    errors: tuple[ScanError, ...]
    files_scanned: int

    @property
    def bytes_reclaimable(self) -> int:
        return sum(group.bytes_reclaimable for group in self.groups)


def read_chunks(stream: BinaryIO, chunk_size: int) -> Iterator[bytes]:
    """Yield bounded chunks until the stream is exhausted."""
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            return
        yield chunk


def _path_key(path: str) -> tuple[str, str]:
    return os.path.normcase(path), path


def _error_message(error: OSError) -> str:
    return error.strerror or str(error)


def _hash_file(path: str, expected_size: int, chunk_size: int) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        before = os.fstat(stream.fileno())
        if before.st_size != expected_size:
            raise OSError(f"file size changed before hashing: {path}")

        for chunk in read_chunks(stream, chunk_size):
            digest.update(chunk)

        after = os.fstat(stream.fileno())
        if (before.st_size, before.st_mtime_ns) != (
            after.st_size,
            after.st_mtime_ns,
        ):
            raise OSError(f"file changed while being read: {path}")
    return digest.hexdigest()


def find_duplicates(
    roots: Sequence[str], chunk_size: int = CHUNK_SIZE
) -> ScanResult:
    """Scan directory roots and group regular files by size and SHA-256."""
    errors: list[ScanError] = []
    files_by_size: dict[int, list[str]] = {}
    seen_files: set[str] = set()
    visited_directories: set[str] = set()
    pending_directories: list[str] = []

    for root in sorted((os.path.abspath(root) for root in roots), key=_path_key):
        identity = os.path.normcase(root)
        try:
            root_stat = os.lstat(root)
        except OSError as error:
            errors.append(ScanError(root, _error_message(error)))
            continue
        if stat.S_ISLNK(root_stat.st_mode):
            errors.append(ScanError(root, "directory root is a symbolic link"))
        elif not stat.S_ISDIR(root_stat.st_mode):
            errors.append(ScanError(root, "input is not a directory"))
        elif identity not in visited_directories:
            pending_directories.append(root)

    while pending_directories:
        directory = pending_directories.pop()
        directory_identity = os.path.normcase(directory)
        if directory_identity in visited_directories:
            continue
        visited_directories.add(directory_identity)

        try:
            with os.scandir(directory) as iterator:
                entries = sorted(iterator, key=lambda entry: entry.name)
        except OSError as error:
            errors.append(ScanError(directory, _error_message(error)))
            continue

        child_directories: list[str] = []
        for entry in entries:
            path = os.path.abspath(entry.path)
            identity = os.path.normcase(path)
            if identity in seen_files or identity in visited_directories:
                continue
            try:
                entry_stat = entry.stat(follow_symlinks=False)
                if stat.S_ISLNK(entry_stat.st_mode):
                    continue
                if stat.S_ISDIR(entry_stat.st_mode):
                    child_directories.append(path)
                    continue
                if not stat.S_ISREG(entry_stat.st_mode):
                    continue
            except OSError as error:
                errors.append(ScanError(path, _error_message(error)))
                continue

            seen_files.add(identity)
            files_by_size.setdefault(entry_stat.st_size, []).append(path)

        pending_directories.extend(reversed(child_directories))

    hashed_files: dict[tuple[int, str], list[str]] = {}
    for size, paths in files_by_size.items():
        if len(paths) < 2:
            continue
        for path in sorted(paths, key=_path_key):
            try:
                digest = _hash_file(path, size, chunk_size)
            except OSError as error:
                errors.append(ScanError(path, _error_message(error)))
                continue
            hashed_files.setdefault((size, digest), []).append(path)

    groups = [
        DuplicateGroup(size, digest, tuple(sorted(paths, key=_path_key)))
        for (size, digest), paths in hashed_files.items()
        if len(paths) > 1
    ]
    groups.sort(key=lambda group: (group.size, group.sha256, group.files))
    errors.sort(key=lambda error: (_path_key(error.path), error.message))
    return ScanResult(tuple(groups), tuple(errors), len(seen_files))


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def _json_report(result: ScanResult) -> dict[str, object]:
    return {
        "duplicates": [
            {
                "bytes_reclaimable": group.bytes_reclaimable,
                "files": list(group.files),
                "sha256": group.sha256,
                "size": group.size,
            }
            for group in result.groups
        ],
        "errors": [
            {"message": error.message, "path": error.path}
            for error in result.errors
        ],
        "summary": {
            "bytes_reclaimable": result.bytes_reclaimable,
            "duplicate_file_count": sum(
                len(group.files) - 1 for group in result.groups
            ),
            "duplicate_group_count": len(result.groups),
            "files_scanned": result.files_scanned,
        },
    }


def _write_text_report(result: ScanResult) -> None:
    if result.groups:
        for index, group in enumerate(result.groups, start=1):
            print(
                f"Duplicate group {index}: {len(group.files)} files, "
                f"{group.size} bytes each (SHA-256 {group.sha256})"
            )
            for path in group.files:
                print(f"  {path}")
        print(f"Potential space savings: {result.bytes_reclaimable} bytes")
    else:
        print("No duplicate files found.")

    print(f"Files scanned: {result.files_scanned}")
    if result.errors:
        print(f"Scan errors: {len(result.errors)}", file=sys.stderr)
        for error in result.errors:
            print(f"{error.path}: {error.message}", file=sys.stderr)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Find exact duplicate files under one or more directory roots. "
            "Scanned files are never changed."
        ),
        epilog=(
            "Examples:\n"
            "  python duplicate_finder.py ./photos ./backup\n"
            "  python duplicate_finder.py --json ~/Documents\n"
            "  python duplicate_finder.py --chunk-size 262144 ./data"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "directories",
        metavar="DIRECTORY",
        nargs="+",
        help="directory roots to scan (symbolic-link roots are rejected)",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="write a deterministic JSON report to stdout",
    )
    parser.add_argument(
        "--chunk-size",
        type=_positive_int,
        default=CHUNK_SIZE,
        metavar="BYTES",
        help=f"bytes read at a time when hashing files (default: {CHUNK_SIZE})",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    result = find_duplicates(args.directories, args.chunk_size)

    if args.json_output:
        print(json.dumps(_json_report(result), indent=2, sort_keys=True))
        for error in result.errors:
            print(f"{error.path}: {error.message}", file=sys.stderr)
    else:
        _write_text_report(result)

    if result.errors:
        return 2
    return 1 if result.groups else 0


if __name__ == "__main__":
    raise SystemExit(main())

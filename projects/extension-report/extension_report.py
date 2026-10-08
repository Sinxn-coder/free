#!/usr/bin/env python3
"""Summarize file counts and sizes by suffix without modifying a directory."""

from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Report:
    groups: dict[str, list[int]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    scanned: int = 0
    limit_reached: bool = False


def non_negative_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if number < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return number


def summarize(directory: Path, max_files: int | None = None, max_depth: int | None = None) -> Report:
    """Collect regular, readable files in deterministic depth-first order."""
    report = Report()
    if directory.is_symlink():
        report.errors.append(f"{directory}: root directory is a symlink")
        return report

    groups: defaultdict[str, list[int]] = defaultdict(lambda: [0, 0])
    pending = [(directory, 0)]

    while pending:
        current, depth = pending.pop()
        try:
            with os.scandir(current) as iterator:
                entries = sorted(iterator, key=lambda entry: entry.name)
        except OSError as exc:
            report.errors.append(f"{current}: {exc}")
            continue

        subdirectories: list[Path] = []
        for entry in entries:
            path = Path(entry.path)
            try:
                if entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    if max_depth is None or depth < max_depth:
                        subdirectories.append(path)
                    continue
                if not entry.is_file(follow_symlinks=False):
                    continue
            except OSError as exc:
                report.errors.append(f"{path}: {exc}")
                continue

            if max_files is not None and report.scanned >= max_files:
                report.limit_reached = True
                pending.clear()
                break

            try:
                with open(path, "rb") as file:
                    size = os.fstat(file.fileno()).st_size
            except OSError as exc:
                report.errors.append(f"{path}: {exc}")
                continue

            group = groups[path.suffix]
            group[0] += 1
            group[1] += size
            report.scanned += 1

        if not report.limit_reached:
            pending.extend((path, depth + 1) for path in reversed(subdirectories))

    report.groups = dict(groups)
    return report


def format_report(report: Report) -> str:
    lines = ["Suffix\tFiles\tBytes"]
    for suffix in sorted(report.groups):
        count, size = report.groups[suffix]
        lines.append(f"{suffix or '<none>'}\t{count}\t{size}")
    lines.append(f"Total\t{report.scanned}\t{sum(size for _, size in report.groups.values())}")
    if report.limit_reached:
        lines.append("File limit reached; results may be incomplete.")
    if report.errors:
        lines.append(f"Errors\t{len(report.errors)}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Count readable regular files and total bytes grouped by suffix."
    )
    parser.add_argument("directory", type=Path, help="directory to summarize")
    parser.add_argument(
        "--max-files",
        type=non_negative_int,
        help="stop after this many readable regular files (zero scans no files)",
    )
    parser.add_argument(
        "--max-depth",
        type=non_negative_int,
        help="maximum directory depth below the root (zero includes root files only)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.directory.is_dir():
        print(f"Not a directory: {args.directory}", file=sys.stderr)
        return 2

    report = summarize(args.directory, args.max_files, args.max_depth)
    print(format_report(report))
    for error in report.errors:
        print(f"Error: {error}", file=sys.stderr)
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

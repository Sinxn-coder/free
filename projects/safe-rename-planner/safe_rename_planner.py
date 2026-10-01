"""Preview and safely apply deterministic filename replacements."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Sequence


@dataclass(frozen=True)
class Rename:
    source: Path
    destination: Path


@dataclass(frozen=True)
class RenamePlan:
    renames: tuple[Rename, ...]
    collisions: tuple[str, ...]


def _entries(directory: Path, recursive: bool) -> list[Path]:
    if not recursive:
        return sorted(
            (
                path
                for path in directory.iterdir()
                if path.is_file() or (path.is_symlink() and not path.is_dir())
            ),
            key=lambda path: path.name,
        )

    entries: list[Path] = []
    for root, directories, filenames in os.walk(directory, followlinks=False):
        directories.sort()
        entries.extend(Path(root) / name for name in sorted(filenames))
    return sorted(entries, key=lambda path: path.relative_to(directory).as_posix())


def _safe_name(name: str) -> bool:
    return (
        name not in {"", ".", ".."}
        and "\x00" not in name
        and "/" not in name
        and "\\" not in name
        and not Path(name).is_absolute()
    )


def plan_renames(
    directory: Path | str,
    old: str,
    new: str,
    recursive: bool = False,
) -> RenamePlan:
    """Plan literal replacements in entry names without changing the filesystem."""
    if not old:
        raise ValueError("the search text must not be empty")
    if not _safe_name(new):
        raise ValueError("replacement text must not contain path separators")

    root = Path(directory).resolve()
    if not root.is_dir():
        raise ValueError(f"not a directory: {directory}")

    renames: list[Rename] = []
    collisions: list[str] = []
    for source in _entries(root, recursive):
        destination_name = source.name.replace(old, new)
        if destination_name == source.name:
            continue
        if not _safe_name(destination_name):
            collisions.append(
                f"{source.relative_to(root)} -> unsafe destination name "
                f"{destination_name!r}"
            )
            continue
        destination = source.with_name(destination_name)
        renames.append(Rename(source, destination))

    planned_destinations: dict[str, Path] = {}
    for rename in renames:
        relative_destination = rename.destination.relative_to(root).as_posix()
        destination_key = os.path.normcase(relative_destination)
        prior_source = planned_destinations.get(destination_key)
        if prior_source is not None:
            collisions.append(
                f"{prior_source.relative_to(root)} and "
                f"{rename.source.relative_to(root)} both target "
                f"{relative_destination}"
            )
        else:
            planned_destinations[destination_key] = rename.source

        if rename.destination.exists() or rename.destination.is_symlink():
            collisions.append(
                f"{rename.source.relative_to(root)} -> "
                f"{relative_destination} (destination already exists)"
            )

    return RenamePlan(tuple(renames), tuple(collisions))


def apply_plan(plan: RenamePlan) -> None:
    """Apply a collision-free plan, rechecking destinations before each rename."""
    if plan.collisions:
        raise ValueError("cannot apply a plan with collisions")

    completed: list[Rename] = []
    try:
        for rename in plan.renames:
            if rename.destination.exists() or rename.destination.is_symlink():
                raise FileExistsError(f"destination appeared: {rename.destination}")
            rename.source.rename(rename.destination)
            completed.append(rename)
    except OSError:
        for rename in reversed(completed):
            rename.destination.rename(rename.source)
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview literal filename replacements; use --apply to rename."
    )
    parser.add_argument("directory", type=Path, help="directory to scan")
    parser.add_argument("old", help="literal text to replace in each filename")
    parser.add_argument("new", help="replacement text")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="also scan files in subdirectories (does not follow directory symlinks)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="perform the renames (default is preview only)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        plan = plan_renames(args.directory, args.old, args.new, args.recursive)
    except ValueError as error:
        parser.error(str(error))

    if not plan.renames and not plan.collisions:
        print("No filenames would change.")
        return 0

    for rename in plan.renames:
        print(
            f"{rename.source.relative_to(Path(args.directory).resolve())} -> "
            f"{rename.destination.relative_to(Path(args.directory).resolve())}"
        )
    for collision in plan.collisions:
        print(f"COLLISION: {collision}", file=sys.stderr)

    if plan.collisions:
        return 1
    if not args.apply:
        print("Dry run: no files were renamed. Use --apply to perform these changes.")
        return 0

    try:
        apply_plan(plan)
    except OSError as error:
        print(f"Rename failed: {error}", file=sys.stderr)
        return 1
    print(f"Renamed {len(plan.renames)} item(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

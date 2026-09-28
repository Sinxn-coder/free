"""Pick a random item from a text file."""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from typing import Optional, Sequence


def load_items(path: Path, ignore_blank_lines: bool = True) -> list[str]:
    """Read items from a UTF-8 text file, one item per line."""
    with path.open(encoding="utf-8") as item_file:
        items = [line.strip() for line in item_file]

    if ignore_blank_lines:
        items = [item for item in items if item]
    return items


def choose_item(items: Sequence[str], seed: Optional[str] = None) -> str:
    """Choose one item uniformly at random, or raise ValueError if empty."""
    if not items:
        raise ValueError("cannot choose from an empty list")
    return random.Random(seed).choice(items)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Select one random item from a text file."
    )
    parser.add_argument("file", type=Path, help="text file with one item per line")
    parser.add_argument(
        "--seed",
        help="seed the random generator for a reproducible selection",
    )
    parser.add_argument(
        "--keep-blank-lines",
        action="store_true",
        help="treat blank lines as selectable items (ignored by default)",
    )
    args = parser.parse_args(argv)

    try:
        items = load_items(args.file, ignore_blank_lines=not args.keep_blank_lines)
    except OSError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except UnicodeError as error:
        print(f"Error: unable to read {args.file} as UTF-8: {error}", file=sys.stderr)
        return 1

    if not items:
        print(f"Error: no selectable items in {args.file}", file=sys.stderr)
        return 1

    print(choose_item(items, seed=args.seed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

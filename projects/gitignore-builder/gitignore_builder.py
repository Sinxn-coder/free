#!/usr/bin/env python3
"""Generate a .gitignore snippet from a small collection of common templates."""

import argparse
from pathlib import Path
import sys
from typing import Iterable


TEMPLATES = {
    "python": (
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        ".Python",
        "build/",
        "dist/",
        "*.egg-info/",
        ".venv/",
        "venv/",
    ),
    "node": (
        "node_modules/",
        "npm-debug.log*",
        "yarn-debug.log*",
        "pnpm-debug.log*",
        "dist/",
        "coverage/",
    ),
    "java": (
        "*.class",
        "*.jar",
        "*.war",
        "*.ear",
        "target/",
        ".gradle/",
        "build/",
    ),
    "windows": (
        "Thumbs.db",
        "ehthumbs.db",
        "Desktop.ini",
        "$RECYCLE.BIN/",
    ),
    "macos": (
        ".DS_Store",
        ".AppleDouble",
        ".LSOverride",
        "._*",
        ".Spotlight-V100/",
        ".Trashes/",
        ".fseventsd/",
    ),
}


def build_gitignore(templates: Iterable[str], existing: str = "") -> str:
    """Combine existing lines and selected templates, preserving first occurrence."""
    selected = set(templates)
    lines = list(dict.fromkeys(existing.splitlines()))

    for name, entries in TEMPLATES.items():
        if name not in selected:
            continue
        for entry in entries:
            if entry not in lines:
                lines.append(entry)

    return "\n".join(lines) + ("\n" if lines else "")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a .gitignore snippet from known templates."
    )
    parser.add_argument(
        "templates",
        nargs="+",
        choices=tuple(TEMPLATES),
        metavar="TEMPLATE",
        help="one or more templates: %(choices)s",
    )
    parser.add_argument(
        "--existing",
        type=Path,
        help="merge lines from an existing .gitignore file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="write the generated snippet to this file instead of stdout",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    existing = ""
    if args.existing is not None:
        try:
            existing = args.existing.read_text(encoding="utf-8")
        except OSError as error:
            raise SystemExit(f"error reading {args.existing}: {error}") from error

    result = build_gitignore(args.templates, existing)
    if args.output is None:
        sys.stdout.write(result)
    else:
        try:
            args.output.write_text(result, encoding="utf-8", newline="\n")
        except OSError as error:
            raise SystemExit(f"error writing {args.output}: {error}") from error
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

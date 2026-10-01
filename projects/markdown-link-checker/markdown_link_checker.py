#!/usr/bin/env python3
"""Check local Markdown links without changing any files."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


@dataclass(frozen=True)
class BrokenLink:
    line: int
    target: str


def _mask_fenced_code(markdown: str) -> str:
    """Replace fenced code contents with spaces while preserving offsets."""
    lines = markdown.splitlines(keepends=True)
    masked: list[str] = []
    fence_char: str | None = None
    fence_length = 0

    for line in lines:
        match = re.match(r"^[ ]{0,3}(`{3,}|~{3,})", line)
        if fence_char is None and match:
            fence_char = match.group(1)[0]
            fence_length = len(match.group(1))
            masked.append("".join("\n" if char == "\n" else " " for char in line))
        elif fence_char is not None:
            masked.append("".join("\n" if char == "\n" else " " for char in line))
            if re.match(rf"^[ ]{{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ ]*(?:\r?\n)?$", line):
                fence_char = None
                fence_length = 0
        else:
            masked.append(line)
    return "".join(masked)


def _mask_inline_code(markdown: str) -> str:
    """Replace inline code spans with spaces while preserving offsets."""
    characters = list(markdown)
    position = 0
    while position < len(markdown):
        if markdown[position] != "`" or (position > 0 and markdown[position - 1] == "\\"):
            position += 1
            continue

        opening_end = position
        while opening_end < len(markdown) and markdown[opening_end] == "`":
            opening_end += 1
        fence = markdown[position:opening_end]
        closing = opening_end
        while closing < len(markdown):
            closing = markdown.find("`", closing)
            if closing < 0:
                break
            closing_end = closing
            while closing_end < len(markdown) and markdown[closing_end] == "`":
                closing_end += 1
            if markdown[closing:closing_end] == fence:
                for index in range(position, closing_end):
                    if characters[index] != "\n":
                        characters[index] = " "
                position = closing_end
                break
            closing = closing_end
        else:
            position = opening_end
            continue
        if closing < 0:
            position = opening_end
    return "".join(characters)


def _inline_destinations(markdown: str):
    """Yield each inline Markdown link destination and its source offset."""
    text = _mask_inline_code(_mask_fenced_code(markdown))
    marker = 0
    while True:
        marker = text.find("](", marker)
        if marker < 0:
            return
        if marker > 0 and text[marker - 1] == "\\":
            marker += 2
            continue

        position = marker + 2
        while position < len(text) and text[position].isspace():
            position += 1
        link_start = text.rfind("[", 0, marker)

        if position < len(text) and text[position] == "<":
            destination_start = position + 1
            position = destination_start
            while position < len(text):
                if text[position] == ">" and text[position - 1] != "\\":
                    destination = text[destination_start:position]
                    position += 1
                    break
                position += 1
            else:
                marker += 2
                continue
        else:
            destination_start = position
            nested_parentheses = 0
            while position < len(text):
                char = text[position]
                escaped = position > destination_start and text[position - 1] == "\\"
                if not escaped:
                    if char == "(":
                        nested_parentheses += 1
                    elif char == ")":
                        if nested_parentheses == 0:
                            break
                        nested_parentheses -= 1
                    elif char.isspace():
                        break
                position += 1
            destination = text[destination_start:position]

        if link_start >= 0 and destination:
            yield destination, link_start
        marker += 2


def _reference_destinations(markdown: str):
    """Yield destinations declared by Markdown reference definitions."""
    text = _mask_inline_code(_mask_fenced_code(markdown))
    definition = re.compile(
        r"^[ ]{0,3}\[(?:\\.|[^\]])+\]:[ \t]*"
        r"(?:<(?P<angle>[^>\r\n]*)>|(?P<plain>\S+))",
        re.MULTILINE,
    )
    for match in definition.finditer(text):
        destination = match.group("angle") or match.group("plain")
        yield destination, match.start()


def _resolve_target(destination: str, source: Path, root: Path) -> Path | None:
    destination = re.sub(r"\\([()<>\\ ])", r"\1", destination)
    parsed = urlsplit(destination)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None

    decoded_path = unquote(parsed.path)
    if decoded_path.startswith("/"):
        return root / decoded_path.lstrip("/")
    return source.parent / decoded_path


def check_markdown_file(source: Path, root: Path) -> list[BrokenLink]:
    markdown = source.read_text(encoding="utf-8")
    broken: list[BrokenLink] = []
    destinations = (*_inline_destinations(markdown), *_reference_destinations(markdown))
    for destination, offset in destinations:
        target = _resolve_target(destination, source, root)
        if target is not None and not target.exists():
            line = markdown.count("\n", 0, offset) + 1
            broken.append(BrokenLink(line, destination))
    return broken


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report missing local targets in Markdown links; never modify files."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Markdown file or directory to inspect (default: current directory)",
    )
    args = parser.parse_args(argv)
    root = Path(args.path).resolve()
    if not root.exists():
        parser.error(f"path does not exist: {args.path}")

    if root.is_file():
        files = [root] if root.suffix.lower() == ".md" else []
        scan_root = root.parent
    elif root.is_dir():
        files = sorted(root.rglob("*.md"))
        scan_root = root
    else:
        parser.error(f"path is not a file or directory: {args.path}")

    issues: list[tuple[Path, BrokenLink]] = []
    try:
        for source in files:
            issues.extend((source, issue) for issue in check_markdown_file(source, scan_root))
    except (OSError, UnicodeError) as error:
        print(f"markdown-link-checker: {error}", file=sys.stderr)
        return 2

    if not issues:
        print("No broken local Markdown links found.")
        return 0

    for source, issue in issues:
        try:
            display_source = source.relative_to(scan_root)
        except ValueError:
            display_source = source
        print(f"{display_source}:{issue.line}: missing target '{issue.target}'")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

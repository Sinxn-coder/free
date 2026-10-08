"""Generate a table of contents from Markdown ATX headings."""

import argparse
import html
from pathlib import Path
import re
import sys
import unicodedata


_ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*)|[ \t]*)$")
_FENCE_START = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_REFERENCE_LINK = re.compile(r"!?\[([^\]]*)\]\[[^\]]*\]")
_HTML_TAG = re.compile(r"<[^>]*>")
_ESCAPED_MARKDOWN = re.compile(r"\\([\\`*{}\[\]()#+\-.!_>])")


def extract_headings(markdown: str) -> list[tuple[int, str]]:
    """Return ATX heading levels and text, excluding fenced code blocks."""
    headings = []
    fence_char = None
    fence_length = 0

    for line in markdown.splitlines():
        if fence_char is not None:
            closing = re.match(
                rf"^ {{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ \t]*$",
                line,
            )
            if closing:
                fence_char = None
            continue

        fence = _FENCE_START.match(line)
        if fence:
            marker, info = fence.groups()
            if marker[0] != "`" or "`" not in info:
                fence_char = marker[0]
                fence_length = len(marker)
            continue

        heading = _ATX_HEADING.match(line)
        if not heading:
            continue

        text = heading.group(2) or ""
        text = re.sub(r"[ \t]+#+[ \t]*$", "", text).strip()
        headings.append((len(heading.group(1)), text))

    return headings


def _heading_slug(text: str) -> str:
    """Create a GitHub-style anchor slug from rendered heading text."""
    text = html.unescape(text)
    text = _LINK.sub(r"\1", text)
    text = _REFERENCE_LINK.sub(r"\1", text)
    text = _HTML_TAG.sub("", text)
    text = _ESCAPED_MARKDOWN.sub(r"\1", text)
    text = text.replace("`", "")
    text = re.sub(r"(\*\*|__|~~|\*)", "", text)
    text = re.sub(r"(?<!\w)_|_(?!\w)", "", text)
    text = text.lower().strip()

    slug_characters = []
    for character in text:
        category = unicodedata.category(character)
        if category[0] in ("L", "N", "M") or character in "-_":
            slug_characters.append(character)
        elif character.isspace():
            slug_characters.append(" ")

    return re.sub(r"\s+", "-", "".join(slug_characters).strip())


def generate_toc(markdown: str) -> str:
    """Generate a Markdown table of contents for the document's ATX headings."""
    lines = []
    used_slugs = set()
    next_suffix = {}

    for level, text in extract_headings(markdown):
        base_slug = _heading_slug(text)
        slug = base_slug
        if slug in used_slugs:
            suffix = next_suffix.get(base_slug, 1)
            while f"{base_slug}-{suffix}" in used_slugs:
                suffix += 1
            slug = f"{base_slug}-{suffix}"
            next_suffix[base_slug] = suffix + 1
        used_slugs.add(slug)

        lines.append(f'{"  " * (level - 1)}- [{text}](#{slug})')

    return "\n".join(lines) + ("\n" if lines else "")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Markdown file to read")
    parser.add_argument(
        "-o", "--output", type=Path, help="write the table of contents to this file"
    )
    args = parser.parse_args()

    toc = generate_toc(args.source.read_text(encoding="utf-8"))
    if args.output:
        args.output.write_text(toc, encoding="utf-8")
    else:
        sys.stdout.write(toc)


if __name__ == "__main__":
    main()

"""Convert a small Markdown subset to HTML."""

import argparse
import html
from pathlib import Path
import re


def _format_inline(text: str) -> str:
    escaped = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def convert(markdown: str) -> str:
    output = []
    list_type = None
    list_items = []

    def close_list() -> None:
        nonlocal list_type, list_items
        if list_type is not None:
            items = "".join(f"<li>{item}</li>" for item in list_items)
            output.append(f"<{list_type}>{items}</{list_type}>")
            list_type = None
            list_items = []

    for line in markdown.splitlines():
        unordered_item = line.startswith(("- ", "* "))
        ordered_item = re.match(r"\d+\. ", line)

        if unordered_item or ordered_item:
            current_list_type = "ul" if unordered_item else "ol"
            if list_type != current_list_type:
                close_list()
                list_type = current_list_type
            item_text = line[2:] if unordered_item else line[ordered_item.end():]
            list_items.append(_format_inline(item_text))
        elif not line:
            close_list()
        elif line.startswith("# "):
            close_list()
            output.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            close_list()
            output.append(f"<h2>{html.escape(line[3:])}</h2>")
        else:
            close_list()
            output.append(f"<p>{_format_inline(line)}</p>")

    close_list()
    return "\n".join(output) + ("\n" if output else "")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(convert(args.source.read_text(encoding="utf-8")), encoding="utf-8")


if __name__ == "__main__":
    main()

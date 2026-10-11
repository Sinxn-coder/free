"""Format or minify JSON files."""

import argparse
import json
import sys
from pathlib import Path


def format_json(text: str, minify: bool = False, sort_keys: bool = False) -> str:
    value = json.loads(text)
    if minify:
        return json.dumps(value, separators=(",", ":"), sort_keys=sort_keys)
    return json.dumps(value, indent=2, sort_keys=sort_keys) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--minify", action="store_true")
    parser.add_argument("--sort-keys", action="store_true")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if the file is properly formatted without modifying it",
    )
    args = parser.parse_args()

    file_content = args.file.read_text(encoding="utf-8")
    formatted = format_json(file_content, args.minify, args.sort_keys)

    if args.check:
        if file_content == formatted:
            return
        sys.exit(1)

    print(formatted, end="")


if __name__ == "__main__":
    main()

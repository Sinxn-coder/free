"""Format or minify JSON files."""

import argparse
import json
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
    args = parser.parse_args()
    print(
        format_json(args.file.read_text(encoding="utf-8"), args.minify, args.sort_keys),
        end="",
    )


if __name__ == "__main__":
    main()

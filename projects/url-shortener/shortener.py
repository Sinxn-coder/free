"""Create deterministic short codes for URLs."""

import argparse
import hashlib
import json
from pathlib import Path


DATA_FILE = Path(__file__).with_name("urls.json")


def shorten(url: str, mappings: dict[str, str]) -> str:
    code = hashlib.sha256(url.encode()).hexdigest()[:8]
    mappings[code] = url
    return code


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--expand", action="store_true")
    args = parser.parse_args()
    mappings = json.loads(DATA_FILE.read_text()) if DATA_FILE.exists() else {}
    if args.expand:
        print(mappings.get(args.url, "Unknown code"))
    else:
        code = shorten(args.url, mappings)
        DATA_FILE.write_text(json.dumps(mappings, indent=2) + "\n")
        print(code)


if __name__ == "__main__":
    main()

"""Report basic statistics for text."""

import argparse
from collections import Counter
from pathlib import Path
import re


def statistics(text: str) -> dict[str, int]:
    words = re.findall(r"\b[\w']+\b", text.lower())
    return {
        "characters": len(text),
        "words": len(words),
        "lines": text.count("\n") + (1 if text else 0),
        "reading_minutes": max(1, round(len(words) / 200)),
        "unique_words": len(set(words)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    for key, value in statistics(args.file.read_text(encoding="utf-8")).items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

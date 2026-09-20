"""A tiny JSON-backed todo list."""

import argparse
import json
from pathlib import Path


DATA_FILE = Path(__file__).with_name("todos.json")


def load() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save(items: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")


def add(items: list[dict], text: str) -> None:
    items.append({"text": text, "done": False})
    save(items)


def complete(items: list[dict], index: int) -> None:
    if not 1 <= index <= len(items):
        raise ValueError("todo number is out of range")
    items[index - 1]["done"] = True
    save(items)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    add_parser = sub.add_parser("add")
    add_parser.add_argument("text")
    sub.add_parser("list")
    done_parser = sub.add_parser("done")
    done_parser.add_argument("number", type=int)
    args = parser.parse_args()
    items = load()
    if args.command == "add":
        add(items, args.text)
    elif args.command == "done":
        complete(items, args.number)
    else:
        for number, item in enumerate(items, 1):
            print(f"[{'x' if item['done'] else ' '}] {number}. {item['text']}")


if __name__ == "__main__":
    main()

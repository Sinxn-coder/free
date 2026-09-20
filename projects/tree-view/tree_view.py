"""Print a directory as a tree."""

import argparse
from pathlib import Path


def render(root: Path, max_depth: int = 3) -> list[str]:
    lines = [root.name]

    def visit(directory: Path, prefix: str, depth: int) -> None:
        if depth >= max_depth:
            return
        children = sorted(directory.iterdir(), key=lambda item: (item.is_file(), item.name.lower()))
        for number, child in enumerate(children):
            branch = "└── " if number == len(children) - 1 else "├── "
            lines.append(prefix + branch + child.name)
            if child.is_dir():
                visit(child, prefix + ("    " if number == len(children) - 1 else "│   "), depth + 1)

    visit(root, "", 0)
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--max-depth", type=int, default=3)
    args = parser.parse_args()
    print("\n".join(render(args.directory, args.max_depth)))


if __name__ == "__main__":
    main()

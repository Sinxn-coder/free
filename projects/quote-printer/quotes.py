"""Print a random quote."""

import argparse
import random


QUOTES = {
    "motivation": ["Small steps every day become big results."],
    "learning": ["The expert in anything was once a beginner."],
    "focus": ["The secret of getting ahead is getting started."],
}


def random_quote(category: str | None = None, seed: int | None = None) -> str:
    generator = random.Random(seed)
    choices = QUOTES.get(category, sum(QUOTES.values(), [])) if category else sum(QUOTES.values(), [])
    if not choices:
        raise ValueError(f"unknown category: {category}")
    return generator.choice(choices)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--category", choices=sorted(QUOTES))
    args = parser.parse_args()
    print(random_quote(args.category))


if __name__ == "__main__":
    main()

"""Generate random HEX color palettes."""

import argparse
import random


def palette(count: int, seed: int | None = None) -> list[str]:
    generator = random.Random(seed)
    if count < 1:
        raise ValueError("count must be positive")
    return [f"#{generator.randrange(0x1000000):06X}" for _ in range(count)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    print("\n".join(palette(args.count, args.seed)))


if __name__ == "__main__":
    main()

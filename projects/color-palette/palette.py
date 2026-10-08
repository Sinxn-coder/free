"""Generate random HEX color palettes."""

import argparse
import random


def palette(count: int, seed: int | None = None, unique: bool = False) -> list[str]:
    generator = random.Random(seed)
    if count < 1:
        raise ValueError("count must be positive")
    if unique:
        if count > 0x1000000:
            raise ValueError("count cannot exceed the number of available HEX colors")
        colors = generator.sample(range(0x1000000), count)
        return [f"#{color:06X}" for color in colors]
    return [f"#{generator.randrange(0x1000000):06X}" for _ in range(count)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--unique", action="store_true")
    args = parser.parse_args()
    print("\n".join(palette(args.count, args.seed, args.unique)))


if __name__ == "__main__":
    main()

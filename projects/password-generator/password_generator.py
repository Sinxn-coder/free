"""Generate secure random passwords."""

import argparse
import secrets
import string


def generate_password(length: int, use_symbols: bool = True) -> str:
    if length < 4:
        raise ValueError("length must be at least 4")

    categories = [
        string.ascii_lowercase,
        string.ascii_uppercase,
        string.digits,
    ]
    if use_symbols:
        categories.append(string.punctuation)

    alphabet = "".join(categories)
    password = [secrets.choice(category) for category in categories]
    password.extend(secrets.choice(alphabet) for _ in range(length - len(password)))
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--length", type=int, default=16)
    parser.add_argument("--no-symbols", action="store_true")
    args = parser.parse_args()
    print(generate_password(args.length, not args.no_symbols))


if __name__ == "__main__":
    main()

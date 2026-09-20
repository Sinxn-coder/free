"""Generate secure random passwords."""

import argparse
import secrets
import string


def generate_password(length: int, use_symbols: bool = True) -> str:
    if length < 4:
        raise ValueError("length must be at least 4")
    alphabet = string.ascii_letters + string.digits
    if use_symbols:
        alphabet += string.punctuation
    return "".join(secrets.choice(alphabet) for _ in range(length))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--length", type=int, default=16)
    parser.add_argument("--no-symbols", action="store_true")
    args = parser.parse_args()
    print(generate_password(args.length, not args.no_symbols))


if __name__ == "__main__":
    main()

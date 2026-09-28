"""Calculate date differences and apply day offsets using the standard library."""

import argparse
import re
from datetime import date, timedelta


ISO_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}\Z")


def parse_iso_date(value: str) -> date:
    """Parse a date in the exact YYYY-MM-DD format."""
    if not ISO_DATE_PATTERN.fullmatch(value):
        raise argparse.ArgumentTypeError(
            f"invalid date {value!r}: expected YYYY-MM-DD"
        )

    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"invalid date {value!r}: {error}"
        ) from error


def parse_day_offset(value: str) -> int:
    """Parse an integer day offset."""
    try:
        return int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"invalid day offset {value!r}: expected an integer"
        ) from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Calculate the number of days between dates or shift a date."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    between = commands.add_parser(
        "between",
        help="calculate the signed number of days from START to END",
    )
    between.add_argument("start", type=parse_iso_date, metavar="START")
    between.add_argument("end", type=parse_iso_date, metavar="END")

    offset = commands.add_parser(
        "offset",
        help="add a signed number of DAYS to DATE (negative values subtract)",
    )
    offset.add_argument("date", type=parse_iso_date, metavar="DATE")
    offset.add_argument("days", type=parse_day_offset, metavar="DAYS")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "between":
        difference = (args.end - args.start).days
        unit = "day" if abs(difference) == 1 else "days"
        print(f"{difference} {unit} (END - START)")
    else:
        try:
            result = args.date + timedelta(days=args.days)
        except OverflowError:
            parser.error("resulting date is outside the supported date range")
        operation = "+" if args.days >= 0 else "-"
        amount = abs(args.days)
        unit = "day" if amount == 1 else "days"
        print(
            f"{args.date.isoformat()} {operation} {amount} {unit} = "
            f"{result.isoformat()}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

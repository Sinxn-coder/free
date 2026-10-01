"""Command-line conversions for common temperature, distance, and mass units."""

import argparse
from decimal import Decimal, DecimalException


UNIT_ALIASES = {
    "c": ("temperature", "C"),
    "celsius": ("temperature", "C"),
    "f": ("temperature", "F"),
    "fahrenheit": ("temperature", "F"),
    "k": ("temperature", "K"),
    "kelvin": ("temperature", "K"),
    "mm": ("distance", "mm"),
    "millimeter": ("distance", "mm"),
    "millimeters": ("distance", "mm"),
    "cm": ("distance", "cm"),
    "centimeter": ("distance", "cm"),
    "centimeters": ("distance", "cm"),
    "m": ("distance", "m"),
    "meter": ("distance", "m"),
    "meters": ("distance", "m"),
    "km": ("distance", "km"),
    "kilometer": ("distance", "km"),
    "kilometers": ("distance", "km"),
    "in": ("distance", "in"),
    "inch": ("distance", "in"),
    "inches": ("distance", "in"),
    "ft": ("distance", "ft"),
    "foot": ("distance", "ft"),
    "feet": ("distance", "ft"),
    "yd": ("distance", "yd"),
    "yard": ("distance", "yd"),
    "yards": ("distance", "yd"),
    "mi": ("distance", "mi"),
    "mile": ("distance", "mi"),
    "miles": ("distance", "mi"),
    "mg": ("mass", "mg"),
    "milligram": ("mass", "mg"),
    "milligrams": ("mass", "mg"),
    "g": ("mass", "g"),
    "gram": ("mass", "g"),
    "grams": ("mass", "g"),
    "kg": ("mass", "kg"),
    "kilogram": ("mass", "kg"),
    "kilograms": ("mass", "kg"),
    "oz": ("mass", "oz"),
    "ounce": ("mass", "oz"),
    "ounces": ("mass", "oz"),
    "lb": ("mass", "lb"),
    "lbs": ("mass", "lb"),
    "pound": ("mass", "lb"),
    "pounds": ("mass", "lb"),
}

DISTANCE_IN_METERS = {
    "mm": Decimal("0.001"),
    "cm": Decimal("0.01"),
    "m": Decimal("1"),
    "km": Decimal("1000"),
    "in": Decimal("0.0254"),
    "ft": Decimal("0.3048"),
    "yd": Decimal("0.9144"),
    "mi": Decimal("1609.344"),
}

MASS_IN_GRAMS = {
    "mg": Decimal("0.001"),
    "g": Decimal("1"),
    "kg": Decimal("1000"),
    "oz": Decimal("28.349523125"),
    "lb": Decimal("453.59237"),
}

SUPPORTED_UNITS = {
    "temperature": "C, F, K",
    "distance": "mm, cm, m, km, in, ft, yd, mi",
    "mass": "mg, g, kg, oz, lb",
}


def resolve_unit(unit: str) -> tuple[str, str]:
    """Return a unit's category and canonical symbol."""
    resolved = UNIT_ALIASES.get(unit.strip().lower())
    if resolved is None:
        raise ValueError(
            f"Unknown unit {unit!r}. Supported units: "
            + "; ".join(
                f"{category}: {symbols}"
                for category, symbols in SUPPORTED_UNITS.items()
            )
        )
    return resolved


def convert(value: Decimal, source_unit: str, target_unit: str) -> Decimal:
    """Convert a Decimal value between compatible units."""
    if not value.is_finite():
        raise ValueError("Value must be a finite number.")

    source_category, source = resolve_unit(source_unit)
    target_category, target = resolve_unit(target_unit)
    if source_category != target_category:
        raise ValueError(
            f"Cannot convert {source_category} unit {source_unit!r} "
            f"to {target_category} unit {target_unit!r}."
        )

    if source_category == "temperature":
        kelvin = {
            "C": value + Decimal("273.15"),
            "F": (value + Decimal("459.67")) * Decimal(5) / Decimal(9),
            "K": value,
        }[source]
        if kelvin < 0:
            raise ValueError("Temperature cannot be below absolute zero (0 K).")
        if target == "C":
            return kelvin - Decimal("273.15")
        if target == "F":
            return kelvin * Decimal(9) / Decimal(5) - Decimal("459.67")
        return kelvin

    factors = DISTANCE_IN_METERS if source_category == "distance" else MASS_IN_GRAMS
    base_value = value * factors[source]
    return base_value / factors[target]


def format_decimal(value: Decimal) -> str:
    """Format a Decimal without unnecessary trailing fractional zeroes."""
    formatted = format(value, "f")
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")
    return formatted or "0"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert common temperature, distance, and mass units."
    )
    parser.add_argument("value", help="numeric value to convert")
    parser.add_argument("source_unit", help="unit to convert from")
    parser.add_argument("target_unit", help="unit to convert to")
    args = parser.parse_args()

    try:
        value = Decimal(args.value)
        result = convert(value, args.source_unit, args.target_unit)
    except (DecimalException, ValueError) as error:
        parser.error(str(error))

    source = resolve_unit(args.source_unit)[1]
    target = resolve_unit(args.target_unit)[1]
    print(
        f"{format_decimal(value)} {source} = "
        f"{format_decimal(result)} {target}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

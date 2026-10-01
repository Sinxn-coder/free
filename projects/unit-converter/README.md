# Unit Converter

A Python 3 command-line converter for common temperature, distance, and mass
units. It uses only the Python standard library.

## Usage

```console
python converter.py 100 C F
python converter.py 1.5 miles km
python converter.py 2.2 kg lb
```

The command takes a numeric value, an explicit source unit, and an explicit
target unit, in that order. Unit names and symbols are case-insensitive.
Conversions between different categories are rejected. Temperatures below
absolute zero and non-finite numeric values are rejected with a usage error.
Repeating conversions are rounded according to Python's `decimal` context
(28 significant digits by default).

## Supported units

| Category | Canonical symbol | Accepted names and aliases |
| --- | --- | --- |
| Temperature | `C` | `c`, `celsius` |
| Temperature | `F` | `f`, `fahrenheit` |
| Temperature | `K` | `k`, `kelvin` |
| Distance | `mm` | `millimeter`, `millimeters` |
| Distance | `cm` | `centimeter`, `centimeters` |
| Distance | `m` | `meter`, `meters` |
| Distance | `km` | `kilometer`, `kilometers` |
| Distance | `in` | `inch`, `inches` |
| Distance | `ft` | `foot`, `feet` |
| Distance | `yd` | `yard`, `yards` |
| Distance | `mi` | `mile`, `miles` |
| Mass | `mg` | `milligram`, `milligrams` |
| Mass | `g` | `gram`, `grams` |
| Mass | `kg` | `kilogram`, `kilograms` |
| Mass | `oz` | `ounce`, `ounces` |
| Mass | `lb` | `lbs`, `pound`, `pounds` |

## Conversion definitions

- Temperature conversions use the exact Celsius/Fahrenheit offset (`273.15 K`
  and `459.67 F`) and the `5/9` and `9/5` scale ratios.
- Distances convert through meters: inch = `0.0254 m`, foot = `0.3048 m`,
  yard = `0.9144 m`, and mile = `1609.344 m`; metric prefixes use powers of
  ten.
- Masses convert through grams: avoirdupois ounce = `28.349523125 g` and
  pound = `453.59237 g`; metric prefixes use powers of ten.

The formulas are evaluated with `decimal.Decimal`; results involving repeating
fractions are rounded using the active Decimal context.

## Tests

Run the standard-library test suite from the repository root:

```console
python -m unittest discover -s projects/unit-converter -v
```

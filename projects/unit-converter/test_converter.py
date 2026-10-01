import unittest
from decimal import Decimal

from converter import convert, resolve_unit


class ConversionTests(unittest.TestCase):
    def test_temperature_conversions(self):
        self.assertEqual(convert(Decimal("100"), "C", "F"), Decimal("212.00"))
        self.assertEqual(convert(Decimal("32"), "fahrenheit", "celsius"), Decimal("0.00"))
        self.assertEqual(convert(Decimal("0"), "C", "K"), Decimal("273.15"))
        self.assertEqual(convert(Decimal("273.15"), "K", "C"), Decimal("0.00"))

    def test_distance_conversions(self):
        self.assertEqual(convert(Decimal("1"), "mi", "m"), Decimal("1609.344"))
        self.assertEqual(convert(Decimal("12"), "in", "ft"), Decimal("1"))
        self.assertEqual(convert(Decimal("1"), "km", "cm"), Decimal("100000"))

    def test_mass_conversions(self):
        self.assertEqual(convert(Decimal("1"), "kg", "g"), Decimal("1000"))
        self.assertEqual(convert(Decimal("1"), "lb", "oz"), Decimal("16"))
        self.assertEqual(convert(Decimal("1"), "oz", "g"), Decimal("28.349523125"))

    def test_units_are_case_insensitive(self):
        self.assertEqual(resolve_unit("CELSIUS"), ("temperature", "C"))

    def test_unknown_unit_lists_supported_units(self):
        with self.assertRaisesRegex(ValueError, "Unknown unit.*temperature.*distance.*mass"):
            convert(Decimal("1"), "league", "m")

    def test_incompatible_categories_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Cannot convert distance unit"):
            convert(Decimal("1"), "m", "kg")

    def test_temperature_below_absolute_zero_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "below absolute zero"):
            convert(Decimal("-274"), "C", "K")

    def test_non_finite_values_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "finite number"):
            convert(Decimal("NaN"), "kg", "g")


if __name__ == "__main__":
    unittest.main()

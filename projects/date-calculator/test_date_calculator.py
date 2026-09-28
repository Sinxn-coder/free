import argparse
import contextlib
import io
import unittest
from datetime import date

from date_calculator import main, parse_iso_date


class ParseISODateTests(unittest.TestCase):
    def test_accepts_leap_day(self):
        self.assertEqual(parse_iso_date("2024-02-29"), date(2024, 2, 29))

    def test_rejects_invalid_or_non_iso_dates(self):
        for value in ("2023-02-29", "2024-2-09", "20240229", "not-a-date"):
            with self.subTest(value=value):
                with self.assertRaises(argparse.ArgumentTypeError):
                    parse_iso_date(value)


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(list(args))
        return result, output.getvalue()

    def test_same_date_difference(self):
        result, output = self.run_cli("between", "2024-02-29", "2024-02-29")

        self.assertEqual(result, 0)
        self.assertEqual(output, "0 days (END - START)\n")

    def test_difference_is_signed_and_order_is_explicit(self):
        result, output = self.run_cli("between", "2024-03-01", "2024-02-29")

        self.assertEqual(result, 0)
        self.assertEqual(output, "-1 day (END - START)\n")

    def test_offset_adds_across_leap_day(self):
        result, output = self.run_cli("offset", "2024-02-28", "1")

        self.assertEqual(result, 0)
        self.assertEqual(output, "2024-02-28 + 1 day = 2024-02-29\n")

    def test_negative_offset_subtracts_days(self):
        result, output = self.run_cli("offset", "2024-03-01", "-1")

        self.assertEqual(result, 0)
        self.assertEqual(output, "2024-03-01 - 1 day = 2024-02-29\n")

    def test_invalid_input_exits_with_validation_error(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                main(["between", "2023-02-29", "2023-03-01"])

        self.assertEqual(error.exception.code, 2)

    def test_non_integer_offset_exits_with_validation_error(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                main(["offset", "2024-03-01", "1.5"])

        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()

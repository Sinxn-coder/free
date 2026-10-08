import subprocess
import sys
import unittest
from pathlib import Path

from quotes import QUOTES, random_quote


class QuoteTests(unittest.TestCase):
    def test_category_returns_matching_quote(self):
        self.assertEqual(random_quote("focus", seed=1), "The secret of getting ahead is getting started.")

    def test_cli_seed_reproduces_output(self):
        script = Path(__file__).with_name("quotes.py")
        command = [sys.executable, str(script), "--seed", "17"]

        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout.strip()
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout.strip()

        self.assertEqual(first, second)
        self.assertEqual(first, random_quote(seed=17))

    def test_cli_seed_preserves_category_filter(self):
        script = Path(__file__).with_name("quotes.py")
        result = subprocess.run(
            [sys.executable, str(script), "--category", "learning", "--seed", "17"],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.strip(), random_quote("learning", seed=17))

    def test_cli_without_seed_still_prints_a_quote(self):
        script = Path(__file__).with_name("quotes.py")
        result = subprocess.run(
            [sys.executable, str(script)],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn(result.stdout.strip(), sum(QUOTES.values(), []))


if __name__ == "__main__":
    unittest.main()

import unittest

from quotes import random_quote


class QuoteTests(unittest.TestCase):
    def test_category_returns_matching_quote(self):
        self.assertEqual(random_quote("focus", seed=1), "The secret of getting ahead is getting started.")


if __name__ == "__main__":
    unittest.main()

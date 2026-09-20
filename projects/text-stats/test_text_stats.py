import unittest

from text_stats import statistics


class TextStatsTests(unittest.TestCase):
    def test_counts_text(self):
        result = statistics("Hello world\nHello")
        self.assertEqual(result["words"], 3)
        self.assertEqual(result["unique_words"], 2)
        self.assertEqual(result["lines"], 2)


if __name__ == "__main__":
    unittest.main()

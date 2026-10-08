import unittest

from text_stats import statistics


class TextStatsTests(unittest.TestCase):
    def test_counts_text(self):
        result = statistics("Hello world\nHello")
        self.assertEqual(result["words"], 3)
        self.assertEqual(result["unique_words"], 2)
        self.assertEqual(result["lines"], 2)

    def test_empty_text_has_no_paragraphs(self):
        self.assertEqual(statistics("")["paragraphs"], 0)

    def test_blank_lines_separate_paragraphs(self):
        result = statistics("First paragraph\n \t\n\nSecond paragraph\n")
        self.assertEqual(result["paragraphs"], 2)

    def test_normal_paragraphs(self):
        result = statistics("First line\ncontinues here\n\nAnother paragraph")
        self.assertEqual(result["paragraphs"], 2)


if __name__ == "__main__":
    unittest.main()

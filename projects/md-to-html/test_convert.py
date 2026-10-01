import unittest

from convert import convert


class ConvertTests(unittest.TestCase):
    def test_converts_headings_and_bold_text(self):
        result = convert("# Title\n\nThis is **important**.")
        self.assertIn("<h1>Title</h1>", result)
        self.assertIn("<strong>important</strong>", result)


if __name__ == "__main__":
    unittest.main()

import unittest

from shortener import shorten


class ShortenerTests(unittest.TestCase):
    def test_shortens_and_stores_url(self):
        mappings = {}
        code = shorten("https://example.com", mappings)
        self.assertEqual(mappings[code], "https://example.com")
        self.assertEqual(len(code), 8)


if __name__ == "__main__":
    unittest.main()

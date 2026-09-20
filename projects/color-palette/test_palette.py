import unittest

from palette import palette


class PaletteTests(unittest.TestCase):
    def test_seed_makes_output_repeatable(self):
        self.assertEqual(palette(3, 10), palette(3, 10))
        self.assertTrue(all(len(color) == 7 for color in palette(3, 10)))


if __name__ == "__main__":
    unittest.main()

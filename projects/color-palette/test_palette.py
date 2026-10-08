from pathlib import Path
import subprocess
import sys
import unittest

from palette import palette


class PaletteTests(unittest.TestCase):
    def test_seed_makes_output_repeatable(self):
        self.assertEqual(palette(3, 10), palette(3, 10))
        self.assertTrue(all(len(color) == 7 for color in palette(3, 10)))

    def test_seeded_output_remains_unchanged(self):
        self.assertEqual(
            palette(5, 42),
            ["#390062", "#0CCE35", "#8CD0A4", "#7D6277", "#7248AD"],
        )

    def test_unique_palette_has_no_repeated_colors(self):
        result = palette(100, seed=42, unique=True)

        self.assertEqual(len(result), 100)
        self.assertEqual(len(set(result)), 100)
        self.assertEqual(result, palette(100, seed=42, unique=True))

    def test_unique_palette_rejects_count_over_color_space(self):
        with self.assertRaisesRegex(ValueError, "number of available HEX colors"):
            palette(0x1000001, unique=True)

    def test_cli_unique_option_outputs_unique_colors(self):
        script = Path(__file__).with_name("palette.py")
        result = subprocess.run(
            [sys.executable, str(script), "--count", "20", "--seed", "42", "--unique"],
            capture_output=True,
            check=True,
            text=True,
        )
        colors = result.stdout.splitlines()

        self.assertEqual(len(colors), 20)
        self.assertEqual(len(set(colors)), 20)


if __name__ == "__main__":
    unittest.main()

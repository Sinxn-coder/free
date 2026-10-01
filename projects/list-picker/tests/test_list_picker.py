import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from list_picker import choose_item, load_items


class ListPickerTests(unittest.TestCase):
    def write_items(self, directory: str, content: str) -> Path:
        path = Path(directory) / "items.txt"
        path.write_text(content, encoding="utf-8")
        return path

    def test_seeded_selection_is_reproducible(self) -> None:
        items = ["apple", "banana", "cherry", "date"]
        self.assertEqual(choose_item(items, seed="demo"), choose_item(items, seed="demo"))
        self.assertIn(choose_item(items, seed="demo"), items)

    def test_blank_lines_are_ignored_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_items(directory, "\n  \napple\n\nbanana\n")
            self.assertEqual(load_items(path), ["apple", "banana"])

    def test_blank_lines_can_be_kept(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_items(directory, "\napple\n \n")
            self.assertEqual(
                load_items(path, ignore_blank_lines=False),
                ["", "apple", ""],
            )

    def test_choose_item_rejects_empty_inputs(self) -> None:
        with self.assertRaisesRegex(ValueError, "empty list"):
            choose_item([])

    def test_cli_reports_empty_file_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_items(directory, "\n  \n")
            script = Path(__file__).parents[1] / "list_picker.py"
            result = subprocess.run(
                [sys.executable, str(script), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("no selectable items", result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()

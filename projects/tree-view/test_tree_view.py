import tempfile
import unittest
from pathlib import Path

from tree_view import render


class TreeViewTests(unittest.TestCase):
    def test_renders_nested_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "child").mkdir()
            (root / "child" / "file.txt").touch()
            output = "\n".join(render(root))
            self.assertIn("child", output)
            self.assertIn("file.txt", output)

    def test_renders_hidden_entries_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hidden_directory = root / ".hidden-directory"
            hidden_directory.mkdir()
            (hidden_directory / ".hidden-file").touch()

            output = "\n".join(render(root))

            self.assertIn(".hidden-directory", output)
            self.assertIn(".hidden-file", output)

    def test_no_hidden_omits_hidden_entries_at_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".hidden-file").touch()
            (root / ".hidden-directory").mkdir()
            (root / "visible-file").touch()

            output = "\n".join(render(root, no_hidden=True))

            self.assertIn("visible-file", output)
            self.assertNotIn(".hidden-file", output)
            self.assertNotIn(".hidden-directory", output)

    def test_no_hidden_omits_nested_hidden_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = root / "visible-directory"
            child.mkdir()
            (child / ".hidden-file").touch()
            (child / ".hidden-directory").mkdir()
            (child / "visible-file").touch()

            output = "\n".join(render(root, no_hidden=True))

            self.assertIn("visible-directory", output)
            self.assertIn("visible-file", output)
            self.assertNotIn(".hidden-file", output)
            self.assertNotIn(".hidden-directory", output)


if __name__ == "__main__":
    unittest.main()

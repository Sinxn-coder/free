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


if __name__ == "__main__":
    unittest.main()

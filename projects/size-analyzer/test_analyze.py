import tempfile
import unittest
from pathlib import Path

from analyze import largest_files


class AnalyzeTests(unittest.TestCase):
    def test_returns_largest_files_first(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "small.txt").write_text("x")
            (root / "large.txt").write_text("xxxxx")
            result = largest_files(root, 1)
            self.assertEqual(result[0][1].name, "large.txt")


if __name__ == "__main__":
    unittest.main()

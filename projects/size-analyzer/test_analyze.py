import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from analyze import format_size, largest_files, main


class AnalyzeTests(unittest.TestCase):
    def test_returns_largest_files_first(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "small.txt").write_text("x")
            (root / "large.txt").write_text("xxxxx")
            result = largest_files(root, 1)
            self.assertEqual(result[0][1].name, "large.txt")

    def test_format_size_uses_binary_units(self):
        self.assertEqual(format_size(0), "0 B")
        self.assertEqual(format_size(1023), "1023 B")
        self.assertEqual(format_size(1024), "1.0 KiB")
        self.assertEqual(format_size(1024**2), "1.0 MiB")

    def test_cli_keeps_bytes_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.bin").write_bytes(b"x" * 1024)
            output = io.StringIO()
            with patch("sys.argv", ["analyze.py", str(root)]), redirect_stdout(output):
                main()
            self.assertEqual(output.getvalue(), f"{1024:>10} bytes  {root / 'sample.bin'}\n")

    def test_cli_supports_human_readable_sizes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.bin").write_bytes(b"x" * 1024)
            output = io.StringIO()
            with patch(
                "sys.argv", ["analyze.py", str(root), "--human-readable"]
            ), redirect_stdout(output):
                main()
            self.assertEqual(output.getvalue(), f"{'1.0 KiB':>10}  {root / 'sample.bin'}\n")


if __name__ == "__main__":
    unittest.main()

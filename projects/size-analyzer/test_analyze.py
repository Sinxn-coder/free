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

    def test_minimum_size_filters_files_in_bytes_inclusively(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "below.txt").write_bytes(b"x" * 3)
            (root / "at-limit.txt").write_bytes(b"x" * 4)
            (root / "above.txt").write_bytes(b"x" * 5)

            result = largest_files(root, min_size=4)

            self.assertEqual(
                [(size, path.name) for size, path in result],
                [(5, "above.txt"), (4, "at-limit.txt")],
            )

    def test_default_minimum_size_includes_all_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "empty.txt").write_bytes(b"")
            (root / "small.txt").write_bytes(b"x")

            result = largest_files(root)

            self.assertEqual(
                {path.name for _, path in result}, {"empty.txt", "small.txt"}
            )

    def test_negative_api_limits_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(
                ValueError, "minimum size must be non-negative"
            ):
                largest_files(root, min_size=-1)
            with self.assertRaisesRegex(ValueError, "limit must be non-negative"):
                largest_files(root, limit=-1)

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

    def test_cli_filters_files_by_minimum_size(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "small.bin").write_bytes(b"x" * 3)
            (root / "large.bin").write_bytes(b"x" * 5)
            output = io.StringIO()
            with patch(
                "sys.argv", ["analyze.py", str(root), "--min-size", "4"]
            ), redirect_stdout(output):
                main()
            self.assertEqual(
                output.getvalue(), f"{5:>10} bytes  {root / 'large.bin'}\n"
            )

    def test_cli_rejects_negative_limits(self):
        for option in ("--min-size", "--top"):
            with self.subTest(option=option), patch(
                "sys.argv", ["analyze.py", ".", option, "-1"]
            ), self.assertRaises(SystemExit) as error:
                main()
            self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()

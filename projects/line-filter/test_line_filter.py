import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from line_filter import filter_lines


SCRIPT = Path(__file__).with_name("line_filter.py")


class FilterLinesTests(unittest.TestCase):
    def test_selects_matching_lines_without_changing_line_endings(self):
        lines = ["keep this\r\n", "skip this\n", "keep café"]

        result = list(filter_lines(lines, re.compile(r"^keep")))

        self.assertEqual(result, ["keep this\r\n", "keep café"])

    def test_invert_selects_non_matching_lines(self):
        lines = ["match\n", "other\n", "another"]

        result = list(filter_lines(lines, re.compile("match"), invert=True))

        self.assertEqual(result, ["other\n", "another"])

    def test_case_insensitive_pattern_matches_mixed_case_content(self):
        lines = ["ERROR: failed\n", "warning\n", "error recovered"]

        result = list(filter_lines(lines, re.compile("error", re.IGNORECASE)))

        self.assertEqual(result, ["ERROR: failed\n", "error recovered"])


class CommandLineTests(unittest.TestCase):
    def run_cli(self, pattern, file, *options):
        return subprocess.run(
            [sys.executable, str(SCRIPT), pattern, str(file), *options],
            capture_output=True,
            check=False,
        )

    def test_prints_selected_content_exactly(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "input.txt"
            file.write_bytes("keep café\r\nskip\nkeep-final".encode("utf-8"))

            result = self.run_cli("keep", file)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "keep café\r\nkeep-final".encode("utf-8"))

    def test_invert_option_prints_non_matching_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "input.txt"
            file.write_bytes(b"match\nother\n")

            result = self.run_cli("match", file, "--invert")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"other\n")

    def test_ignore_case_short_and_long_options_match_mixed_case_content(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "input.txt"
            file.write_bytes(b"ERROR: failed\nwarning\nError recovered")

            with self.subTest(option="-i"):
                short_result = self.run_cli("error", file, "-i")
            with self.subTest(option="--ignore-case"):
                long_result = self.run_cli("error", file, "--ignore-case")

        expected = b"ERROR: failed\nError recovered"
        self.assertEqual(short_result.returncode, 0)
        self.assertEqual(short_result.stdout, expected)
        self.assertEqual(long_result.returncode, 0)
        self.assertEqual(long_result.stdout, expected)

    def test_matching_is_case_sensitive_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "input.txt"
            file.write_bytes(b"ERROR\nerror\n")

            result = self.run_cli("error", file)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"error\n")

    def test_invalid_regex_has_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "input.txt"
            file.write_text("content", encoding="utf-8")

            result = self.run_cli("[", file)

        self.assertEqual(result.returncode, 2)
        self.assertIn(b"invalid regular expression", result.stderr)

    def test_missing_file_has_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "missing.txt"

            result = self.run_cli("match", file)

        self.assertEqual(result.returncode, 2)
        self.assertIn(b"cannot read", result.stderr)

    def test_invalid_utf8_has_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "input.txt"
            file.write_bytes(b"\xff")

            result = self.run_cli("match", file)

        self.assertEqual(result.returncode, 2)
        self.assertIn(b"cannot read", result.stderr)


if __name__ == "__main__":
    unittest.main()

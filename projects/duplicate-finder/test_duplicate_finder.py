import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from duplicate_finder import file_digest, find_duplicates, main


class DuplicateFinderTests(unittest.TestCase):
    def test_finds_identical_files_recursively(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first.txt"
            nested = root / "nested"
            nested.mkdir()
            second = nested / "second.txt"
            first.write_bytes(b"same content")
            second.write_bytes(b"same content")
            (root / "different.txt").write_bytes(b"diff content")

            result = find_duplicates(root)

            self.assertEqual(len(result.duplicates), 1)
            self.assertEqual(set(result.duplicates[0].paths), {first, second})
            self.assertEqual(result.duplicates[0].size, len(b"same content"))
            self.assertEqual(result.errors, ())

    def test_only_hashes_files_when_sizes_match(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "one.txt").write_bytes(b"one")
            (root / "two.txt").write_bytes(b"two")
            (root / "unique.txt").write_bytes(b"unique size")
            original_digest = file_digest

            with patch(
                "duplicate_finder.file_digest", wraps=original_digest
            ) as digest:
                result = find_duplicates(root)

            self.assertEqual(result.duplicates, ())
            self.assertEqual(digest.call_count, 2)

    def test_reports_unreadable_file_and_cli_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unreadable = root / "unreadable.txt"
            readable = root / "readable.txt"
            unreadable.write_bytes(b"same")
            readable.write_bytes(b"same")
            original_digest = file_digest

            def digest(path):
                if path == unreadable:
                    raise PermissionError("permission denied")
                return original_digest(path)

            with patch("duplicate_finder.file_digest", side_effect=digest):
                result = find_duplicates(root)
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    exit_code = main([str(root)])

            self.assertEqual(result.duplicates, ())
            self.assertEqual(len(result.errors), 1)
            self.assertEqual(result.errors[0].path, unreadable)
            self.assertIn("permission denied", result.errors[0].message)
            self.assertEqual(exit_code, 1)
            self.assertIn(str(unreadable), stderr.getvalue())

    def test_rejects_non_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "file.txt"
            path.touch()

            with self.assertRaises(NotADirectoryError):
                find_duplicates(path)

    def test_cli_reports_no_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "file.txt").write_text("only one")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main([directory])

        self.assertEqual(exit_code, 0)
        self.assertIn("No duplicate files found.", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()

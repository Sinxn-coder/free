import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import duplicate_finder


class DuplicateFinderTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_file(self, relative_path, content):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def run_cli(self, *args):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = duplicate_finder.main(list(map(str, args)))
        return status, stdout.getvalue(), stderr.getvalue()

    def test_detects_exact_duplicates_and_reports_reclaimable_bytes(self):
        first = self.write_file("one.bin", b"identical")
        second = self.write_file("nested/two.bin", b"identical")

        result = duplicate_finder.find_duplicates([str(self.root)])

        self.assertEqual(len(result.groups), 1)
        group = result.groups[0]
        self.assertEqual(group.files, tuple(sorted(
            (str(first), str(second)), key=duplicate_finder._path_key
        )))
        self.assertEqual(group.bytes_reclaimable, len(b"identical"))
        self.assertEqual(result.bytes_reclaimable, len(b"identical"))

    def test_same_size_different_content_is_not_duplicate(self):
        self.write_file("first", b"same size")
        self.write_file("second", b"diff size")

        status, output, _ = self.run_cli(self.root)

        self.assertEqual(status, 0)
        self.assertIn("No duplicate files found.", output)

    def test_nested_folders_are_scanned(self):
        self.write_file("top/a.bin", b"nested")
        self.write_file("top/deeper/b.bin", b"nested")

        result = duplicate_finder.find_duplicates([str(self.root)])

        self.assertEqual(len(result.groups), 1)
        self.assertEqual(len(result.groups[0].files), 2)

    def test_overlapping_roots_do_not_repeat_a_physical_path(self):
        first = self.write_file("outer/a.bin", b"same")
        second = self.write_file("outer/inner/b.bin", b"same")

        result = duplicate_finder.find_duplicates(
            [str(self.root / "outer"), str(self.root / "outer" / "inner")]
        )

        self.assertEqual(len(result.groups), 1)
        self.assertEqual(len(result.groups[0].files), 2)
        self.assertEqual(set(result.groups[0].files), {str(first), str(second)})
        self.assertEqual(result.files_scanned, 2)

    def test_json_output_is_deterministic(self):
        self.write_file("z.bin", b"same")
        self.write_file("a.bin", b"same")

        first = self.run_cli("--json", self.root)
        second = self.run_cli("--json", self.root)

        self.assertEqual(first, second)
        self.assertEqual(first[0], 1)
        parsed = json.loads(first[1])
        self.assertEqual(
            set(parsed),
            {"duplicates", "errors", "summary"},
        )
        self.assertEqual(parsed["summary"]["bytes_reclaimable"], 4)

    def test_invalid_path_appears_in_json_and_stderr_with_exit_two(self):
        missing = self.root / "missing"

        status, output, stderr = self.run_cli("--json", missing)

        report = json.loads(output)
        self.assertEqual(status, 2)
        self.assertEqual(report["errors"][0]["path"], str(missing))
        self.assertIn(str(missing), stderr)

    def test_hash_read_error_is_reported_without_silencing(self):
        self.write_file("first", b"same")
        self.write_file("second", b"same")
        with mock.patch(
            "duplicate_finder._hash_file", side_effect=PermissionError("denied")
        ):
            status, output, stderr = self.run_cli("--json", self.root)

        report = json.loads(output)
        self.assertEqual(status, 2)
        self.assertEqual(len(report["errors"]), 2)
        self.assertIn("denied", stderr)

    def test_large_files_are_hashed_in_bounded_chunks(self):
        content = bytes(range(256)) * 4097
        self.write_file("large/first.bin", content)
        self.write_file("large/second.bin", content)
        chunk_size = 64 * 1024
        observed_chunk_sizes = []
        original_read_chunks = duplicate_finder.read_chunks

        def record_chunks(stream, requested_size):
            self.assertEqual(requested_size, chunk_size)
            for chunk in original_read_chunks(stream, requested_size):
                observed_chunk_sizes.append(len(chunk))
                yield chunk

        with mock.patch(
            "duplicate_finder.read_chunks", side_effect=record_chunks
        ):
            result = duplicate_finder.find_duplicates(
                [str(self.root)], chunk_size=chunk_size
            )

        self.assertEqual(len(result.groups), 1)
        self.assertGreater(len(content), chunk_size)
        self.assertTrue(observed_chunk_sizes)
        self.assertLessEqual(max(observed_chunk_sizes), chunk_size)

    @unittest.skipUnless(hasattr(os, "symlink"), "symbolic links are unavailable")
    def test_symbolic_link_files_are_not_followed(self):
        target = self.write_file("target.bin", b"same")
        duplicate = self.write_file("duplicate.bin", b"same")
        link = self.root / "link.bin"
        try:
            link.symlink_to(target)
        except OSError as error:
            self.skipTest(f"cannot create symbolic links: {error}")

        result = duplicate_finder.find_duplicates([str(self.root)])

        self.assertEqual(len(result.groups), 1)
        self.assertEqual(set(result.groups[0].files), {str(target), str(duplicate)})
        self.assertNotIn(str(link), result.groups[0].files)


if __name__ == "__main__":
    unittest.main()

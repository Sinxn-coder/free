import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import text_diff_viewer


class TextDiffViewerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.old_file = self.root / "old.txt"
        self.new_file = self.root / "new.txt"

    def run_cli(self, *args):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = text_diff_viewer.main(
                [str(self.old_file), str(self.new_file), *args]
            )
        return status, stdout.getvalue(), stderr.getvalue()

    def test_equal_inputs_return_success_without_output(self):
        self.old_file.write_text("same\ncontent\n", encoding="utf-8")
        self.new_file.write_text("same\ncontent\n", encoding="utf-8")

        status, stdout, stderr = self.run_cli()

        self.assertEqual(status, 0)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "")

    def test_different_inputs_show_unified_diff(self):
        self.old_file.write_text("before\n", encoding="utf-8")
        self.new_file.write_text("after\n", encoding="utf-8")

        status, stdout, stderr = self.run_cli()

        self.assertEqual(status, 1)
        self.assertEqual(
            stdout,
            f"--- {self.old_file}\n+++ {self.new_file}\n@@ -1 +1 @@\n-before\n+after\n",
        )
        self.assertEqual(stderr, "")

    def test_crlf_and_lf_line_endings_are_normalized(self):
        self.old_file.write_bytes(b"first\r\nsecond\r\n")
        self.new_file.write_bytes(b"first\nsecond\n")

        status, stdout, stderr = self.run_cli()

        self.assertEqual(status, 0)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "")

    def test_context_option_controls_surrounding_lines(self):
        self.old_file.write_text("one\ntwo\nold\nfour\nfive\n", encoding="utf-8")
        self.new_file.write_text("one\ntwo\nnew\nfour\nfive\n", encoding="utf-8")

        status, stdout, stderr = self.run_cli("--context", "1")

        self.assertEqual(status, 1)
        self.assertIn("@@ -2,3 +2,3 @@", stdout)
        self.assertIn(" two\n-old\n+new\n four\n", stdout)
        self.assertNotIn("one", stdout)
        self.assertNotIn("five", stdout)
        self.assertEqual(stderr, "")

    def test_missing_file_has_clear_error(self):
        status, stdout, stderr = self.run_cli()

        self.assertEqual(status, 2)
        self.assertEqual(stdout, "")
        self.assertIn(f"error: file not found: {self.old_file}", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_negative_context_is_rejected(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as error:
                text_diff_viewer.main(
                    [str(self.old_file), str(self.new_file), "--context", "-1"]
                )

        self.assertEqual(error.exception.code, 2)
        self.assertIn("must be a non-negative integer", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()

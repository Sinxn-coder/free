import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import whitespace_auditor


class WhitespaceAuditorTests(unittest.TestCase):
    def test_check_reports_each_finding_and_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            original = b"first  \r\nsecond\t"
            path.write_bytes(original)
            output = io.StringIO()
            with (
                contextlib.redirect_stdout(output),
                mock.patch.object(
                    whitespace_auditor,
                    "write_atomically",
                    side_effect=AssertionError("check mode must not write"),
                ),
            ):
                result = whitespace_auditor.run([path])

            self.assertEqual(result, 1)
            self.assertEqual(
                output.getvalue().splitlines(),
                [
                    f"{path}:1: trailing whitespace",
                    f"{path}:2: trailing whitespace",
                    f"{path}:2: missing final newline",
                ],
            )
            self.assertEqual(path.read_bytes(), original)

    def test_fix_removes_trailing_whitespace_and_adds_final_newline(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            path.write_bytes(b"first  \r\nsecond\t")

            result = whitespace_auditor.run([path], fix=True)

            self.assertEqual(result, 0)
            self.assertEqual(path.read_bytes(), b"first\r\nsecond\r\n")

    def test_fix_preserves_utf8_bom_and_mixed_newlines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            path.write_bytes(b"\xef\xbb\xbfalpha \r\nbeta\t\nlast")

            result = whitespace_auditor.run([path], fix=True)

            self.assertEqual(result, 0)
            self.assertEqual(
                path.read_bytes(), b"\xef\xbb\xbfalpha\r\nbeta\nlast\r\n"
            )

    def test_fix_preserves_utf16_encoding_and_carriage_return_newlines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            path.write_bytes("alpha \rbeta\t".encode("utf-16"))

            result = whitespace_auditor.run([path], fix=True)

            self.assertEqual(result, 0)
            self.assertEqual(path.read_bytes(), "alpha\rbeta\r".encode("utf-16"))

    def test_clean_file_is_unchanged_and_returns_success(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "clean.txt"
            content = "clean\r\n".encode("utf-8")
            path.write_bytes(content)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = whitespace_auditor.run([path])

            self.assertEqual(result, 0)
            self.assertEqual(output.getvalue(), "")
            self.assertEqual(path.read_bytes(), content)

    def test_empty_file_is_clean(self):
        findings, fixed_text = whitespace_auditor.inspect_text("")

        self.assertEqual(findings, [])
        self.assertEqual(fixed_text, "")


if __name__ == "__main__":
    unittest.main()

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import redactor


class RedactTests(unittest.TestCase):
    def test_redacts_common_email_addresses(self):
        text = "Contact jane.doe+tag@example.co.uk or admin@sample.org."
        self.assertEqual(
            redactor.redact(text),
            f"Contact {redactor.REDACTION} or {redactor.REDACTION}.",
        )

    def test_redacts_phone_number_like_strings(self):
        text = "Call +1 (415) 555-2671 or 415.555.2672."
        self.assertEqual(
            redactor.redact(text),
            f"Call {redactor.REDACTION} or {redactor.REDACTION}.",
        )

    def test_leaves_unmatched_text_unchanged(self):
        text = "Nothing to redact: hello, world! 12345."
        self.assertEqual(redactor.redact(text), text)

    def test_replaces_only_matches(self):
        text = "A jane@example.com B 415-555-0100 C"
        self.assertEqual(
            redactor.redact(text),
            f"A {redactor.REDACTION} B {redactor.REDACTION} C",
        )


class CliSafetyTests(unittest.TestCase):
    def invoke(self, *arguments):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch("sys.argv", ["redactor.py", *map(str, arguments)]):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                status = redactor.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def test_writes_to_stdout_by_default_without_changing_input(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.txt"
            source.write_text("jane@example.com", encoding="utf-8")

            status, output, error = self.invoke(source)

            self.assertEqual(status, 0)
            self.assertEqual(output, redactor.REDACTION)
            self.assertEqual(error, "")
            self.assertEqual(source.read_text(encoding="utf-8"), "jane@example.com")

    def test_writes_to_a_new_separate_output_file(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.txt"
            output = Path(directory) / "redacted.txt"
            source.write_text("jane@example.com", encoding="utf-8")

            status, stdout, error = self.invoke(source, "--output", output)

            self.assertEqual(status, 0)
            self.assertEqual(stdout, "")
            self.assertEqual(error, "")
            self.assertEqual(output.read_text(encoding="utf-8"), redactor.REDACTION)
            self.assertEqual(source.read_text(encoding="utf-8"), "jane@example.com")

    def test_refuses_to_overwrite_input(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.txt"
            source.write_text("jane@example.com", encoding="utf-8")

            status, stdout, error = self.invoke(source, "--output", source)

            self.assertEqual(status, 1)
            self.assertEqual(stdout, "")
            self.assertIn("different from the input", error)
            self.assertEqual(source.read_text(encoding="utf-8"), "jane@example.com")

    def test_refuses_to_overwrite_an_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.txt"
            output = Path(directory) / "output.txt"
            source.write_text("jane@example.com", encoding="utf-8")
            output.write_text("keep this", encoding="utf-8")

            status, stdout, error = self.invoke(source, "--output", output)

            self.assertEqual(status, 1)
            self.assertEqual(stdout, "")
            self.assertIn("already exists", error)
            self.assertEqual(output.read_text(encoding="utf-8"), "keep this")


if __name__ == "__main__":
    unittest.main()

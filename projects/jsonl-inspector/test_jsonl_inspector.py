import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from jsonl_inspector import inspect_jsonl, main


class InspectJsonlTests(unittest.TestCase):
    def test_blank_lines_are_ignored(self):
        count, errors = inspect_jsonl(io.StringIO('\n {"ok": true}\n \t\n'))

        self.assertEqual(count, 1)
        self.assertEqual(errors, [])

    def test_malformed_errors_include_physical_line_numbers(self):
        count, errors = inspect_jsonl(io.StringIO('{"ok": true}\nnot json\n\n{broken}\n'))

        self.assertEqual(count, 1)
        self.assertEqual([error.split(":", 1)[0] for error in errors], ["Line 2", "Line 4"])

    def test_multiple_records_are_counted(self):
        count, errors = inspect_jsonl(io.StringIO('{"n": 1}\n[2, 3]\n"four"\n'))

        self.assertEqual(count, 3)
        self.assertEqual(errors, [])

    def test_output_contains_pretty_printed_valid_records_only(self):
        output = io.StringIO()
        count, errors = inspect_jsonl(
            io.StringIO('{"name":"Ada","active":true}\ninvalid\n[1,2]\n'),
            output,
        )

        rendered_records = output.getvalue().strip().split("\n\n")
        self.assertEqual(count, 2)
        self.assertEqual(len(errors), 1)
        self.assertEqual(json.loads(rendered_records[0]), {"name": "Ada", "active": True})
        self.assertIn("\n", rendered_records[0])
        self.assertEqual(json.loads(rendered_records[1]), [1, 2])

    def test_cli_writes_output_and_never_overwrites_input(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "records.jsonl"
            output_path = Path(directory) / "pretty.json"
            original = '{"value": 1}\n'
            input_path.write_text(original, encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                result = main([str(input_path), "--output", str(output_path)])

            self.assertEqual(result, 0)
            self.assertEqual(input_path.read_text(encoding="utf-8"), original)
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), {"value": 1})
            self.assertIn("Total records: 1", stdout.getvalue())

    def test_cli_refuses_output_that_is_input(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "records.jsonl"
            original = '{"value": 1}\n'
            input_path.write_text(original, encoding="utf-8")
            stderr = io.StringIO()

            with redirect_stderr(stderr), self.assertRaises(SystemExit) as error:
                main([str(input_path), "--output", str(input_path)])

            self.assertEqual(error.exception.code, 2)
            self.assertIn("output must be a different file", stderr.getvalue())
            self.assertEqual(input_path.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()

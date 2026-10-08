import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from csv_summary import CsvSummaryError, main, summarize_csv


class CsvSummaryTests(unittest.TestCase):
    def write_csv(self, directory: str, content: str) -> Path:
        path = Path(directory) / "input.csv"
        path.write_text(content, encoding="utf-8")
        return path

    def test_counts_rows_columns_and_non_empty_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_csv(
                directory,
                "name,city,note\nAda,London,\n,Paris,  \nLin,Tokyo,hello\n",
            )

            self.assertEqual(
                summarize_csv(path),
                (3, ["name", "city", "note"], [2, 3, 1]),
            )

    def test_skips_blank_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_csv(directory, "name\nAda\n\n")

            self.assertEqual(summarize_csv(path), (1, ["name"], [1]))

    def test_rejects_inconsistent_row_width(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_csv(directory, "name,city\nAda\n")

            with self.assertRaisesRegex(CsvSummaryError, "row 2 has 1 fields"):
                summarize_csv(path)

    def test_rejects_malformed_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_csv(directory, 'name,note\nAda,"unfinished\n')

            with self.assertRaises(CsvSummaryError):
                summarize_csv(path)

    def test_rejects_file_without_header(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_csv(directory, "\n")

            with self.assertRaisesRegex(CsvSummaryError, "no header"):
                summarize_csv(path)

    def test_reports_unreadable_file(self):
        path = Path("does-not-exist.csv")

        with self.assertRaises(CsvSummaryError):
            summarize_csv(path)

    def test_cli_prints_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_csv(directory, "name,city\nAda,London\n")
            output = io.StringIO()
            with patch("sys.argv", ["csv_summary.py", str(path)]):
                with contextlib.redirect_stdout(output):
                    main()

            self.assertEqual(
                output.getvalue(),
                "Data rows: 1\n"
                "Columns: name, city\n"
                "Non-empty values:\n"
                "  name: 1\n"
                "  city: 1\n",
            )


if __name__ == "__main__":
    unittest.main()

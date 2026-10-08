import csv
import tempfile
import unittest
from pathlib import Path

from csv_cleaner import clean_csv, main


class CleanCsvTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.source = self.directory / "input.csv"
        self.output = self.directory / "output.csv"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def read_output(self) -> list[list[str]]:
        with self.output.open(encoding="utf-8", newline="") as file:
            return list(csv.reader(file))

    def test_trims_cells_and_preserves_quoted_commas_and_newlines(self) -> None:
        self.source.write_text(
            ' Name , Note \r\n Alice ,"  hello, world  "\r\n'
            '" Bob ","  first line\nsecond line  "\r\n',
            encoding="utf-8",
            newline="",
        )

        clean_csv(self.source, self.output)

        self.assertEqual(
            self.read_output(),
            [
                ["Name", "Note"],
                ["Alice", "hello, world"],
                ["Bob", "first line\nsecond line"],
            ],
        )

    def test_normalizes_headers_only_when_requested(self) -> None:
        self.source.write_text(" First Name ,E-mail Address \n Ada , yes \n")

        clean_csv(self.source, self.output, normalize_headers=True)

        self.assertEqual(
            self.read_output(),
            [["first_name", "e_mail_address"], ["Ada", "yes"]],
        )

    def test_refuses_same_input_and_output_without_changing_input(self) -> None:
        original = " Name \n Alice \n"
        self.source.write_text(original)

        with self.assertRaisesRegex(ValueError, "must be different"):
            clean_csv(self.source, self.source, overwrite=True)

        self.assertEqual(self.source.read_text(), original)

    def test_refuses_existing_output_unless_overwrite_is_enabled(self) -> None:
        self.source.write_text(" Name \n Alice \n")
        self.output.write_text("keep this\n")

        with self.assertRaises(FileExistsError):
            clean_csv(self.source, self.output)

        self.assertEqual(self.output.read_text(), "keep this\n")

        clean_csv(self.source, self.output, overwrite=True)

        self.assertEqual(self.read_output(), [["Name"], ["Alice"]])

    def test_cli_reports_invalid_paths(self) -> None:
        result = main([str(self.source), str(self.output)])

        self.assertEqual(result, 1)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()

import json
from pathlib import Path
import tempfile
import unittest

from csv_to_json import CsvToJsonError, convert_csv_to_json


class ConvertCsvToJsonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.directory = Path(self.temp_dir.name)
        self.source = self.directory / "input.csv"
        self.destination = self.directory / "output.json"

    def convert(self, content: str) -> list[dict[str, str]]:
        self.source.write_text(content, encoding="utf-8", newline="")
        convert_csv_to_json(self.source, self.destination)
        return json.loads(self.destination.read_text(encoding="utf-8"))

    def test_converts_quoted_cells_and_embedded_newlines(self) -> None:
        result = self.convert(
            'name,note\n"Ada, Lovelace","first line\nsecond line"\n'
        )
        self.assertEqual(
            [{"name": "Ada, Lovelace", "note": "first line\nsecond line"}], result
        )

    def test_skips_empty_rows_but_keeps_empty_fields(self) -> None:
        result = self.convert("name,city\n\nAda,\n,\n")
        self.assertEqual(
            [{"name": "Ada", "city": ""}, {"name": "", "city": ""}], result
        )

    def test_header_only_file_becomes_empty_array(self) -> None:
        self.assertEqual([], self.convert("name,city\n"))

    def test_rejects_duplicate_headers_without_replacing_existing_output(self) -> None:
        self.destination.write_text("previous output", encoding="utf-8")
        self.source.write_text("name,name\nAda,Lovelace\n", encoding="utf-8")

        with self.assertRaisesRegex(CsvToJsonError, "duplicate header"):
            convert_csv_to_json(self.source, self.destination)

        self.assertEqual("previous output", self.destination.read_text(encoding="utf-8"))
        self.assertEqual(
            ["input.csv", "output.json"],
            sorted(path.name for path in self.directory.iterdir()),
        )

    def test_rejects_missing_header_names(self) -> None:
        for content in ("", "name,\nAda,Lovelace\n", ",\nAda,Lovelace\n"):
            with self.subTest(content=content):
                self.source.write_text(content, encoding="utf-8")
                with self.assertRaisesRegex(CsvToJsonError, "header"):
                    convert_csv_to_json(self.source, self.destination)

    def test_rejects_malformed_csv(self) -> None:
        self.destination.write_text("previous output", encoding="utf-8")
        self.source.write_text('name,note\nAda,"unfinished\n', encoding="utf-8")
        with self.assertRaises(CsvToJsonError):
            convert_csv_to_json(self.source, self.destination)
        self.assertEqual("previous output", self.destination.read_text(encoding="utf-8"))

    def test_rejects_rows_with_missing_or_extra_fields(self) -> None:
        for content in ("name,city\nAda\n", "name,city\nAda,London,UK\n"):
            with self.subTest(content=content):
                self.source.write_text(content, encoding="utf-8")
                with self.assertRaisesRegex(CsvToJsonError, "expected 2"):
                    convert_csv_to_json(self.source, self.destination)

    def test_refuses_to_use_input_as_output(self) -> None:
        self.source.write_text("name\nAda\n", encoding="utf-8")
        with self.assertRaisesRegex(CsvToJsonError, "different files"):
            convert_csv_to_json(self.source, self.source)
        self.assertEqual("name\nAda\n", self.source.read_text(encoding="utf-8"))

    def test_replaces_existing_output_after_success(self) -> None:
        self.destination.write_text("old content", encoding="utf-8")
        self.assertEqual([{"name": "Ada"}], self.convert("name\nAda\n"))


if __name__ == "__main__":
    unittest.main()

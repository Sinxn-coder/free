import subprocess
import tempfile
import unittest
from pathlib import Path

from json_formatter import format_json


class JsonFormatterTests(unittest.TestCase):
    def test_pretty_prints_json(self):
        self.assertEqual(format_json('{"name":"Ada"}'), '{\n  "name": "Ada"\n}\n')

    def test_minifies_json(self):
        self.assertEqual(format_json('{"name": "Ada"}', True), '{"name":"Ada"}')

    def test_sorts_nested_object_keys(self):
        self.assertEqual(
            format_json('{"z":1,"nested":{"y":2,"a":3},"a":0}', sort_keys=True),
            '{\n'
            '  "a": 0,\n'
            '  "nested": {\n'
            '    "a": 3,\n'
            '    "y": 2\n'
            '  },\n'
            '  "z": 1\n'
            '}\n',
        )

    def test_minify_output_is_unchanged_without_sorting(self):
        self.assertEqual(format_json('{"z": 1, "a": 2}', True), '{"z":1,"a":2}')

    def test_sorts_keys_when_minifying(self):
        self.assertEqual(
            format_json('{"z":1,"nested":{"y":2,"a":3},"a":0}', True, True),
            '{"a":0,"nested":{"a":3,"y":2},"z":1}',
        )


class CheckModeTests(unittest.TestCase):
    def test_check_mode_succeeds_for_properly_formatted_json(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write('{\n  "name": "Ada"\n}\n')
            temp_file = f.name

        try:
            result = subprocess.run(
                ["python", "json_formatter.py", temp_file, "--check"],
                cwd=Path(__file__).parent,
            )
            self.assertEqual(result.returncode, 0)
        finally:
            Path(temp_file).unlink()

    def test_check_mode_fails_for_unformatted_json(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write('{"name":"Ada"}')
            temp_file = f.name

        try:
            result = subprocess.run(
                ["python", "json_formatter.py", temp_file, "--check"],
                cwd=Path(__file__).parent,
            )
            self.assertEqual(result.returncode, 1)
        finally:
            Path(temp_file).unlink()

    def test_check_mode_does_not_modify_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            original_content = '{"name":"Ada"}'
            f.write(original_content)
            temp_file = f.name

        try:
            subprocess.run(
                ["python", "json_formatter.py", temp_file, "--check"],
                cwd=Path(__file__).parent,
            )
            self.assertEqual(Path(temp_file).read_text(), original_content)
        finally:
            Path(temp_file).unlink()

    def test_check_mode_with_minify_succeeds_for_minified_json(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write('{"name":"Ada"}')
            temp_file = f.name

        try:
            result = subprocess.run(
                ["python", "json_formatter.py", temp_file, "--check", "--minify"],
                cwd=Path(__file__).parent,
            )
            self.assertEqual(result.returncode, 0)
        finally:
            Path(temp_file).unlink()

    def test_check_mode_with_sort_keys_succeeds_for_sorted_json(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write(
                '{\n'
                '  "a": 0,\n'
                '  "nested": {\n'
                '    "a": 3,\n'
                '    "y": 2\n'
                '  },\n'
                '  "z": 1\n'
                '}\n'
            )
            temp_file = f.name

        try:
            result = subprocess.run(
                ["python", "json_formatter.py", temp_file, "--check", "--sort-keys"],
                cwd=Path(__file__).parent,
            )
            self.assertEqual(result.returncode, 0)
        finally:
            Path(temp_file).unlink()

    def test_check_mode_with_minify_and_sort_keys(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write('{"a":0,"nested":{"a":3,"y":2},"z":1}')
            temp_file = f.name

        try:
            result = subprocess.run(
                [
                    "python",
                    "json_formatter.py",
                    temp_file,
                    "--check",
                    "--minify",
                    "--sort-keys",
                ],
                cwd=Path(__file__).parent,
            )
            self.assertEqual(result.returncode, 0)
        finally:
            Path(temp_file).unlink()


if __name__ == "__main__":
    unittest.main()

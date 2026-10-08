import unittest

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


if __name__ == "__main__":
    unittest.main()

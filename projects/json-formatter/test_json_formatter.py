import unittest

from json_formatter import format_json


class JsonFormatterTests(unittest.TestCase):
    def test_pretty_prints_json(self):
        self.assertEqual(format_json('{"name":"Ada"}'), '{\n  "name": "Ada"\n}\n')

    def test_minifies_json(self):
        self.assertEqual(format_json('{"name": "Ada"}', True), '{"name":"Ada"}')


if __name__ == "__main__":
    unittest.main()

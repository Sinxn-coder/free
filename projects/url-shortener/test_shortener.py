import hashlib
import unittest
from unittest.mock import patch

from shortener import shorten


class ShortenerTests(unittest.TestCase):
    def test_uses_first_eight_digest_characters(self):
        mappings = {}
        url = "https://example.com"
        code = shorten(url, mappings)
        self.assertEqual(code, hashlib.sha256(url.encode()).hexdigest()[:8])
        self.assertEqual(mappings[code], url)
        self.assertEqual(len(code), 8)

    def test_repeated_url_keeps_the_same_code(self):
        mappings = {}
        url = "https://example.com"
        first_code = shorten(url, mappings)
        second_code = shorten(url, mappings)
        self.assertEqual(second_code, first_code)
        self.assertEqual(mappings, {first_code: url})

    def test_collision_extends_code_without_overwriting_existing_url(self):
        class FakeDigest:
            def __init__(self, digest):
                self.digest = digest

            def hexdigest(self):
                return self.digest

        digests = {
            "https://first.example": "12345678a0" + "0" * 54,
            "https://second.example": "12345678a1" + "0" * 54,
            "https://third.example": "12345678a2" + "0" * 54,
        }
        mappings = {"12345678": "https://existing.example"}

        def fake_sha256(value):
            return FakeDigest(digests[value.decode()])

        with patch("shortener.hashlib.sha256", side_effect=fake_sha256):
            first_code = shorten("https://first.example", mappings)
            second_code = shorten("https://second.example", mappings)
            third_code = shorten("https://third.example", mappings)

        self.assertEqual(first_code, "12345678a")
        self.assertEqual(second_code, "12345678a1")
        self.assertEqual(third_code, "12345678a2")
        self.assertEqual(mappings["12345678"], "https://existing.example")
        self.assertEqual(mappings[first_code], "https://first.example")
        self.assertEqual(mappings[second_code], "https://second.example")
        self.assertEqual(mappings[third_code], "https://third.example")

    def test_raises_when_full_digest_is_already_used(self):
        class FakeDigest:
            def hexdigest(self):
                return "a" * 64

        mappings = {
            "a" * length: "https://different.example"
            for length in range(8, 65)
        }
        with patch("shortener.hashlib.sha256", return_value=FakeDigest()):
            with self.assertRaisesRegex(ValueError, "Unable to create a unique code"):
                shorten("https://example.com", mappings)


if __name__ == "__main__":
    unittest.main()

import string
import unittest

from password_generator import generate_password


class PasswordGeneratorTests(unittest.TestCase):
    def test_includes_every_enabled_category(self):
        password = generate_password(20, use_symbols=False)
        self.assertEqual(len(password), 20)
        self.assertTrue(any(character in string.ascii_lowercase for character in password))
        self.assertTrue(any(character in string.ascii_uppercase for character in password))
        self.assertTrue(any(character in string.digits for character in password))

        password_with_symbols = generate_password(20)
        self.assertTrue(any(character in string.ascii_lowercase for character in password_with_symbols))
        self.assertTrue(any(character in string.ascii_uppercase for character in password_with_symbols))
        self.assertTrue(any(character in string.digits for character in password_with_symbols))
        self.assertTrue(any(character in string.punctuation for character in password_with_symbols))

    def test_no_symbols_excludes_punctuation(self):
        password = generate_password(20, use_symbols=False)
        self.assertTrue(password.isalnum())

    def test_accepts_minimum_length(self):
        self.assertEqual(len(generate_password(4)), 4)
        self.assertEqual(len(generate_password(4, use_symbols=False)), 4)

    def test_preserves_requested_length(self):
        self.assertEqual(len(generate_password(64)), 64)
        self.assertEqual(len(generate_password(64, use_symbols=False)), 64)

    def test_rejects_short_passwords(self):
        with self.assertRaises(ValueError):
            generate_password(3)


if __name__ == "__main__":
    unittest.main()

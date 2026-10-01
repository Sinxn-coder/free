import unittest

from password_generator import generate_password


class PasswordGeneratorTests(unittest.TestCase):
    def test_length_and_symbols_option(self):
        password = generate_password(20, use_symbols=False)
        self.assertEqual(len(password), 20)
        self.assertTrue(password.isalnum())

    def test_rejects_short_passwords(self):
        with self.assertRaises(ValueError):
            generate_password(3)


if __name__ == "__main__":
    unittest.main()

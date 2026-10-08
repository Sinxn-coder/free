import unittest

from calculator import ExpressionError, evaluate


class EvaluateTests(unittest.TestCase):
    def test_operator_precedence_and_parentheses(self):
        self.assertEqual(evaluate("2 + 3 * 4"), 14)
        self.assertEqual(evaluate("(2 + 3) * 4"), 20)

    def test_unary_operators(self):
        self.assertEqual(evaluate("-3 + +2"), -1)
        self.assertEqual(evaluate("-(2 - 5)"), 3)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            evaluate("4 / (2 - 2)")

    def test_rejects_names(self):
        with self.assertRaises(ExpressionError):
            evaluate("answer + 1")

    def test_rejects_function_calls(self):
        with self.assertRaises(ExpressionError):
            evaluate("abs(-2)")


if __name__ == "__main__":
    unittest.main()

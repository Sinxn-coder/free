"""A small, safe arithmetic expression calculator."""

import argparse
import ast
import math
import operator
import sys


class ExpressionError(ValueError):
    """Raised when an expression contains unsupported syntax."""


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def evaluate(expression: str) -> int | float:
    """Evaluate an expression containing numbers and +, -, *, /, and parentheses."""
    try:
        tree = ast.parse(expression, mode="eval")
    except (SyntaxError, RecursionError) as error:
        raise ExpressionError("Invalid arithmetic expression") from error

    return _evaluate_node(tree.body)


def _evaluate_node(node: ast.expr) -> int | float:
    if isinstance(node, ast.Constant):
        value = node.value
        if type(value) not in (int, float):
            raise ExpressionError("Only integer and decimal number literals are allowed")
        if isinstance(value, float) and not math.isfinite(value):
            raise ExpressionError("Number literals must be finite")
        return value

    if isinstance(node, ast.BinOp):
        operation = _BINARY_OPERATORS.get(type(node.op))
        if operation is None:
            raise ExpressionError("Only +, -, *, and / operators are allowed")
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)
        return operation(left, right)

    if isinstance(node, ast.UnaryOp):
        operation = _UNARY_OPERATORS.get(type(node.op))
        if operation is None:
            raise ExpressionError("Only unary + and - operators are allowed")
        return operation(_evaluate_node(node.operand))

    raise ExpressionError("Only numbers, parentheses, and arithmetic operators are allowed")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate an arithmetic expression using numbers and +, -, *, /."
    )
    parser.add_argument("expression", help='expression to evaluate, e.g. "2 * (3 + 4)"')
    arguments = parser.parse_args(argv)

    try:
        result = evaluate(arguments.expression)
    except (ExpressionError, ZeroDivisionError, OverflowError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

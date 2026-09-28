# Terminal Calculator

A command-line calculator for arithmetic expressions using integer and decimal
number literals, parentheses, and the `+`, `-`, `*`, and `/` operators. Unary
`+` and `-` are supported as well.

Expressions are parsed with Python's `ast` module and evaluated by recursively
handling only the permitted syntax. Names, function calls, and all other
Python syntax are rejected; the calculator never uses `eval`.

## Requirements

Python 3.10 or newer. The project uses only the Python standard library.

## Usage

Run the script with the expression in quotes:

```console
python calculator.py "2 + 3 * (4 - 1)"
11
```

Use `python calculator.py --help` to see the command-line help. Invalid
expressions and division by zero produce an error message and a non-zero exit
status.

## Tests

Run the tests from this directory:

```console
python -m unittest -v
```

# Password Generator

Generate a random password with Python's `secrets` module:

```text
python password_generator.py --length 20
python password_generator.py --length 20 --no-symbols
```

Generated passwords contain at least one lowercase letter, uppercase letter,
and digit. Symbols are also included by default; `--no-symbols` excludes them.
The minimum password length is 4.

Run tests with `python -m unittest`.

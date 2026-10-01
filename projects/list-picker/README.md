# List Picker

A standard-library Python CLI that selects one random item from a text file,
with one item per line.

## Usage

```text
python list_picker.py items.txt
python list_picker.py items.txt --seed demo
python list_picker.py items.txt --keep-blank-lines
```

Blank lines (including whitespace-only lines) are ignored by default. Use
`--keep-blank-lines` to make them selectable empty-string items. `--seed` accepts
a text seed; using the same seed with the same input gives the same choice.

The selection uses Python's `random.Random.choice`, which gives every entry an
equal chance. If no selectable entries remain, the CLI prints a clear error to
standard error and exits with status 1. Files are read as UTF-8.

## Tests

Python 3.8 or newer is required. Run the standard-library tests from this
directory:

```text
python -m unittest discover -s tests -v
```

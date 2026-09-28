# CSV Cleaner

A small Python 3.10+ command-line tool that trims leading and trailing whitespace
from every CSV cell. It uses only the Python standard library and handles CSV
quoting, commas, and embedded newlines.

## Usage

```text
python csv_cleaner.py INPUT.csv OUTPUT.csv [--normalize-headers] [--overwrite]
```

For example:

```text
python csv_cleaner.py messy.csv clean.csv --normalize-headers
```

Headers are trimmed like other cells. With `--normalize-headers`, header names
are also case-folded and runs of punctuation or whitespace become underscores
(for example, `First Name` becomes `first_name`). Data rows are not renamed.

The input and output must be different paths. By default, the tool also refuses
to replace an existing output file; pass `--overwrite` to explicitly allow
that. Input is read as UTF-8 (an optional UTF-8 BOM is accepted), and output is
written as UTF-8.

## Tests

From this directory, run:

```text
python -m unittest discover -s tests -v
```

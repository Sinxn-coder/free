# Text Redactor

A standard-library Python CLI that replaces common email addresses and
phone-number-like strings in a UTF-8 text file with `[REDACTED]`.

## Usage

```text
python redactor.py INPUT
python redactor.py INPUT --output REDACTED.txt
```

With no `--output` option, the redacted text is written to stdout. An output
file must be new; the CLI refuses to overwrite any existing file, including
the input. Input files are never modified.

## Scope and limitations

The email and phone patterns are heuristics, not complete validators. They can
miss personal information or redact unrelated text. This tool does not
guarantee anonymization, and its output should not be treated as anonymous.
Review results before sharing them.

## Tests

Run the tests from this directory:

```text
python -m unittest discover -s tests -v
```

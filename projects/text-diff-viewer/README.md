# Text Diff Viewer

A read-only, standard-library Python CLI that prints a unified diff between two
UTF-8 text files.

## Usage

```console
python text_diff_viewer.py [--context LINES] OLD_FILE NEW_FILE
```

`-U` is an alias for `--context`; the default is three context lines. Line
endings are normalized when reading, so LF and CRLF files with the same text
compare equally. The command exits with status `0` when files are equal, `1`
when they differ, and `2` for invalid arguments or file errors.

Missing files and unreadable or invalid UTF-8 files produce a clear error on
standard error. An optional UTF-8 byte-order mark is accepted. Diff output is
written as UTF-8. The command never modifies either input.

## Tests

Run the test suite with:

```console
python -m unittest -v
```

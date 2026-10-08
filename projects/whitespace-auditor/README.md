# Whitespace Auditor

A Python 3 command-line tool that checks files for trailing whitespace and a
missing final newline. It uses only the Python standard library.

## Usage

```text
python whitespace_auditor.py [--fix] PATH [PATH ...]
```

Pass one or more files or directories. Directories are searched recursively.
Check mode is the default and prints each finding as `path:line: message`. It
never writes to the inspected files and exits with status `1` if any findings
exist, `0` when all files are clean, or `2` when a path cannot be read or
decoded.

Use `--fix` to explicitly remove trailing whitespace and add a final newline.
Changed files are replaced atomically from a temporary file in the same
directory; their permission bits are retained. Existing CRLF, LF, and CR
newline sequences are preserved per line. If a final newline must be added,
the first newline style in the file is used (LF if the file has no newline).
UTF-8, UTF-8 with BOM, and BOM-marked UTF-16/UTF-32 are supported. Other input
must be valid UTF-8; undecodable files are reported as errors and left
untouched. Exit status is `0` after a successful fix, or `2` if an error
occurs.

## Tests

Run the test suite from this directory:

```text
python -m unittest -v
```

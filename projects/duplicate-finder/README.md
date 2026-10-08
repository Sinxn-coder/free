# Duplicate File Finder

Find files with identical content anywhere beneath a directory. The scanner
first groups files by size and hashes only files in groups with matching sizes,
which avoids unnecessary reads. Files are opened read-only; this tool does not
modify or delete anything. Directory symlinks are not followed.

Run it with Python 3.10 or newer:

```text
python duplicate_finder.py path\to\directory
```

Each duplicate group is printed with its size and file paths. If the scan
encounters unreadable files or directories, their errors are printed to
standard error and the command exits with status `1` rather than reporting a
successful complete scan. An invalid scan path exits with status `2`.

Run the tests from this directory:

```text
python -m unittest -v
```

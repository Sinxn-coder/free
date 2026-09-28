# Empty Directory Finder

A read-only Python 3.10+ command-line tool that lists empty directories below a
specified root. It uses only the Python standard library and never follows
symbolic-link directories.

## Usage

```console
python empty_dir_finder.py PATH [--max-depth N]
```

Paths are printed relative to `PATH`, one per line, in deterministic
lexicographic order. The root itself is not included. `--max-depth` limits the
number of directory levels below the root to inspect: level 1 means immediate
child directories, level 2 includes their child directories, and so on. The
default is unlimited; `--max-depth 0` does not inspect any descendants.

The program only reads directory entries. It does not create, modify, or delete
files or directories. Errors are reported on standard error with a nonzero exit
status.

## Tests

Run the test suite from this directory:

```console
python -m unittest discover -s tests -v
```

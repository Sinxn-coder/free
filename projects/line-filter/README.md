# Line Filter

Print lines from a UTF-8 file that match a regular expression:

```text
python line_filter.py "error|warning" application.log
python line_filter.py "^#" configuration.txt --invert
python line_filter.py "error" application.log --ignore-case
```

The pattern is searched anywhere in each line. `--invert` selects lines that
do not match. Matching is case-sensitive by default; use `-i` or
`--ignore-case` to match without regard to case. Selected lines are written
without changing their original line endings, including a final line without a
newline. Invalid regular expressions, unreadable files, and non-UTF-8 input are
reported as command-line errors.

Run the tests with:

```text
python -m unittest -v
```

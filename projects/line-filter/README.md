# Line Filter

Print lines from a UTF-8 file that match a regular expression:

```text
python line_filter.py "error|warning" application.log
python line_filter.py "^#" configuration.txt --invert
```

The pattern is searched anywhere in each line. `--invert` selects lines that
do not match. Selected lines are written without changing their original line
endings, including a final line without a newline. Invalid regular expressions,
unreadable files, and non-UTF-8 input are reported as command-line errors.

Run the tests with:

```text
python -m unittest -v
```

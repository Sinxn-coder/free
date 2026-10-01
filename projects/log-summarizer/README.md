# Log Summarizer

A Python 3 standard-library CLI that streams a log file, counts lines containing
`ERROR`, `WARNING`, `INFO`, and `DEBUG`, and prints matching error lines.
Level matching is case-insensitive. Each level is counted at most once per line,
even if it appears more than once on that line.

## Usage

```text
python log_summarizer.py path/to/application.log
python log_summarizer.py path/to/application.log --no-error-lines
python log_summarizer.py path/to/application.log --encoding cp1252
python log_summarizer.py --help
```

By default, matching error lines are printed first, followed by counts for all
four levels (including levels with zero matches). Use `--no-error-lines` to
print only counts. The input is read as UTF-8 by default; specify `--encoding`
for logs using another text encoding.

## Tests

Run the standard-library test suite from this directory:

```text
python -m unittest -v
```

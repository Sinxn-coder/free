# CSV Summary

Summarize the data rows, column names, and non-empty value count for each
column in a UTF-8 CSV file. The utility uses only the Python standard library.

```text
python csv_summary.py data.csv
```

For example:

```text
Data rows: 2
Columns: name, city
Non-empty values:
  name: 2
  city: 1
```

Blank lines are ignored, and whitespace-only values count as empty. Files with
malformed CSV quoting, rows whose field count differs from the header, or no
header produce a command-line error.

Run the tests from this directory:

```text
python -m unittest -v
```

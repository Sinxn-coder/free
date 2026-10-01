# CSV to JSON

A Python standard-library command-line tool that converts a CSV file with a
header row into a JSON array of objects.

## Usage

```console
python csv_to_json.py input.csv output.json
```

The input is read as UTF-8 (an optional UTF-8 BOM is accepted). The output is
UTF-8 JSON. Existing output files are replaced only after the entire CSV has
been read and validated. The output must be a different file from the input,
and its parent directory must already exist.

## CSV behavior

- The first record supplies object keys. Empty or whitespace-only header names
  and duplicate header names are rejected; duplicate matching is exact and
  case-sensitive.
- Every nonblank record must have exactly as many fields as the header. A
  short record is not silently padded, and extra fields are not discarded.
- Entirely empty rows are skipped. Rows containing delimiters, even if every
  cell is empty, are retained as records.
- CSV syntax errors fail conversion. Errors leave the requested output
  unchanged and remove the temporary output file.
- Rows are converted one at a time, so the complete input and JSON result are
  not held in memory.

## Tests

From this directory, run:

```console
python -m unittest discover -s tests -v
```

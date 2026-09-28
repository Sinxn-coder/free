# JSONL Inspector

A small Python 3.10+ command-line tool for validating and inspecting JSON Lines
(`.jsonl` / `.ndjson`) files. It uses only the Python standard library.

## Usage

```console
python jsonl_inspector.py records.jsonl
```

Blank lines are ignored. The command reports the number of valid JSON records
and the number of malformed non-blank lines. Each malformed line is reported
to standard error with its physical line number. The exit status is `0` when
all non-blank lines are valid, `1` when malformed lines are found, and `2` for
an input/output error or invalid command-line usage.

To write valid records as indented JSON, one record after another, to a
separate file:

```console
python jsonl_inspector.py records.jsonl --output pretty.json
```

The input is streamed one line at a time and is never used as the output
destination. Malformed lines are skipped in the output file.

## Tests

From this directory, run:

```console
python -m unittest -v
```

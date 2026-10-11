# JSON Formatter

Pretty-print or minify a JSON file:

```text
python json_formatter.py data.json
python json_formatter.py data.json --minify
python json_formatter.py data.json --sort-keys
python json_formatter.py data.json --minify --sort-keys
```

Use `--sort-keys` to sort object keys alphabetically, including nested objects.
Without this option, keys retain their original order. It can be combined with
`--minify`.

## Check Mode

Use `--check` to verify that a JSON file is properly formatted without modifying it:

```text
python json_formatter.py data.json --check
python json_formatter.py data.json --check --minify
python json_formatter.py data.json --check --sort-keys
```

The `--check` mode exits with code 0 if the file is properly formatted, and exits
with code 1 if it needs formatting. The file is never modified.

Invalid JSON produces Python's normal parse error.


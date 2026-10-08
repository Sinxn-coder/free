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

Invalid JSON produces Python's normal parse error.

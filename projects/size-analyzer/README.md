# File Size Analyzer

Find the largest files beneath a directory:

```text
python analyze.py . --top 10
```

The output includes each file's size in bytes and its path.

Use `--min-size` to include only files at least the specified number of bytes:

```text
python analyze.py . --min-size 1048576
```

The minimum size defaults to 0 bytes, so all files are included unless a
threshold is provided. Negative values for `--min-size` and `--top` are rejected.

Use `--human-readable` to display sizes with binary units (1 KiB = 1,024 bytes):

```text
python analyze.py . --top 10 --human-readable
```

Byte output remains the default. Human-readable output uses units such as KiB, MiB,
and GiB.

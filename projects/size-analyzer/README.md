# File Size Analyzer

Find the largest files beneath a directory:

```text
python analyze.py . --top 10
```

The output includes each file's size in bytes and its path.

Use `--human-readable` to display sizes with binary units (1 KiB = 1,024 bytes):

```text
python analyze.py . --top 10 --human-readable
```

Byte output remains the default. Human-readable output uses units such as KiB, MiB,
and GiB.

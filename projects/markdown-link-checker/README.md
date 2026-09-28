# Markdown Link Checker

A dependency-free Python CLI that checks inline links and reference definitions
in Markdown files.
It reports missing targets with the source file and line number and never
changes any files. External URLs, fragment-only links, and `mailto:` links are
ignored. URL-encoded paths are decoded before checking, and links to existing
directories are valid.

## Usage

```text
python markdown_link_checker.py [PATH]
```

`PATH` may be a Markdown file or a directory to scan recursively. If omitted,
the current directory is scanned. The command exits with status `0` when all
local targets exist, `1` when broken links are found, and `2` for an input or
file-reading error.

## Tests

```text
python -m unittest discover -s tests -v
```

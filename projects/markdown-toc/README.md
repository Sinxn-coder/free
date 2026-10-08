# Markdown TOC

Generate a table of contents from Markdown ATX headings (`#` through `######`):

```console
python markdown_toc.py README.md
```

The table of contents is printed to standard output. Use `-o` to write it to a
file instead:

```console
python markdown_toc.py README.md --output toc.md
```

Headings inside backtick or tilde fenced code blocks are ignored. Anchor slugs
use lowercase GitHub-style text, remove punctuation, preserve Unicode letters,
numbers, underscores, and hyphens, and convert whitespace to hyphens. Repeated
slugs receive numeric suffixes (`-1`, `-2`, and so on). Entries are indented by
heading level.

Run the focused tests from this directory:

```console
python -m unittest -v
```

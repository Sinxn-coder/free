# Markdown to HTML

Convert headings, paragraphs, and simple ordered or unordered lists from Markdown:

```text
python convert.py README.md -o page.html
```

This intentionally supports a small, dependency-free Markdown subset.

Supported syntax includes `#` and `##` headings, paragraphs, bold text marked
with `**`, unordered list items starting with `- ` or `* `, and ordered list
items starting with a number and `. `. Consecutive list items are grouped until
a blank line or a different block type.

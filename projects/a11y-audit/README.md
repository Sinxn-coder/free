# A11y Audit

A small, offline, dependency-free command-line checker for common static HTML accessibility issues. It is intended as an early feedback tool for developers, not as an accessibility certification.

## Requirements

- Python 3.10 or newer
- No third-party packages

## Usage

Run the script directly with one or more HTML files or directories:

```sh
python a11y_audit.py index.html
python a11y_audit.py public/ templates/page.html
python a11y_audit.py public/ --format json
```

Directory scans recurse through `.html` and `.htm` files in deterministic name order and do not recurse into symlinked directories. Explicitly passing a symlinked directory is reported as an input error. Files are read as UTF-8 (with an optional UTF-8 BOM); unreadable or invalidly encoded inputs are reported rather than silently ignored.

Text output shows the file, source line, severity, stable rule code, and an actionable summary. JSON output is intended for CI integration and contains `files_scanned`, a severity summary, `issues`, and `input_errors`. Exit statuses are:

- `0`: no findings and no input errors
- `1`: one or more accessibility findings
- `2`: one or more unreadable, missing, or otherwise invalid inputs

Use `python a11y_audit.py --help` for command-line options and examples.

## Checks

| Code | Severity | Check |
| --- | --- | --- |
| `A11Y001` | Error | Document is missing a `<title>` |
| `A11Y002` | Error | Document title is empty |
| `A11Y003` | Error | `<html>` is missing a non-empty `lang` attribute |
| `A11Y004` | Error | An `<img>` is missing `alt` (an explicit empty `alt=""` is accepted) |
| `A11Y005` | Error | An ID value is duplicated |
| `A11Y006` | Error | A form control has no detectable accessible name |
| `A11Y007` | Warning | Heading levels skip one or more levels |

Control names are detected from associated or wrapping labels, non-empty `aria-label` and `aria-labelledby` references, button text, and applicable input values/alt text. Hidden inputs are ignored.

## Limitations

Automated static checks cover only a small set of detectable markup patterns. They do **not** certify WCAG conformance or replace manual review, keyboard testing, or testing with assistive technologies. In particular, the checker cannot judge whether alternative text is meaningful, whether contrast is sufficient, whether controls work well in context, or what names result from browser accessibility-tree computation. Dynamic content, CSS-generated content, JavaScript behavior, and many other accessibility requirements are outside its scope. A clean report is not evidence that a page is accessible.

## Tests

From this directory, run:

```sh
python -m unittest -v
```

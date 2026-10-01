# Env Key Auditor

A standard-library Python CLI that compares variable names in `.env.example`
and `.env` without displaying assignment values. It reports keys missing from
`.env` and keys present only in `.env`; it never modifies either input.

## Usage

Run from the directory containing the two files:

```console
python env_key_auditor.py
```

The defaults are `.env.example` and `.env`. To use other files, pass the
template first and the local env file second:

```console
python env_key_auditor.py path/to/template.env path/to/local.env
```

Blank lines and lines whose first non-whitespace character is `#` are ignored.
Assignments use `KEY=value` syntax, with optional whitespace around `=` and
an optional `export` prefix. Values are not interpreted, so quotes, spaces,
comments within values, and additional `=` characters do not affect the key
comparison. Duplicate names count once. Non-comment lines that are not
assignments produce a line-numbered error without echoing their contents.

The command returns `0` after a comparison, including when keys differ, and
`1` if an input cannot be read or contains an invalid assignment.

## Tests

```console
python -m unittest -v
```

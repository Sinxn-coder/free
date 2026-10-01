# Safe Rename Planner

A standard-library-only Python CLI that previews literal bulk filename
replacements in a directory. Items and output are sorted for a deterministic
plan. The default is a dry run; no rename occurs unless `--apply` is supplied.

## Usage

```text
python safe_rename_planner.py DIRECTORY OLD NEW [--recursive] [--apply]
```

For example, preview replacing `draft` with `final`:

```text
python safe_rename_planner.py ./documents draft final
```

Apply that plan:

```text
python safe_rename_planner.py ./documents draft final --apply
```

Only files directly in the directory are scanned by default. `--recursive`
also scans files in subdirectories and does not follow directory symlinks.
Replacement text cannot contain path separators, and any destination that
already exists (or conflicts with another planned destination) is reported as
a collision. A plan with collisions is never applied.

## Tests

Run the unit tests from this directory:

```text
python -m unittest -v
```

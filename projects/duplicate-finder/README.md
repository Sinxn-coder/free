# Duplicate File Finder

A dependency-free Python command-line tool that finds exact duplicate regular
files beneath one or more directory roots. It only reads files; it never
deletes, moves, or modifies scanned content.

## Requirements

- Python 3.9 or newer
- No third-party packages

## Usage

Run from this directory:

```text
python duplicate_finder.py DIRECTORY [DIRECTORY ...]
python duplicate_finder.py --json DIRECTORY [DIRECTORY ...]
python duplicate_finder.py --chunk-size 262144 DIRECTORY
```

Examples:

```text
python duplicate_finder.py ~/Pictures /mnt/backup/Pictures
python duplicate_finder.py --json ./documents ./old-documents
python duplicate_finder.py --chunk-size 524288 ./archive
```

Use `python duplicate_finder.py --help` for the full command help. Directory
roots must exist and must not themselves be symbolic links.

## Algorithm and safety

The scan first enumerates regular files and groups them by file size. Files in
size groups of two or more are hashed with SHA-256 using bounded reads (1 MiB
by default); `--chunk-size` changes the read buffer size. Only files with both
the same size and the same SHA-256 digest are reported together.

Directory entries and output groups are sorted for repeatable results.
Overlapping roots are deduplicated by normalized absolute path, so a path
encountered through multiple roots is only scanned once. Symbolic-link files
are skipped, symbolic-link directories are not traversed, and symbolic-link
roots are rejected with a scan error. Other non-regular filesystem entries
are ignored.

Each distinct hard-link path is reported as a separate path. Since hard links
have the same content, they can appear in the same duplicate group; the
reported savings count treats one of those paths as retained, though removing
a hard link would not necessarily reclaim the file's storage.

Files are opened read-only. The tool checks file size before hashing and
compares size and modification time before and after the read, reporting a
scan error when a change is detected. This is not a filesystem snapshot:
concurrent changes can still affect what is observed. SHA-256 collisions are
theoretically possible, so digest equality is a strong practical match rather
than a mathematical proof of byte equality.

## Output contract

Text output lists each duplicate group, its paths, and potential bytes
reclaimable. Errors are written to stderr.

With `--json`, stdout contains one JSON object with these top-level keys:

- `duplicates`: ordered group objects with `size`, `sha256`, ordered `files`,
  and `bytes_reclaimable`
- `errors`: ordered objects with `path` and `message`
- `summary`: `files_scanned`, `duplicate_group_count`,
  `duplicate_file_count` (the extra paths beyond one retained path per group),
  and total `bytes_reclaimable`

The JSON is indented and keys are sorted. Scan errors are included in the JSON
and also printed to stderr.

## Exit codes

- `0`: scan completed without errors and no duplicates were found
- `1`: scan completed without errors and duplicates were found
- `2`: an input or scan error occurred (takes precedence if duplicates were
  also found)

Invalid command-line syntax is handled by `argparse` and also exits with code
`2`.

## Tests

From this directory, run:

```text
python -m unittest discover -s tests -v
```

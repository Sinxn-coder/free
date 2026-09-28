# Backup Manifest Verifier

Backup Manifest Verifier is a standard-library-only Python command-line tool for
creating a deterministic SHA-256 manifest of a directory and checking an
independent copy against it. It reports missing, changed, and unexpected
regular files separately.

## Requirements

- Python 3.10 or newer
- No third-party packages

Run the tool directly from this directory:

```text
python backup_verifier.py create PATH\TO\SOURCE PATH\TO\backup-manifest.json
python backup_verifier.py verify PATH\TO\RESTORED-COPY PATH\TO\backup-manifest.json
```

The manifest path must be outside the tree being scanned. On macOS or Linux,
use normal `/` path separators. The manifest stores relative POSIX paths
regardless of the host platform.

## Restore verification workflow

1. Create the manifest for the source directory and store it separately from
   the files being copied:

   ```text
   python backup_verifier.py create D:\work\important D:\backup\important-manifest.json
   ```

2. Copy the directory and the manifest to independent storage. Keep the
   manifest separate from the backup tree.
3. Restore or copy the backup to a directory, then compare that copy to the
   saved manifest:

   ```text
   python backup_verifier.py verify E:\restored\important D:\backup\important-manifest.json
   ```

Exit status `0` means the tree matches; `1` means verification found
differences; `2` means an input, manifest, or filesystem scan error prevented
verification. The human report lists each difference by relative path.

Use `--json` before or after the command for a machine-readable report:

```text
python backup_verifier.py --json verify E:\restored\important D:\backup\important-manifest.json
python backup_verifier.py verify E:\restored\important D:\backup\important-manifest.json --json
```

For successful verification, JSON contains `ok: true` and empty `missing`,
`changed`, and `unexpected` arrays. Differences use the same three sorted
arrays. Input and scan errors use exit status `2` and include an `error` field
in JSON; without `--json`, errors are written to standard error.

## Manifest format

The UTF-8 JSON document has a version and a sorted file list:

```json
{
  "version": 1,
  "files": [
    {
      "path": "documents/notes.txt",
      "sha256": "..."
    }
  ]
}
```

Paths are relative, normalized POSIX paths. Entries are sorted by path and
serialized consistently, so repeated creation for unchanged files produces
identical bytes. Hashes are computed incrementally in 1 MiB chunks.

## Safety and limitations

- The tool only reads scanned files. Manifest creation scans fully before
  writing output; it writes a temporary file in the destination directory and
  atomically replaces the destination only after a successful scan and write.
- A manifest inside the scanned root is rejected, preventing the output or the
  manifest itself from entering the scan. The manifest's parent directory must
  already exist.
- Symbolic-link files and directories are not followed and are omitted from
  the manifest and verification. Links are not reported as unexpected files.
- Special files such as sockets, FIFOs, and device nodes are not included.
- The manifest is an integrity check, not an authenticity mechanism. Anyone
  who can replace both the data and its manifest can produce a matching pair;
  protect or sign the manifest separately when authenticity matters.
- The tool checks file identity and basic metadata while hashing, but cannot
  guarantee a consistent point-in-time snapshot if files are actively changing.
  For best results, verify quiescent data or a filesystem snapshot.
- Verification reports content differences for regular files; it does not
  preserve or compare ownership, permissions, timestamps, hard-link topology,
  or empty directories.

## Tests

Run the focused standard-library test suite from this directory:

```text
python -m unittest discover -s tests -v
```

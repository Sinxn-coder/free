# Extension Report

`extension_report.py` is a read-only Python 3 CLI that reports regular-file counts and total bytes grouped by `pathlib` suffix. It traverses directories in sorted depth-first order, skips symlinked files and directories, and reports files or directories it cannot read to standard error. A scan with any reported errors exits with status 1.

```text
python extension_report.py PATH [--max-files N] [--max-depth N]
```

Suffixes are reported as-is (for example, `.py`); files without a suffix, including dotfiles such as `.gitignore`, are grouped under `<none>`. `--max-files` limits the number of readable files included, and `--max-depth 0` includes only files directly inside the root directory. Both limits accept zero or greater. Hitting the file limit is explicitly reported because there may be additional files.

Run the tests from this directory:

```text
python -m unittest discover -s tests -v
```

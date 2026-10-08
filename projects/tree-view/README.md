# Directory Tree

Display a directory structure:

```text
python tree_view.py . --max-depth 2
```

Directories are sorted before files for easy scanning.

Pass `--no-hidden` to omit dot-prefixed files and directories at every depth:

```text
python tree_view.py . --max-depth 2 --no-hidden
```

# Gitignore Builder

A standard-library Python CLI that prints a `.gitignore` snippet for selected
templates. It supports Python, Node, Java, Windows, and macOS. If templates
contain the same entry, it appears only once.

## Usage

```console
python gitignore_builder.py python node
python gitignore_builder.py java windows macos --existing .gitignore
python gitignore_builder.py python --output .gitignore
```

Output goes to stdout by default. The tool writes a file only when `--output`
is supplied. With `--existing`, its lines are retained first, in their original
order, and duplicate lines are removed before selected template entries are
appended. Template entries follow the fixed order Python, Node, Java, Windows,
macOS, regardless of the order of the command-line arguments.

Run the tests with:

```console
python -m unittest discover -s tests -v
```

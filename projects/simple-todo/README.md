# Simple Todo

A small JSON-backed todo list:

```text
python todo.py add "Learn Python"
python todo.py list
python todo.py done 1
python todo.py remove 1
python todo.py clear
```

Use `remove <number>` to delete a todo by its 1-based number in the displayed list.
Use `clear` to delete all completed todos while keeping incomplete todos.

Data is saved in `todos.json` beside the script.

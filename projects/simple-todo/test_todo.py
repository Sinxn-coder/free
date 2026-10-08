import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import todo


class TodoTests(unittest.TestCase):
    def test_add_and_complete(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(todo, "DATA_FILE", Path(directory) / "todos.json"):
                items = []
                todo.add(items, "Learn Python")
                todo.complete(items, 1)
                self.assertTrue(todo.load()[0]["done"])

    def test_remove_deletes_todo_and_persists_change(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(todo, "DATA_FILE", Path(directory) / "todos.json"):
                items = [{"text": "First", "done": False}, {"text": "Second", "done": True}]
                todo.save(items)

                todo.remove(items, 1)

                self.assertEqual(items, [{"text": "Second", "done": True}])
                self.assertEqual(todo.load(), items)

    def test_remove_rejects_invalid_indices_like_complete(self):
        items = [{"text": "Learn Python", "done": False}]

        for index in (0, 2):
            with self.subTest(index=index):
                with self.assertRaisesRegex(ValueError, "todo number is out of range") as remove_error:
                    todo.remove(items, index)
                with self.assertRaisesRegex(ValueError, "todo number is out of range") as complete_error:
                    todo.complete(items, index)
                self.assertEqual(str(remove_error.exception), str(complete_error.exception))


if __name__ == "__main__":
    unittest.main()

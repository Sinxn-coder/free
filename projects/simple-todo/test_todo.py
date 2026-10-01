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


if __name__ == "__main__":
    unittest.main()

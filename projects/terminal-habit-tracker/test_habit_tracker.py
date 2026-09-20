import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import habit_tracker


class HabitTrackerCoreTests(unittest.TestCase):
    def test_add_and_complete_habit(self):
        with tempfile.TemporaryDirectory() as directory:
            data_file = Path(directory) / "habits.json"
            with patch.object(habit_tracker, "DATA_FILE", data_file):
                habits = habit_tracker.load_habits()
                habit_tracker.add_habit(habits, "Read")
                habit_tracker.complete_habit(habits, "Read")

                saved = json.loads(data_file.read_text(encoding="utf-8"))

        self.assertEqual(saved["Read"]["completed_dates"], [habit_tracker.date.today().isoformat()])

    def test_remove_habit_deletes_saved_habit(self):
        with tempfile.TemporaryDirectory() as directory:
            data_file = Path(directory) / "habits.json"
            with patch.object(habit_tracker, "DATA_FILE", data_file):
                habits = {"Read": {"completed_dates": ["2026-09-20"]}}
                habit_tracker.remove_habit(habits, "Read")
                saved = json.loads(data_file.read_text(encoding="utf-8"))

        self.assertEqual(saved, {})

    def test_history_reports_completed_dates(self):
        habits = {"Read": {"completed_dates": ["2026-09-19"]}}
        with patch("builtins.print") as print_mock:
            habit_tracker.show_history(habits, "Read")

        print_mock.assert_any_call("- 2026-09-19")


if __name__ == "__main__":
    unittest.main()

import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import habit_tracker


class HabitTrackerCoreTests(unittest.TestCase):
    def test_streak_counts_consecutive_days_starting_today(self):
        today = date(2026, 9, 22)
        completed_dates = [
            (today - timedelta(days=offset)).isoformat() for offset in range(3)
        ]
        habits = {"Read": {"completed_dates": completed_dates}}

        with patch.object(habit_tracker, "date") as date_mock:
            date_mock.today.return_value = today
            with patch("builtins.print") as print_mock:
                habit_tracker.show_streak(habits, "Read")

        print_mock.assert_called_once_with("Current streak for Read: 3 days")

    def test_streak_counts_consecutive_days_starting_yesterday(self):
        today = date(2026, 9, 22)
        completed_dates = [
            (today - timedelta(days=offset)).isoformat() for offset in range(1, 4)
        ]
        habits = {"Read": {"completed_dates": completed_dates}}

        with patch.object(habit_tracker, "date") as date_mock:
            date_mock.today.return_value = today
            with patch("builtins.print") as print_mock:
                habit_tracker.show_streak(habits, "Read")

        print_mock.assert_called_once_with("Current streak for Read: 3 days")

    def test_streak_stops_at_a_missing_day(self):
        today = date(2026, 9, 22)
        completed_dates = [
            today.isoformat(),
            (today - timedelta(days=2)).isoformat(),
        ]
        habits = {"Read": {"completed_dates": completed_dates}}

        with patch.object(habit_tracker, "date") as date_mock:
            date_mock.today.return_value = today
            with patch("builtins.print") as print_mock:
                habit_tracker.show_streak(habits, "Read")

        print_mock.assert_called_once_with("Current streak for Read: 1 day")

    def test_streak_is_zero_when_last_completion_is_older_than_yesterday(self):
        today = date(2026, 9, 22)
        habits = {
            "Read": {
                "completed_dates": [(today - timedelta(days=2)).isoformat()]
            }
        }

        with patch.object(habit_tracker, "date") as date_mock:
            date_mock.today.return_value = today
            with patch("builtins.print") as print_mock:
                habit_tracker.show_streak(habits, "Read")

        print_mock.assert_called_once_with("Current streak for Read: 0 days")

    def test_streak_reports_unknown_habit(self):
        with self.assertRaisesRegex(SystemExit, "Unknown habit: Read"):
            habit_tracker.show_streak({}, "Read")

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

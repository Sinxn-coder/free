# Terminal Habit Tracker

A tiny habit tracker built with Python's standard library.

For a full explanation and usage guide, see [ABOUT.md](ABOUT.md).

## Usage

```text
python habit_tracker.py add "Read for 20 minutes"
python habit_tracker.py add "Drink water"
python habit_tracker.py list
python habit_tracker.py done "Read for 20 minutes"
python habit_tracker.py list
python habit_tracker.py history "Read for 20 minutes"
python habit_tracker.py remove "Drink water"
```

Habits are saved in `.habit_data.json` beside the script. The file is ignored
by Git so your personal habits stay local.

Run the tests from this folder with:

```text
python -m unittest test_habit_tracker.py
```
# About the Terminal Habit Tracker

## What is it?

The Terminal Habit Tracker is a small Python program for recording daily
habits from a command prompt. It uses only Python's standard library, so no
extra packages are needed.

You can:

- Add habits such as reading, exercising, or drinking water.
- See which habits are complete today.
- Mark a habit complete for today.
- View all recorded completion dates for a habit.
- Remove habits that you no longer want to track.

## Requirements

- Python 3.7 or newer.
- A command prompt or terminal.

To check that Python is installed, run:

```text
python --version
```

## How to use it

Open a terminal in this folder:

```text
cd projects/terminal-habit-tracker
```

### Add a habit

Use the `add` command. Put the habit name in quotes when it contains spaces:

```text
python habit_tracker.py add "Read for 20 minutes"
python habit_tracker.py add "Go for a walk"
```

### See today's status

```text
python habit_tracker.py list
```

Example:

```text
Habits for 2026-09-20:
[ ] Go for a walk
[x] Read for 20 minutes
```

`[x]` means the habit is complete today. `[ ]` means it is still pending.

### Mark a habit complete

```text
python habit_tracker.py done "Read for 20 minutes"
```

The same habit cannot be completed twice on the same day.

### View completion history

```text
python habit_tracker.py history "Read for 20 minutes"
```

### Remove a habit

```text
python habit_tracker.py remove "Go for a walk"
```

Removing a habit deletes its saved history, so use this command carefully.

## Where data is saved

The program creates `.habit_data.json` in this folder:

```text
projects/terminal-habit-tracker/.habit_data.json
```

This file is your local data store. It is intentionally ignored by Git, so
your personal habits are not uploaded to GitHub.

## Run the tests

From the tracker folder, run:

```text
python -m unittest test_habit_tracker.py
```

The tests verify adding and completing a habit, removing a habit, and showing
completion history.

## Complete example

```text
python habit_tracker.py add "Practice Python"
python habit_tracker.py add "Drink water"
python habit_tracker.py list
python habit_tracker.py done "Practice Python"
python habit_tracker.py history "Practice Python"
python habit_tracker.py remove "Drink water"
```

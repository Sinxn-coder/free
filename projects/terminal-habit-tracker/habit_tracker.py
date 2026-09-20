"""A small, dependency-free terminal habit tracker."""

import argparse
import json
from datetime import date
from pathlib import Path


DATA_FILE = Path(__file__).with_name(".habit_data.json")


def load_habits() -> dict:
    if not DATA_FILE.exists():
        return {}

    try:
        with DATA_FILE.open(encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        raise SystemExit(f"Could not read {DATA_FILE}: {error}") from error

    if not isinstance(data, dict):
        raise SystemExit(f"{DATA_FILE} must contain a JSON object.")
    return data


def save_habits(habits: dict) -> None:
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(habits, file, indent=2)
            file.write("\n")
    except OSError as error:
        raise SystemExit(f"Could not save {DATA_FILE}: {error}") from error


def add_habit(habits: dict, name: str) -> None:
    if name in habits:
        raise SystemExit(f"Habit already exists: {name}")

    habits[name] = {"completed_dates": []}
    save_habits(habits)
    print(f"Added: {name}")


def list_habits(habits: dict) -> None:
    if not habits:
        print("No habits yet. Add one with: python habit_tracker.py add \"Read\"")
        return

    today = date.today().isoformat()
    print(f"Habits for {today}:")
    for name, habit in sorted(habits.items()):
        completed = today in habit.get("completed_dates", [])
        marker = "x" if completed else " "
        print(f"[{marker}] {name}")


def show_history(habits: dict, name: str) -> None:
    if name not in habits:
        raise SystemExit(f"Unknown habit: {name}")

    completed_dates = habits[name].get("completed_dates", [])
    if not completed_dates:
        print(f"No completed days yet: {name}")
        return

    print(f"Completed days for {name}:")
    for completed_date in completed_dates:
        print(f"- {completed_date}")


def complete_habit(habits: dict, name: str) -> None:
    if name not in habits:
        raise SystemExit(f"Unknown habit: {name}")

    completed_dates = habits[name].setdefault("completed_dates", [])
    today = date.today().isoformat()
    if today in completed_dates:
        print(f"Already completed today: {name}")
        return

    completed_dates.append(today)
    save_habits(habits)
    print(f"Completed: {name}")


def remove_habit(habits: dict, name: str) -> None:
    if name not in habits:
        raise SystemExit(f"Unknown habit: {name}")

    del habits[name]
    save_habits(habits)
    print(f"Removed: {name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track daily habits from the terminal.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new habit.")
    add_parser.add_argument("name", help="The habit name.")

    subparsers.add_parser("list", help="Show today's habit status.")

    done_parser = subparsers.add_parser("done", help="Mark a habit complete today.")
    done_parser.add_argument("name", help="The habit name.")

    remove_parser = subparsers.add_parser("remove", help="Remove a habit.")
    remove_parser.add_argument("name", help="The habit name.")

    history_parser = subparsers.add_parser("history", help="Show completed days.")
    history_parser.add_argument("name", help="The habit name.")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    habits = load_habits()

    if args.command == "add":
        add_habit(habits, args.name)
    elif args.command == "list":
        list_habits(habits)
    elif args.command == "done":
        complete_habit(habits, args.name)
    elif args.command == "remove":
        remove_habit(habits, args.name)
    elif args.command == "history":
        show_history(habits, args.name)


if __name__ == "__main__":
    main()

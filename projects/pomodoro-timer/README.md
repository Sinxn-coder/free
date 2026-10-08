# Pomodoro Timer

A simple terminal Pomodoro timer written using only the Python standard library.
It runs configurable focus sessions separated by breaks and can be stopped at
any time with **Ctrl-C**.

## Run

```console
python pomodoro_timer.py
python pomodoro_timer.py --focus-minutes 30 --break-minutes 10 --sessions 3
python pomodoro_timer.py --help
```

Each duration and the number of focus sessions must be a positive integer.
There is no break after the final focus session.

## Test

From this directory, run:

```console
python -m unittest -v
```

The session planner and configuration validation are separate from countdown
execution, so the unit tests do not wait for real timer durations.

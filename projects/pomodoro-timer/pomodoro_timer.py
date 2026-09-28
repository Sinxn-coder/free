"""A configurable terminal Pomodoro timer."""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class TimerConfig:
    focus_minutes: int = 25
    break_minutes: int = 5
    sessions: int = 4

    def __post_init__(self) -> None:
        if self.focus_minutes <= 0:
            raise ValueError("focus_minutes must be greater than zero")
        if self.break_minutes <= 0:
            raise ValueError("break_minutes must be greater than zero")
        if self.sessions <= 0:
            raise ValueError("sessions must be greater than zero")


@dataclass(frozen=True)
class TimerSession:
    kind: str
    duration_seconds: int


def plan_sessions(config: TimerConfig) -> tuple[TimerSession, ...]:
    """Plan alternating focus and break sessions, without a trailing break."""
    plan: list[TimerSession] = []
    for index in range(config.sessions):
        plan.append(TimerSession("Focus", config.focus_minutes * 60))
        if index < config.sessions - 1:
            plan.append(TimerSession("Break", config.break_minutes * 60))
    return tuple(plan)


def run_countdown(
    session: TimerSession,
    *,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
    tick_seconds: float = 1.0,
) -> None:
    """Wait for a session duration, printing remaining time once per tick."""
    if tick_seconds <= 0:
        raise ValueError("tick_seconds must be greater than zero")

    deadline = monotonic() + session.duration_seconds
    while True:
        remaining = max(0, int(deadline - monotonic() + 0.999))
        minutes, seconds = divmod(remaining, 60)
        print(f"\r{session.kind}: {minutes:02d}:{seconds:02d}", end="", flush=True)
        if remaining == 0:
            print()
            return
        sleep(min(tick_seconds, remaining))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="A terminal Pomodoro timer. Press Ctrl-C to stop at any time."
    )
    parser.add_argument(
        "--focus-minutes", type=int, default=25, help="focus duration (default: 25)"
    )
    parser.add_argument(
        "--break-minutes", type=int, default=5, help="break duration (default: 5)"
    )
    parser.add_argument(
        "--sessions", type=int, default=4, help="number of focus sessions (default: 4)"
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        config = TimerConfig(
            focus_minutes=args.focus_minutes,
            break_minutes=args.break_minutes,
            sessions=args.sessions,
        )
    except ValueError as error:
        print(f"Invalid timer configuration: {error}")
        return 2

    try:
        for session in plan_sessions(config):
            print(f"\nStarting {session.kind.lower()} for {session.duration_seconds // 60} minute(s).")
            run_countdown(session)
            print(f"{session.kind} complete!")
    except KeyboardInterrupt:
        print("\nTimer stopped.")
        return 130

    print("\nPomodoro complete. Great work!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

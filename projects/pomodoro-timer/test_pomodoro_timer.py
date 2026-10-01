import unittest

from pomodoro_timer import TimerConfig, TimerSession, plan_sessions


class TimerConfigTests(unittest.TestCase):
    def test_default_config(self):
        self.assertEqual(TimerConfig(), TimerConfig(25, 5, 4))

    def test_rejects_non_positive_values(self):
        for values in ((0, 5, 4), (25, 0, 4), (25, 5, 0), (-1, 5, 4)):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    TimerConfig(*values)


class SessionPlanningTests(unittest.TestCase):
    def test_alternates_focus_and_break_without_final_break(self):
        plan = plan_sessions(TimerConfig(focus_minutes=20, break_minutes=3, sessions=3))

        self.assertEqual(
            plan,
            (
                TimerSession("Focus", 1200),
                TimerSession("Break", 180),
                TimerSession("Focus", 1200),
                TimerSession("Break", 180),
                TimerSession("Focus", 1200),
            ),
        )

    def test_single_session_has_no_break(self):
        self.assertEqual(
            plan_sessions(TimerConfig(sessions=1)),
            (TimerSession("Focus", 1500),),
        )


if __name__ == "__main__":
    unittest.main()

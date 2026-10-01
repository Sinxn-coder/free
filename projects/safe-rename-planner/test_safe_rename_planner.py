import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from safe_rename_planner import main, plan_renames


class SafeRenamePlannerTests(unittest.TestCase):
    def test_preview_is_sorted_and_does_not_rename(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            (directory / "z_old.txt").touch()
            (directory / "a_old.txt").touch()

            plan = plan_renames(directory, "old", "new")

            self.assertEqual(
                [rename.source.name for rename in plan.renames],
                ["a_old.txt", "z_old.txt"],
            )
            self.assertTrue((directory / "a_old.txt").exists())
            self.assertFalse((directory / "a_new.txt").exists())

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([str(directory), "old", "new"]), 0)
            self.assertIn("a_old.txt -> a_new.txt", output.getvalue())
            self.assertIn("Dry run", output.getvalue())

    def test_existing_destination_is_reported_as_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            (directory / "report_old.txt").touch()
            (directory / "report_new.txt").touch()

            plan = plan_renames(directory, "old", "new")

            self.assertEqual(len(plan.collisions), 1)
            self.assertIn("destination already exists", plan.collisions[0])
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                self.assertEqual(main([str(directory), "old", "new", "--apply"]), 1)
            self.assertIn("COLLISION:", errors.getvalue())

    def test_apply_renames_only_with_explicit_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "draft_old.txt"
            destination = directory / "draft_new.txt"
            source.write_text("contents", encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(directory), "old", "new"]), 0)
            self.assertTrue(source.exists())
            self.assertFalse(destination.exists())

            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main([str(directory), "old", "new", "--apply"]), 0
                )
            self.assertFalse(source.exists())
            self.assertEqual(destination.read_text(encoding="utf-8"), "contents")

    def test_replacement_cannot_escape_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(ValueError, "path separators"):
                plan_renames(temporary_directory, "old", "../outside")

    def test_recursive_scan_is_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            nested = directory / "nested"
            nested.mkdir()
            (nested / "child_old.txt").touch()

            self.assertEqual(len(plan_renames(directory, "old", "new").renames), 0)
            self.assertEqual(
                len(plan_renames(directory, "old", "new", recursive=True).renames),
                1,
            )


if __name__ == "__main__":
    unittest.main()

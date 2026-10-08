import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from empty_dir_finder import find_empty_directories, main


class FindEmptyDirectoriesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_finds_empty_directories_but_not_nonempty_directories(self) -> None:
        (self.root / "empty").mkdir()
        (self.root / "nonempty").mkdir()
        (self.root / "nonempty" / "file.txt").write_text("content")
        (self.root / "nested").mkdir()
        (self.root / "nested" / "also-empty").mkdir()
        (self.root / "nested" / "with-child").mkdir()
        (self.root / "nested" / "with-child" / "file.txt").touch()

        self.assertEqual(
            find_empty_directories(self.root),
            ["empty", "nested/also-empty"],
        )

    def test_returns_paths_in_deterministic_order(self) -> None:
        for name in ("z-last", "a-first", "middle"):
            (self.root / name).mkdir()

        self.assertEqual(
            find_empty_directories(self.root), ["a-first", "middle", "z-last"]
        )

    def test_depth_limit_counts_levels_below_root(self) -> None:
        (self.root / "level-one").mkdir()
        (self.root / "level-one" / "empty-at-level-two").mkdir()
        (self.root / "level-one" / "level-two").mkdir()
        (self.root / "level-one" / "level-two" / "empty-at-level-three").mkdir()

        self.assertEqual(
            find_empty_directories(self.root, max_depth=1), []
        )
        self.assertEqual(
            find_empty_directories(self.root, max_depth=2),
            ["level-one/empty-at-level-two"],
        )
        self.assertEqual(
            find_empty_directories(self.root, max_depth=3),
            [
                "level-one/empty-at-level-two",
                "level-one/level-two/empty-at-level-three",
            ],
        )
        self.assertEqual(find_empty_directories(self.root, max_depth=0), [])

    def test_empty_root_is_not_reported_as_a_descendant(self) -> None:
        self.assertEqual(find_empty_directories(self.root), [])

    def test_rejects_negative_depth(self) -> None:
        with self.assertRaisesRegex(ValueError, "zero or greater"):
            find_empty_directories(self.root, max_depth=-1)

    def test_does_not_follow_symlink_directories(self) -> None:
        target = self.root / "target"
        target.mkdir()
        (target / "empty-child").mkdir()
        link = self.root / "linked-target"

        try:
            link.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"directory symlinks are unavailable: {error}")

        self.assertEqual(find_empty_directories(self.root), ["target/empty-child"])

    def test_cli_prints_results_and_does_not_mutate_directories(self) -> None:
        (self.root / "empty").mkdir()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = main([str(self.root)])

        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue(), "empty\n")
        self.assertTrue((self.root / "empty").is_dir())

    def test_cli_reports_invalid_root(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stderr(output), self.assertRaises(SystemExit) as error:
            main([str(self.root / "missing")])

        self.assertEqual(error.exception.code, 2)
        self.assertIn("root is not a directory", output.getvalue())

    def test_cli_rejects_negative_depth(self) -> None:
        with mock.patch("sys.stderr", new_callable=io.StringIO) as output:
            with self.assertRaises(SystemExit) as error:
                main([str(self.root), "--max-depth", "-1"])

        self.assertEqual(error.exception.code, 2)
        self.assertIn("must be zero or greater", output.getvalue())


if __name__ == "__main__":
    unittest.main()

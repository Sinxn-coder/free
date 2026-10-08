import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import extension_report


class SummarizeTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self):
        self.tempdir.cleanup()

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def test_groups_files_in_nested_directories(self):
        self.write("a.txt", b"one")
        self.write("nested/b.txt", b"two2")
        self.write("nested/c.py", b"x")

        report = extension_report.summarize(self.root)

        self.assertEqual(report.groups, {".txt": [2, 7], ".py": [1, 1]})
        self.assertEqual(report.scanned, 3)
        self.assertEqual(
            extension_report.format_report(report),
            "Suffix\tFiles\tBytes\n.py\t1\t1\n.txt\t2\t7\nTotal\t3\t8",
        )

    def test_groups_extensionless_files_and_dotfiles_as_empty_suffix(self):
        self.write("README", b"doc")
        self.write(".gitignore", b"ignore")

        report = extension_report.summarize(self.root)

        self.assertEqual(report.groups, {"": [2, 9]})
        self.assertIn("<none>\t2\t9", extension_report.format_report(report))

    def test_file_limit_is_deterministic(self):
        self.write("b.txt", b"bb")
        self.write("a.txt", b"a")
        self.write("c.py", b"ccc")

        report = extension_report.summarize(self.root, max_files=2)

        self.assertEqual(report.groups, {".txt": [2, 3]})
        self.assertTrue(report.limit_reached)
        self.assertIn("File limit reached", extension_report.format_report(report))

    def test_zero_file_limit_scans_nothing(self):
        self.write("a.txt", b"a")

        report = extension_report.summarize(self.root, max_files=0)

        self.assertEqual(report.scanned, 0)
        self.assertEqual(report.groups, {})
        self.assertTrue(report.limit_reached)

    def test_depth_limit_includes_only_root_files_at_zero(self):
        self.write("root.txt", b"root")
        self.write("nested/child.txt", b"child")

        report = extension_report.summarize(self.root, max_depth=0)

        self.assertEqual(report.groups, {".txt": [1, 4]})

    def test_skips_symlinked_files_and_directories(self):
        target_file = self.write("target.txt", b"target")
        target_dir = self.root / "real"
        target_dir.mkdir()
        (target_dir / "inside.py").write_bytes(b"inside")
        try:
            (self.root / "linked.txt").symlink_to(target_file)
            (self.root / "linked-dir").symlink_to(target_dir, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symlinks are unavailable: {exc}")

        report = extension_report.summarize(self.root)

        self.assertEqual(report.groups, {".txt": [1, 6], ".py": [1, 6]})
        self.assertEqual(report.scanned, 2)

    def test_does_not_follow_symlink_root(self):
        target = self.root / "target"
        target.mkdir()
        (target / "inside.txt").write_bytes(b"inside")
        linked_root = self.root / "linked-root"
        try:
            linked_root.symlink_to(target, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symlinks are unavailable: {exc}")

        report = extension_report.summarize(linked_root)

        self.assertEqual(report.groups, {})
        self.assertIn("root directory is a symlink", report.errors[0])

    def test_unreadable_file_is_reported_and_other_files_are_counted(self):
        unreadable = self.write("a.txt", b"secret")
        self.write("b.py", b"ok")
        real_open = open

        def deny_unreadable(path, *args, **kwargs):
            if Path(path) == unreadable:
                raise PermissionError("permission denied")
            return real_open(path, *args, **kwargs)

        with patch("builtins.open", side_effect=deny_unreadable):
            report = extension_report.summarize(self.root)

        self.assertEqual(report.groups, {".py": [1, 2]})
        self.assertEqual(report.scanned, 1)
        self.assertEqual(len(report.errors), 1)
        self.assertIn(str(unreadable), report.errors[0])

    def test_cli_prints_errors_and_returns_failure(self):
        unreadable = self.write("a.txt", b"secret")

        with patch.object(extension_report, "summarize") as summarize:
            summarize.return_value = extension_report.Report(
                errors=[f"{unreadable}: permission denied"]
            )
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = extension_report.main([str(self.root)])

        self.assertEqual(result, 1)
        self.assertIn("Errors\t1", stdout.getvalue())
        self.assertIn("Error:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()

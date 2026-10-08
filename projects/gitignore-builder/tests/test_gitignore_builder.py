import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gitignore_builder


class BuildGitignoreTests(unittest.TestCase):
    def test_template_selection_is_deterministic(self):
        expected = gitignore_builder.build_gitignore(["python", "node"])

        self.assertEqual(
            expected,
            gitignore_builder.build_gitignore(["node", "python"]),
        )
        self.assertLess(expected.index("__pycache__/"), expected.index("node_modules/"))

    def test_existing_and_template_lines_are_deduplicated(self):
        result = gitignore_builder.build_gitignore(
            ["java", "python"],
            "custom-entry\nbuild/\ncustom-entry\n",
        )

        self.assertEqual(result.splitlines().count("custom-entry"), 1)
        self.assertEqual(result.splitlines().count("build/"), 1)
        self.assertEqual(result.splitlines()[0], "custom-entry")


class CommandLineTests(unittest.TestCase):
    def test_default_output_is_stdout(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = gitignore_builder.main(["python"])

        self.assertEqual(status, 0)
        self.assertIn("__pycache__/\n", output.getvalue())

    def test_explicit_output_writes_file_without_stdout(self):
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / ".gitignore"
            with contextlib.redirect_stdout(output):
                status = gitignore_builder.main(["macos", "--output", str(target)])

            self.assertEqual(status, 0)
            self.assertEqual(output.getvalue(), "")
            self.assertIn(".DS_Store\n", target.read_text(encoding="utf-8"))

    def test_existing_file_is_merged_before_output(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            existing = directory / "current.gitignore"
            target = directory / "generated.gitignore"
            existing.write_text("keep-me\nnode_modules/\n", encoding="utf-8")

            gitignore_builder.main(
                ["node", "--existing", str(existing), "--output", str(target)]
            )

            lines = target.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[0], "keep-me")
            self.assertEqual(lines.count("node_modules/"), 1)


if __name__ == "__main__":
    unittest.main()

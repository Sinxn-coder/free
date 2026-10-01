import tempfile
import unittest
from pathlib import Path

from markdown_link_checker import check_markdown_file, main


class MarkdownLinkCheckerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write(self, relative_path, contents=""):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
        return path

    def test_valid_file_and_directory_links_are_accepted(self):
        self.write("docs/guide.md", "[file](../assets/image.png)\n[dir](../assets/)")
        self.write("assets/image.png")
        self.write("assets/child/index.md")
        source = self.root / "docs/guide.md"

        self.assertEqual(check_markdown_file(source, self.root), [])

    def test_missing_target_reports_source_line(self):
        source = self.write(
            "docs/guide.md",
            "# Guide\n\nA valid [link](../present.md).\n[missing](../absent.md)\n",
        )
        self.write("present.md")

        issues = check_markdown_file(source, self.root)

        self.assertEqual([(issue.line, issue.target) for issue in issues], [(4, "../absent.md")])

    def test_url_encoded_path_resolves(self):
        self.write("my page.md")
        source = self.write("index.md", "[encoded](my%20page.md)")

        self.assertEqual(check_markdown_file(source, self.root), [])

    def test_external_anchor_and_mailto_links_are_skipped(self):
        source = self.write(
            "index.md",
            "[web](https://example.com/missing)\n"
            "[anchor](#section)\n"
            "[mail](mailto:hello@example.com)\n",
        )

        self.assertEqual(check_markdown_file(source, self.root), [])

    def test_fenced_code_examples_are_ignored(self):
        source = self.write("index.md", "````markdown\n[example](missing.md)\n````\n")

        self.assertEqual(check_markdown_file(source, self.root), [])

    def test_inline_code_examples_are_ignored(self):
        source = self.write("index.md", "Example: `[not a link](missing.md)`")

        self.assertEqual(check_markdown_file(source, self.root), [])

    def test_reference_definition_is_checked(self):
        source = self.write("index.md", "[guide][missing]\n\n[missing]: absent.md\n")

        issues = check_markdown_file(source, self.root)

        self.assertEqual([(issue.line, issue.target) for issue in issues], [(3, "absent.md")])

    def test_cli_reports_failure_for_missing_target(self):
        self.write("index.md", "[missing](not-here.md)")

        self.assertEqual(main([str(self.root)]), 1)


if __name__ == "__main__":
    unittest.main()

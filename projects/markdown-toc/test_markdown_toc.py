import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from markdown_toc import extract_headings, generate_toc


class ExtractHeadingsTests(unittest.TestCase):
    def test_extracts_all_atx_levels_and_closing_hashes(self):
        markdown = "# One\n ## Two\n### Three ###\n#### Four\n##### Five\n###### Six\n"
        self.assertEqual(
            extract_headings(markdown),
            [(1, "One"), (2, "Two"), (3, "Three"), (4, "Four"), (5, "Five"), (6, "Six")],
        )

    def test_ignores_headings_inside_backtick_and_tilde_fences(self):
        markdown = (
            "```python\n# not a heading\n````\n"
            "# Actual heading\n"
            "~~~~\n## also not a heading\n~~~~~~~\n"
            "## Another heading\n"
        )
        self.assertEqual(
            extract_headings(markdown),
            [(1, "Actual heading"), (2, "Another heading")],
        )

    def test_rejects_invalid_atx_markers(self):
        self.assertEqual(
            extract_headings("#No space\n####### Too many\n    # Indented too far"),
            [],
        )


class GenerateTocTests(unittest.TestCase):
    def test_generates_github_style_slugs_and_heading_indentation(self):
        markdown = (
            "# Hello, World!\n"
            "## **Bold** & `code`\n"
            "### Café &amp; tea\n"
            "#### [Link label](https://example.test/path)\n"
            "##### snake_case\n"
        )
        self.assertEqual(
            generate_toc(markdown),
            "- [Hello, World!](#hello-world)\n"
            "  - [**Bold** & `code`](#bold-code)\n"
            "    - [Café &amp; tea](#café-tea)\n"
            "      - [[Link label](https://example.test/path)](#link-label)\n"
            "        - [snake_case](#snake_case)\n",
        )

    def test_disambiguates_duplicate_headings_and_slug_collisions(self):
        markdown = "# Same\n# Same\n# Same-1\n# Same\n"
        self.assertEqual(
            generate_toc(markdown),
            "- [Same](#same)\n"
            "- [Same](#same-1)\n"
            "- [Same-1](#same-1-1)\n"
            "- [Same](#same-2)\n",
        )

    def test_preserves_empty_output_for_documents_without_headings(self):
        self.assertEqual(generate_toc("Paragraph only.\n"), "")


class CommandLineTests(unittest.TestCase):
    def test_prints_table_of_contents_and_can_write_output_file(self):
        script = Path(__file__).with_name("markdown_toc.py")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.md"
            output = Path(directory) / "toc.md"
            source.write_text("# Command line\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(script), str(source)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.stdout, "- [Command line](#command-line)\n")

            subprocess.run(
                [sys.executable, str(script), str(source), "--output", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(output.read_text(encoding="utf-8"), result.stdout)


if __name__ == "__main__":
    unittest.main()

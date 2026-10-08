import json
import subprocess
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

import a11y_audit


class AuditRuleTests(unittest.TestCase):
    def codes(self, source: str) -> set[str]:
        return {issue.code for issue in a11y_audit.audit_html(source)}

    def test_missing_and_empty_title(self) -> None:
        self.assertIn("A11Y001", self.codes("<html lang='en'></html>"))
        issues = a11y_audit.audit_html("<html lang='en'><title>  </title></html>")
        self.assertIn("A11Y002", {issue.code for issue in issues})

    def test_missing_html_language(self) -> None:
        self.assertIn("A11Y003", self.codes("<html><title>Site</title></html>"))

    def test_image_alt_presence_and_entity_decoding(self) -> None:
        issues = a11y_audit.audit_html(
            "<html lang='en'><title>A &amp; B</title>"
            "<img src='decorative.png' alt=''>"
            "<img src='missing.png'></html>"
        )
        image_issues = [issue for issue in issues if issue.code == "A11Y004"]
        self.assertEqual(len(image_issues), 1)
        self.assertEqual(image_issues[0].message, "Image is missing an alt attribute.")
        self.assertEqual(image_issues[0].line, 1)
        self.assertNotIn(
            "A11Y002",
            {
                issue.code
                for issue in a11y_audit.audit_html(
                    "<html lang='en'><title>A &amp; B</title></html>"
                )
            },
        )

    def test_duplicate_ids(self) -> None:
        issues = a11y_audit.audit_html(
            '<html lang="en"><title>Page</title><p id="same"></p>\n<div id="same"></div></html>'
        )
        duplicate = next(issue for issue in issues if issue.code == "A11Y005")
        self.assertEqual(duplicate.line, 2)
        self.assertIn("first used on line 1", duplicate.message)

    def test_form_control_names(self) -> None:
        source = (
            '<html lang="en"><title>Form</title>'
            '<label for="user">User &amp; account</label><input id="user">'
            '<label>Notes <textarea></textarea></label>'
            '<span id="search-label">Search</span>'
            '<input aria-labelledby="search-label">'
            '<input aria-label="Filter"><input type="hidden">'
            '<select></select><button>Save</button></html>'
        )
        issues = [issue for issue in a11y_audit.audit_html(source) if issue.code == "A11Y006"]
        self.assertEqual(len(issues), 1)
        self.assertIn("<select>", issues[0].message)

    def test_heading_level_skip_and_line(self) -> None:
        issues = a11y_audit.audit_html(
            "<html lang='en'><title>Headings</title>\n<h1>One</h1>\n<h3>Three</h3></html>"
        )
        heading = next(issue for issue in issues if issue.code == "A11Y007")
        self.assertEqual(heading.line, 3)
        self.assertEqual(heading.severity, "warning")


class CliTests(unittest.TestCase):
    def test_directory_scan_is_sorted_and_json_report_is_serializable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "b.html").write_text("<html lang='en'><title>B</title></html>", encoding="utf-8")
            (root / "a.htm").write_text("<html><title>A</title></html>", encoding="utf-8")
            (root / "ignore.txt").write_text("<img>", encoding="utf-8")
            files, errors = a11y_audit.collect_files([str(root)])
            self.assertEqual([path.name for path in files], ["a.htm", "b.html"])
            self.assertEqual(errors, [])

            output = StringIO()
            status = a11y_audit.run([str(root)], "json", stdout=output, stderr=StringIO())
            report = json.loads(output.getvalue())
            self.assertEqual(status, 1)
            self.assertEqual(report["files_scanned"], 2)
            self.assertEqual(report["summary"]["errors"], 1)
            self.assertEqual(report["issues"][0]["code"], "A11Y003")
            self.assertEqual(report["issues"][0]["line"], 1)

    def test_exit_status_for_clean_findings_and_unreadable_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clean = root / "clean.html"
            findings = root / "findings.html"
            clean.write_text(
                '<html lang="en"><title>Okay</title><img alt=""></html>', encoding="utf-8"
            )
            findings.write_text("<img>", encoding="utf-8")
            missing = root / "missing.html"

            clean_result = subprocess.run(
                [sys.executable, str(Path(a11y_audit.__file__)), str(clean)],
                capture_output=True,
                text=True,
                check=False,
            )
            findings_result = subprocess.run(
                [sys.executable, str(Path(a11y_audit.__file__)), str(findings)],
                capture_output=True,
                text=True,
                check=False,
            )
            missing_result = subprocess.run(
                [sys.executable, str(Path(a11y_audit.__file__)), str(missing)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(clean_result.returncode, 0)
            self.assertEqual(findings_result.returncode, 1)
            self.assertEqual(missing_result.returncode, 2)
            self.assertIn("INPUT ERROR", missing_result.stderr)


if __name__ == "__main__":
    unittest.main()

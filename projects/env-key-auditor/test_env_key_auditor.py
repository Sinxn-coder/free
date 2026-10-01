import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("env_key_auditor.py")


class EnvKeyAuditorTests(unittest.TestCase):
    def run_auditor(self, template_contents: str, env_contents: str):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        directory = Path(temporary_directory.name)
        template = directory / ".env.example"
        env_file = directory / ".env"
        template.write_text(template_contents, encoding="utf-8")
        env_file.write_text(env_contents, encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(template), str(env_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result, template, env_file

    def test_reports_missing_and_extra_keys_and_ignores_comments(self):
        result, _, _ = self.run_auditor(
            "# example\n\nAPI_TOKEN=template-secret\nSHARED=value\n",
            "SHARED=local-value\nEXTRA_KEY=extra-secret\n# ignored\n",
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout,
            "Missing keys in .env: API_TOKEN\nExtra keys in .env: EXTRA_KEY\n",
        )
        self.assertEqual(result.stderr, "")
        for secret in ("template-secret", "local-value", "extra-secret"):
            self.assertNotIn(secret, result.stdout + result.stderr)

    def test_supports_export_and_equals_inside_values_without_outputting_values(self):
        result, _, _ = self.run_auditor(
            "export API_TOKEN=template-secret\nPASSWORD=template=password\n",
            "export API_TOKEN=local-secret\nPASSWORD=local=password\n",
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout,
            "Missing keys in .env: (none)\nExtra keys in .env: (none)\n",
        )
        self.assertNotIn("template-secret", result.stdout + result.stderr)
        self.assertNotIn("local-secret", result.stdout + result.stderr)
        self.assertNotIn("template=password", result.stdout + result.stderr)
        self.assertNotIn("local=password", result.stdout + result.stderr)

    def test_does_not_modify_input_files(self):
        template_contents = "TOKEN=template-secret\n"
        env_contents = "TOKEN=local-secret\n"
        result, template, env_file = self.run_auditor(template_contents, env_contents)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(template.read_text(encoding="utf-8"), template_contents)
        self.assertEqual(env_file.read_text(encoding="utf-8"), env_contents)

    def test_invalid_assignment_reports_line_without_leaking_contents(self):
        result, _, _ = self.run_auditor(
            "API_TOKEN=template-secret\n",
            "PASSWORD=private-value\nmalformed-private-value\n",
        )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "env-key-auditor: env: invalid assignment on line 2\n")
        self.assertNotIn("private-value", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

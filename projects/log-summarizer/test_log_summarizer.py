import io
import unittest

from log_summarizer import LEVELS, summarize_lines


class SummarizeLinesTests(unittest.TestCase):
    def test_counts_each_level_once_per_line(self):
        counts = summarize_lines(
            [
                "ERROR: request failed ERROR: retrying\n",
                "WARNING: slow response\n",
                "INFO: started\n",
                "DEBUG: details\n",
                "INFO: ready; DEBUG: enabled\n",
            ]
        )

        self.assertEqual(
            {level: counts[level] for level in LEVELS},
            {"ERROR": 1, "WARNING": 1, "INFO": 2, "DEBUG": 2},
        )

    def test_matches_case_variants_and_streams_error_lines(self):
        errors = io.StringIO()
        counts = summarize_lines(
            ["error: lowercase\n", "ErRoR: mixed case", "warning: delayed response\n"],
            errors,
        )

        self.assertEqual(counts["ERROR"], 2)
        self.assertEqual(errors.getvalue(), "error: lowercase\nErRoR: mixed case\n")


if __name__ == "__main__":
    unittest.main()

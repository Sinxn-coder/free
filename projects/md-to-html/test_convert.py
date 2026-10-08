import unittest

from convert import convert


class ConvertTests(unittest.TestCase):
    def test_converts_headings_and_bold_text(self):
        result = convert("# Title\n\nThis is **important**.")
        self.assertIn("<h1>Title</h1>", result)
        self.assertIn("<strong>important</strong>", result)

    def test_converts_contiguous_unordered_items_to_one_list(self):
        result = convert("- first\n* **second**\n- third")
        self.assertEqual(
            result,
            "<ul><li>first</li><li><strong>second</strong></li>"
            "<li>third</li></ul>\n",
        )

    def test_converts_ordered_items_to_one_list(self):
        result = convert("1. first\n2. second")
        self.assertEqual(
            result,
            "<ol><li>first</li><li>second</li></ol>\n",
        )

    def test_list_content_is_escaped(self):
        result = convert("- <script>alert('x')</script> & **safe**")
        self.assertEqual(
            result,
            "<ul><li>&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt; "
            "&amp; <strong>safe</strong></li></ul>\n",
        )

    def test_lists_close_at_blank_lines_and_block_changes(self):
        result = convert("- first\n\n- second\nParagraph\n1. third\n# Heading")
        self.assertEqual(
            result,
            "<ul><li>first</li></ul>\n"
            "<ul><li>second</li></ul>\n"
            "<p>Paragraph</p>\n"
            "<ol><li>third</li></ol>\n"
            "<h1>Heading</h1>\n",
        )

    def test_preserves_paragraph_whitespace(self):
        self.assertEqual(convert("  keep spaces  "), "<p>  keep spaces  </p>\n")


if __name__ == "__main__":
    unittest.main()

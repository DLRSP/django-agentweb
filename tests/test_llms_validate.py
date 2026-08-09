"""Tests for llms.txt format validation."""

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from agentweb.llms.validate import validate_llms_txt


class ValidateLlmsTxtTestCase(SimpleTestCase):
    def test_valid_document(self):
        body = "# Site\n\n> Summary\n\n## Docs\n- [A](https://ex.com/a)\n"
        self.assertEqual(validate_llms_txt(body), [])

    def test_missing_h1(self):
        errors = validate_llms_txt("> only a quote\n")
        self.assertTrue(any("H1" in e for e in errors))

    def test_rejects_html(self):
        errors = validate_llms_txt("# Site\n\n<script>x</script>\n")
        self.assertTrue(any("HTML" in e for e in errors))


class LlmsValidationHeaderTestCase(TestCase):
    def test_response_marks_valid(self):
        response = self.client.get(reverse("agentweb-llms-txt"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Agentweb-Llms-Valid"], "1")

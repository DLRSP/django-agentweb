"""Tests for the readability (llms.txt) domain."""

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse


class LlmsTxtTestCase(TestCase):
    def test_llms_txt_served_plain_text_with_h1(self):
        response = self.client.get(reverse("agentweb-llms-txt"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        body = response.content.decode()
        self.assertTrue(body.startswith("# Test Site"))
        self.assertIn("> Test site for django-agentweb.", body)

    def test_llms_full_txt_served(self):
        response = self.client.get(reverse("agentweb-llms-full-txt"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("full", response.content.decode().lower())

    def test_exclude_patterns_strip_private_links(self):
        sections = [
            {
                "heading": "Docs",
                "links": [
                    {
                        "title": "Public",
                        "url": "https://example.com/about/",
                        "notes": "ok",
                    },
                    {
                        "title": "Secret",
                        "url": "https://example.com/admin/secret/",
                    },
                ],
            }
        ]
        with override_settings(
            AGENTWEB={
                **self._agentweb_base(),
                "LLMS": {
                    "ENABLED": True,
                    "TITLE": "Test Site",
                    "DESCRIPTION": "desc",
                    "CACHE_TIMEOUT": 0,
                    "SECTIONS": sections,
                    "EXCLUDE_PATTERNS": ["/admin/"],
                },
            }
        ):
            # URLconf was already loaded with ENABLED domains; override only
            # affects conf.get_domain for the view body.
            response = self.client.get(reverse("agentweb-llms-txt"))
        body = response.content.decode()
        self.assertIn("Public", body)
        self.assertIn("https://example.com/about/", body)
        self.assertNotIn("/admin/", body)
        self.assertNotIn("Secret", body)

    def test_i18n_prefixed_llms_txt(self):
        response = self.client.get("/it/llms.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Language"], "it")

    def test_mgmt_command_writes_files(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            call_command("generate_llms_txt", output=tmp)
            self.assertTrue((Path(tmp) / "llms.txt").is_file())
            text = (Path(tmp) / "llms.txt").read_text(encoding="utf-8")
            self.assertTrue(text.startswith("# Test Site"))

    @staticmethod
    def _agentweb_base():
        from agentweb import conf

        return {name: dict(cfg) for name, cfg in conf.get_config().items()}

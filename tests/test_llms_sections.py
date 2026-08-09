"""Unit tests for llms section filtering."""

from django.test import SimpleTestCase

from agentweb.llms.sections import build_sections, filter_sections


class SectionsTestCase(SimpleTestCase):
    def test_filter_drops_excluded_and_empty(self):
        sections = [
            {
                "heading": "A",
                "links": [
                    {"title": "Ok", "url": "https://ex.com/ok"},
                    {"title": "Bad", "url": "https://ex.com/private/x"},
                ],
            },
            {
                "heading": "EmptyAfter",
                "links": [{"title": "P", "url": "/api/x"}],
            },
        ]
        out = filter_sections(sections, ["/private/", "/api/"])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["links"][0]["title"], "Ok")

    def test_build_sections_from_cfg(self):
        cfg = {
            "SECTIONS": [
                {
                    "heading": "Book",
                    "links": [
                        {
                            "title": "Rooms",
                            "url": "https://ex.com/rooms/",
                            "notes": "types",
                        }
                    ],
                }
            ],
            "EXCLUDE_PATTERNS": [],
        }
        out = build_sections(cfg)
        self.assertEqual(out[0]["heading"], "Book")
        self.assertEqual(out[0]["links"][0]["notes"], "types")

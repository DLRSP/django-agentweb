"""Declarative WebMCP template helpers."""

from django.template import Context, Template
from django.test import SimpleTestCase


class DeclarativeWebmcpTestCase(SimpleTestCase):
    def test_form_attrs(self):
        template = Template(
            "{% load agentweb_webmcp_decl %}"
            '<form {% webmcp_form_attrs "search" "Search rooms" %}>'
        )
        rendered = template.render(Context({}))
        self.assertIn('data-mcp-tool-name="search"', rendered)
        self.assertIn('data-mcp-tool-description="Search rooms"', rendered)
        self.assertIn('data-mcp-tool-readonly="true"', rendered)

    def test_form_attrs_escape_hostile_payload(self):
        template = Template(
            "{% load agentweb_webmcp_decl %}"
            "<form {% webmcp_form_attrs name desc %}>"
        )
        rendered = template.render(
            Context(
                {
                    "name": '"><img src=x onerror=alert(1)>',
                    "desc": '"><script>alert(1)</script>',
                }
            )
        )
        self.assertNotIn("<img", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&quot;", rendered)

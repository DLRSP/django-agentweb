"""Tests for the WebMCP domain."""

import json

from django.template import Context, Template
from django.test import TestCase, override_settings
from django.urls import reverse

from agentweb.webmcp import tools


class WebMCPTestCase(TestCase):
    def setUp(self):
        tools.clear()

    def tearDown(self):
        tools.clear()

    def test_manifest_exposes_registered_tool_descriptor(self):
        @tools.register(
            name="check_availability",
            description="Check availability.",
            read_only_hint=True,
            input_schema={"type": "object"},
        )
        def _handler(request, **params):  # pragma: no cover - not called here
            return {"ok": True}

        response = self.client.get(reverse("agentweb-webmcp-manifest"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["protocol"], "webmcp-descriptors")
        names = [t["name"] for t in payload["tools"]]
        self.assertIn("check_availability", names)

    def test_remote_bridge_disabled_by_default(self):
        @tools.register(
            name="echo",
            description="Echo params.",
            read_only_hint=True,
        )
        def _echo(request, **params):
            return params

        url = reverse("agentweb-webmcp-tool", args=["echo"])
        response = self.client.post(
            url, data=json.dumps({"x": 1}), content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("remote bridge disabled", response.json()["error"])

    @override_settings(
        AGENTWEB={
            "LLMS": {"ENABLED": True, "CACHE_TIMEOUT": 0},
            "JSONLD": {"ENABLED": True},
            "DISCOVERY": {"ENABLED": True},
            "WEBMCP": {
                "ENABLED": True,
                "DATA_SOURCE": "proxy",
                "REMOTE_BRIDGE": True,
            },
            "COMMERCE": {"ENABLED": True, "VENDOR": "example-booking-vendor"},
            "SDF": {"ENABLED": True},
        }
    )
    def test_read_only_tool_executes_when_bridge_enabled(self):
        @tools.register(
            name="echo",
            description="Echo params.",
            read_only_hint=True,
            input_schema={"type": "object"},
        )
        def _echo(request, **params):
            return params

        url = reverse("agentweb-webmcp-tool", args=["echo"])
        response = self.client.post(
            url, data=json.dumps({"x": 1}), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], {"x": 1})

    @override_settings(
        AGENTWEB={
            "LLMS": {"ENABLED": True, "CACHE_TIMEOUT": 0},
            "JSONLD": {"ENABLED": True},
            "DISCOVERY": {"ENABLED": True},
            "WEBMCP": {
                "ENABLED": True,
                "DATA_SOURCE": "proxy",
                "REMOTE_BRIDGE": True,
            },
            "COMMERCE": {"ENABLED": True, "VENDOR": "example-booking-vendor"},
            "SDF": {"ENABLED": True},
        }
    )
    def test_state_changing_tool_requires_confirmation(self):
        @tools.register(
            name="book",
            description="Make a booking.",
            read_only_hint=False,
            requires_human_confirmation=True,
        )
        def _book(request, **params):  # pragma: no cover - blocked before call
            return {"booked": True}

        url = reverse("agentweb-webmcp-tool", args=["book"])
        response = self.client.post(
            url, data="{}", content_type="application/json"
        )
        self.assertEqual(response.status_code, 409)
        self.assertTrue(response.json()["requiresHumanConfirmation"])

    def test_unknown_tool_returns_404_when_bridge_on(self):
        with override_settings(
            AGENTWEB={
                "LLMS": {"ENABLED": True, "CACHE_TIMEOUT": 0},
                "JSONLD": {"ENABLED": True},
                "DISCOVERY": {"ENABLED": True},
                "WEBMCP": {
                    "ENABLED": True,
                    "DATA_SOURCE": "proxy",
                    "REMOTE_BRIDGE": True,
                },
                "COMMERCE": {
                    "ENABLED": True,
                    "VENDOR": "example-booking-vendor",
                },
                "SDF": {"ENABLED": True},
            }
        ):
            url = reverse("agentweb-webmcp-tool", args=["nope"])
            response = self.client.post(
                url, data="{}", content_type="application/json"
            )
        self.assertEqual(response.status_code, 404)

    def test_webmcp_register_template_tag_embeds_config(self):
        @tools.register(
            name="ping",
            description="Ping.",
            read_only_hint=True,
        )
        def _ping(request, **params):  # pragma: no cover
            return {"pong": True}

        template = Template("{% load agentweb_webmcp %}{% webmcp_register %}")
        rendered = template.render(Context({}))
        self.assertIn("agentweb-webmcp-config", rendered)
        self.assertIn("ping", rendered)
        self.assertIn("agentweb/webmcp.js", rendered)

"""Tests for the discovery domain."""

from django.test import TestCase
from django.urls import reverse


class DiscoveryTestCase(TestCase):
    def test_agent_descriptor_lists_enabled_capabilities(self):
        response = self.client.get(reverse("agentweb-agent-descriptor"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["untrustedContentHint"])
        self.assertTrue(data["deprecated"])
        self.assertEqual(data["successor"], "/.well-known/ai-catalog.json")
        self.assertIn("llmsTxt", data["capabilities"])
        self.assertIn("webmcp", data["capabilities"])
        self.assertIn("commerce", data["capabilities"])

    def test_ai_catalog_ard_shape_and_cors(self):
        response = self.client.get(reverse("agentweb-ai-catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")
        data = response.json()
        self.assertEqual(data["specVersion"], "1.0")
        self.assertIn("host", data)
        self.assertIn("displayName", data["host"])
        identifiers = [e["identifier"] for e in data["entries"]]
        self.assertTrue(any(":llms:" in i for i in identifiers))
        self.assertTrue(any(":webmcp:" in i for i in identifiers))
        self.assertTrue(any(":commerce:" in i for i in identifiers))
        self.assertTrue(any(":mcp:server-card" in i for i in identifiers))

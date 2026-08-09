"""Core readiness contract tests for agent-web domains.

Covers packaging checks, discovery server-card, JSON-LD profile contracts,
WebMCP safety hints, and CAP Lite Offer typing.
"""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management import call_command
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from agentweb.commerce import build_cap_lite_product
from agentweb.jsonld import builders, profiles
from agentweb.webmcp import tools


class PackagingChecksTestCase(TestCase):
    """Modelless package: Django system check and no pending migrations."""

    def test_django_check_passes(self):
        call_command("check")

    def test_no_agentweb_migration_modules(self):
        package_root = Path(__file__).resolve().parents[1] / "src" / "agentweb"
        migrations_dir = package_root / "migrations"
        self.assertFalse(
            migrations_dir.exists(),
            "agentweb must stay modelless (no migrations package)",
        )
        call_command(
            "makemigrations",
            "agentweb",
            check=True,
            dry_run=True,
            verbosity=0,
        )


class McpServerCardTestCase(TestCase):
    def test_server_card_shape_and_catalog_link(self):
        response = self.client.get(reverse("agentweb-mcp-server-card"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("mcp-server-card", response["Content-Type"])
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")
        data = response.json()
        self.assertEqual(
            data["$schema"],
            "https://static.modelcontextprotocol.io/schemas/v1/"
            "server-card.schema.json",
        )
        self.assertEqual(data["name"], "io.github.dlrsp/agentweb")
        self.assertIn("version", data)
        self.assertTrue(1 <= len(data["description"]) <= 100)
        self.assertNotIn("remotes", data)
        meta = data["_meta"]["io.github.dlrsp/agentweb"]
        self.assertEqual(meta["protocol"], "webmcp-browser")
        self.assertFalse(meta["remoteBridge"])
        self.assertIn("webmcp", meta["manifestUrl"])

        catalog = self.client.get(reverse("agentweb-ai-catalog")).json()
        identifiers = [e["identifier"] for e in catalog["entries"]]
        self.assertTrue(any(":mcp:server-card" in i for i in identifiers))


class JsonLdCoreContractsTestCase(SimpleTestCase):
    def test_sitewide_stable_ids_across_pages(self):
        ctx_home = {
            "site_url": "https://ex.com/",
            "organization_name": "Acme",
            "site_name": "Acme Site",
            "page_name": "Home",
            "page_url": "https://ex.com/",
        }
        ctx_about = {
            **ctx_home,
            "page_name": "About",
            "page_url": "https://ex.com/about/",
        }
        home = profiles.resolve_profiles(["sitewide"], ctx_home)
        about = profiles.resolve_profiles(["sitewide"], ctx_about)
        org_home = next(n for n in home if n["@type"] == "Organization")
        org_about = next(n for n in about if n["@type"] == "Organization")
        web_home = next(n for n in home if n["@type"] == "WebSite")
        web_about = next(n for n in about if n["@type"] == "WebSite")
        self.assertEqual(org_home["@id"], org_about["@id"])
        self.assertEqual(web_home["@id"], web_about["@id"])

    def test_local_business_default_type(self):
        nodes = profiles.resolve_profiles(
            ["local_business"],
            {
                "business_name": "Canal Works",
                "business_type": "LocalBusiness",
            },
        )
        self.assertEqual(nodes[0]["@type"], "LocalBusiness")

    def test_lodging_room_offer_and_unit_price_specification(self):
        nodes = profiles.resolve_profiles(
            ["lodging_room"],
            {
                "room_name": "Double",
                "price": 90,
                "currency": "EUR",
                "unit_code": "DAY",
            },
        )
        room = nodes[0]
        offer = room["offers"]
        if isinstance(offer, list):
            offer = offer[0]
        self.assertEqual(offer["@type"], "Offer")
        self.assertEqual(offer["price"], 90)
        spec = offer["priceSpecification"]
        self.assertEqual(spec["@type"], "UnitPriceSpecification")
        self.assertEqual(spec["unitCode"], "DAY")
        self.assertEqual(
            builders.build_offer(
                price=1,
                currency="EUR",
                price_specification=builders.build_price_specification(
                    1, "EUR", unit_code="DAY"
                ),
            )["priceSpecification"]["@type"],
            "UnitPriceSpecification",
        )


class CapLiteOfferTypeTestCase(SimpleTestCase):
    def test_product_offer_typed(self):
        product = build_cap_lite_product(
            name="Room night", price=100, currency="EUR"
        )
        self.assertEqual(product["@context"], "https://schema.org")
        self.assertEqual(product["offers"]["@type"], "Offer")


class WebMcpHintsTestCase(TestCase):
    def setUp(self):
        tools.clear()

    def tearDown(self):
        tools.clear()

    def test_manifest_and_register_embed_safety_hints(self):
        @tools.register(
            name="check_availability",
            description="Check availability.",
            read_only_hint=True,
            exposed_to="agents",
            untrusted_content_hint=True,
            input_schema={"type": "object"},
        )
        def _handler(request, **params):  # pragma: no cover
            return {"ok": True}

        payload = self.client.get(reverse("agentweb-webmcp-manifest")).json()
        tool = next(
            t for t in payload["tools"] if t["name"] == "check_availability"
        )
        self.assertTrue(tool["readOnlyHint"])
        self.assertEqual(tool["exposedTo"], "agents")
        self.assertTrue(tool["untrustedContentHint"])

        rendered = Template(
            "{% load agentweb_webmcp %}{% webmcp_register %}"
        ).render(Context({}))
        config_start = rendered.find(">") + 1
        config_end = rendered.find("</script>")
        config = json.loads(rendered[config_start:config_end])
        embedded = config["tools"][0]
        self.assertTrue(embedded["readOnlyHint"])
        self.assertEqual(embedded["exposedTo"], "agents")
        self.assertTrue(embedded["untrustedContentHint"])

    def test_webmcp_js_feature_detects_register_tool(self):
        js_path = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "agentweb"
            / "static"
            / "agentweb"
            / "webmcp.js"
        )
        source = js_path.read_text(encoding="utf-8")
        self.assertIn('typeof ctx.registerTool !== "function"', source)
        self.assertIn("readOnlyHint:", source)
        self.assertIn("exposedTo:", source)
        self.assertIn("untrustedContentHint:", source)

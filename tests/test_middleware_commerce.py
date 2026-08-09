"""Tests for discovery middleware + CAP Lite commerce helpers."""

from django.test import TestCase
from django.urls import reverse

from agentweb.commerce import build_cap_lite_catalog, build_cap_lite_product


class DiscoveryMiddlewareTestCase(TestCase):
    def test_link_and_permissions_policy_headers(self):
        response = self.client.get(reverse("agentweb-llms-txt"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("ai-catalog", response["Link"])
        self.assertIn("tools=(self)", response["Permissions-Policy"])
        self.assertEqual(response["X-Agentweb-Discovery"], "1")


class CapLiteTestCase(TestCase):
    def test_product_offer(self):
        product = build_cap_lite_product(
            name="Room night", price=100, currency="EUR"
        )
        self.assertEqual(product["@type"], "Product")
        self.assertEqual(product["offers"]["price"], 100)

    def test_catalog_graph(self):
        doc = build_cap_lite_catalog(
            [
                {"name": "A", "price": 10},
                {"name": "B", "price": 20, "currency": "EUR"},
            ]
        )
        self.assertEqual(len(doc["@graph"]), 2)
